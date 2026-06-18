<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/lizardfs-cgiserver.py.in -->
# sources/distributed-fs/lizardfs/src/cgi/lizardfs-cgiserver.py.in

## Purpose
Python 3 asynchronous HTTP/CGI server template installed as `lizardfs-cgiserver`, replacing the deprecated Python 2 `mfscgiserv`.

## Important APIs, Types, and Functions
Defines global `CLIENT_HANDLERS`, `Server`, `ClientHandler`, event `loop`, `HTTP`, `exit_err`, `fork`, `daemonize`, and a main block parsing `-v`, `-h`, `-H`, `-P`, `-R`, `-p`, and `-u`. `HTTP` handles request parsing, static files, `.cgi` execution with `exec(compile(...))`, CGI environment setup, redirects, errors, and logging. `HTTP.StrWritableBytesIO` adapts string writes to bytes for CGI scripts.

## Control Flow, State, and Persistence
Main configures host/port/root, creates the listening server, sets logging/root, optionally daemonizes with a PID file and user drop, then enters a `select` loop. Client handlers read bytes nonblocking, detect `\r\n\r\n`, parse request line/headers, read POST body into `sys.stdin`, build static or CGI responses, and stream bytes/file chunks. Daemon mode double-forks, changes to `/`, resets umask, redirects stdio, optionally switches user/group, and writes a PID file.

## Dependencies and Integration Points
Depends on Python 3 modules `datetime`, `getopt`, `io`, `mimetypes`, `pwd`, `select`, `socket`, `urllib.parse`, and filesystem permissions. It is launched by `lizardfs-cgiserv.service` and serves the generated CGI UI root.

## Risks and Test Signals
Risks include in-process CGI execution with shared interpreter state, global `os.environ`/`sys.stdin`/`sys.stdout` mutation per request, path traversal prevention depending on byte `realpath` prefix checks, malformed headers raising and returning 500/400, keepalive handling tied to explicit `Connection: keep-alive`, daemonization changing user after opening PID file but before forking, no TLS/authentication, and no request/body size limits. Test signals are static/CGI GET/HEAD/POST, traversal attempts, non-executable CGI rejection, malformed headers, large static file streaming, pidfile/user daemonization, systemd foreground mode, KeyboardInterrupt exit, and chart.cgi byte output under the stdout wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/lizardfs-cgiserver.py.in -->
