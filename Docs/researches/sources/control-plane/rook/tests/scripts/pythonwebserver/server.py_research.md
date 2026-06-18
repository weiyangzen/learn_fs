<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/pythonwebserver/server.py -->
# sources/control-plane/rook/tests/scripts/pythonwebserver/server.py

Purpose: tiny HTTP server for tests that need an endpoint receiving and logging POST bodies.

Important APIs and control flow: class `S` extends `BaseHTTPRequestHandler`; `_set_response` would send a 200 HTML response but is not called by `do_POST`. `do_POST` reads `Content-Length` bytes and logs the decoded body. `run` starts an `HTTPServer` on all interfaces and a requested or default port 8080, handling KeyboardInterrupt for shutdown.

State, persistence, and integration: it does not persist request bodies except to process logs. Dependencies are Python standard library HTTP server and logging modules. Risks include `do_POST` not sending a response, missing/invalid `Content-Length` handling, no GET handler, and single-threaded serving. Test signals are log lines showing received POST body and process availability.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/pythonwebserver/server.py -->
