import logging
import requests

from flask_api import FlaskAPI, request
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

app = FlaskAPI(__name__)

#TODO use breadcrumb

class ProgrammeTv:
    """programmetv.net
    crawler class
    """


    def __init__(self):
        self.url = "http://www.programme-tv.net/programme/programme-tnt.html"
    
    def __get_content(self):
        logger.info('Get content from %s' % self.url)
        try:
            result = requests.get(self.url)
            result.raise_for_status()
            return result.content
        except requests.exception.HTTPError:
            logger.error('%s on %s' % (result.status_code, self.url))
        except Exception as e:
            logger.error('%r' % e)

    def __get_channel_name(self, channel):
        """Get channel name form channel parts of the site
        """

        link_name = channel.find('a').text

        return link_name.strip().replace('Programme', '')


    def __get_show_name(self, content):
        """Get prime name
        """
        show_name = content.find('div', class_='p-r w-100 mb-xs').find('a')
        return show_name.text.strip()

    def __get_show_start(self, content):
        show_start = content.find('div', class_='prog_heure d-tc w-25 fw-700')
        return show_start.text.strip()

    def __get_show_rating(self, content):
        star_checked = len(content.find_all('span', class_="icon-star c-red"))
        all_start = len(content.find_all('span', class_="icon-star"))

        return '%s/%s' % (star_checked, all_start)

    def __get_show_type(self, content):
        """Get show type
        """

        prog_type = content.find_all('span', class_='prog_type')[0]
        return prog_type.text

    def __get_show_length(self, content):
        length = content.find_all('span', class_='date')[0]
        return length.text


    def __extract_shows(self, content):
        """Use BS4 to extract show from html page

        Struct
        ======
        * line
            * div ==> channel
            * div ==> Prime time
            * div ==> night show
        """

        bs = BeautifulSoup(content, "html.parser")
        shows = []
        lines = bs.find_all('div', class_='clearfix p-v-md bgc-white bb-grey-3')
        for line in lines:
            channel, prime_time, late_show = line.find_all('div', recursive=False)
            channel_name = self.__get_channel_name(channel)
            show_name = self.__get_show_name(prime_time)
            show_start = self.__get_show_start(prime_time)
            rating  = self.__get_show_rating(prime_time)
            prog_type = self.__get_show_type(prime_time)
            length = self.__get_show_length(prime_time)

            shows.append({
                'name': show_name,
                'channel': channel_name,
                'start': show_start,
                'rating': rating,
                'type': prog_type,
                'length': length
            })
        
        return shows

    def get_shows(self):
        content = self.__get_content()
        shows = self.__extract_shows(content)
        return shows
        


@app.route('/tonight', methods=['GET'])
def tv_schedule():
    """List all tv show in prime time
    from All tnt channel
    """
    logger.info('Incoming request %r' % request)
    

    ptv = ProgrammeTv()
    tv_shows = ptv.get_shows()
    
    logger.info('Returning %s' % tv_shows)
    return tv_shows

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
