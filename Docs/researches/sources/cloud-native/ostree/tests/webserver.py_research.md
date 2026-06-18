# sources/cloud-native/ostree/tests/webserver.py

## Purpose
This Python helper daemonizes a simple threaded HTTP server on an automatically selected port and writes the port number to a file for tests.

## Important APIs, Types, And Functions
It uses `http.server.SimpleHTTPRequestHandler`, `ThreadingHTTPServer`, `socket.getaddrinfo`, `os.fork`, `os.setsid`, `os.rename`, `threading.Thread`, and `argparse`. Functions are `_get_best_family()`, `run()`, and `main()`.

## Control Flow
`main()` double-forks to daemonize, starts a daemon watcher thread that exits if the original working directory is deleted, parses a single `port_path` argument, and calls `run()`. `run()` selects address family, sets protocol version to HTTP/1.1, starts the server on the requested or random port, writes the chosen port atomically via `port_path.tmp` then rename, prints the port, and serves forever until keyboard interrupt.

## State And Persistence
The helper writes the port file and serves files from its current working directory. It holds an HTTP server socket and exits when the served directory disappears.

## Dependencies And Integration Points
This is used by shell tests needing an HTTP remote without the richer OSTree expected-header/cookie server. It integrates with test harness process cleanup through working-directory deletion.

## Risks
Double-forking can make failures harder to observe. The watcher calls `sys.exit()` from a thread, which exits that thread rather than forcibly terminating the process in standard Python semantics, so cleanup depends on surrounding harness behavior. Atomic port-file write is important to avoid races.

## Test Signals
There are no direct tests in this file. Consumers wait for the port file and then perform HTTP requests against the served directory.
