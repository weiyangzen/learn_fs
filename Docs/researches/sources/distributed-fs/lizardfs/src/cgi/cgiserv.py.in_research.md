<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/cgiserv.py.in -->
# sources/distributed-fs/lizardfs/src/cgi/cgiserv.py.in

## Purpose
Deprecated Python 2 asynchronous HTTP/CGI server template installed as `mfscgiserv`. It serves static CGI UI files and executes `.cgi` scripts from a configured root, with legacy start/stop/restart/test lockfile management.

## Important APIs, Types, and Functions
Defines global `client_handlers`, `Server`, `ClientHandler`, `HTTP`, event `loop`, lock helpers `mylock` and `wdlock`, and a main block parsing `-H`, `-P`, `-R`, `-D`, `-t`, `-f`, and `-v`. `HTTP` implements request parsing, static response generation, CGI execution with `execfile`, CGI environment setup, redirects, error responses, and logging.

## Control Flow, State, and Persistence
Main prints a deprecation warning, parses options/mode, optionally daemonizes by double-fork with a pipe to the parent, obtains an exclusive lockfile under the data path, starts a nonblocking listening socket, and enters `select` loop. Each accepted client gets a handler that accumulates incoming request bytes, checks header/body completeness, builds a response, and writes chunks until closed or reset for keepalive. Lockfiles persist process PID text; daemon mode redirects stdio to `/dev/null`.

## Dependencies and Integration Points
Depends on Python 2 modules `fcntl`, `posix`, `urlparse`, `urllib`, `cStringIO`, sockets, and filesystem permissions. Generated placeholders include `@CGI_PATH@` and `@DATA_PATH@`. It serves generated `mfs.cgi`, `chart.cgi`, and static UI assets.

## Risks and Test Signals
Risks include Python 2 end-of-life, running CGI via `execfile` in-process with shared globals/environment/stdin/stdout, simplistic HTTP parsing, possible header parsing exceptions on malformed lines, path traversal reliance on `realpath` prefix checks, persistent-connection logic only enabling keepalive on explicit `Connection: keep-alive`, lockfile/PID race behavior, and deprecation drift from the Python 3 server. Test signals are start/stop/test/restart lock behavior, foreground/daemon modes, GET/HEAD/POST static and CGI requests, forbidden traversal, unreadable/non-executable files, malformed requests, and deprecation messaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/cgiserv.py.in -->
