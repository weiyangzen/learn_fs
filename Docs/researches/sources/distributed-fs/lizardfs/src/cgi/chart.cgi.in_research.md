<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/chart.cgi.in -->
# sources/distributed-fs/lizardfs/src/cgi/chart.cgi.in

## Purpose
CGI proxy that requests chart data from a LizardFS backend service and returns image or timestamp payloads to the web UI.

## Important APIs, Types, and Functions
Defines substituted `PROTO_BASE`, packet command constants `CUTOAN_CHART` and `ANTOCU_CHART`, parsed CGI fields `host`, `port`, and `id`, helpers `mysend`, `myrecv`, and `handle_error`.

## Control Flow, State, and Persistence
The script validates host, port, and chart ID; on invalid input or any exception it returns `err.gif` from `DOCUMENT_ROOT`. On success it opens a socket to the requested host/port, sends a big-endian packet header with chart ID, reads response header and payload, and emits `Content-Type` based on GIF, PNG, or `timestamp` prefix. No state is persisted.

## Dependencies and Integration Points
Depends on Python 3 `cgi`, sockets, `struct`, `DOCUMENT_ROOT`, and the LizardFS chart protocol. It is executed by the CGI server and consumed by the web UI.

## Risks and Test Signals
Risks include user-controlled host/port enabling server-side request forgery from the CGI server, blocking socket operations without explicit timeout, `sys.stdout.write(bytes)` on a text stdout in Python 3 unless the CGI server's stdout wrapper accepts bytes, deprecated `cgi` module, and returning a generic error image for all failures. Test signals are valid GIF/PNG/timestamp responses, invalid parameters, backend timeout/refusal, unexpected command/length, malformed image data, missing `err.gif`, and execution under both installed CGI server wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/chart.cgi.in -->
