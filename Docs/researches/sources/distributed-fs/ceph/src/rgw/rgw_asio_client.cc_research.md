# sources/distributed-fs/ceph/src/rgw/rgw_asio_client.cc

## Purpose
Implements the Boost.Beast/ASIO `ClientIO` adapter that converts parsed HTTP requests into RGW environment variables and writes HTTP responses through RGW's buffered client IO interface.

## Important APIs, Types, and Functions
- `ClientIO::init_env()` populates `RGWEnv` from Beast request headers, HTTP version, method, target/query, local port, SSL flag, and remote address.
- `complete_request()` updates RGW queue counters.
- `send_status()`, `send_100_continue()`, `send_header()`, `send_content_length()`, and `complete_header()` generate HTTP/1.1 response bytes.
- `dump_date_header()` formats the Date header.

## Control Flow
Construction snapshots keepalive and `Expect: 100-continue` state from the parser. `init_env()` maps `Content-Length`/`Content-Type` to CGI-style names and other headers to `HTTP_...` uppercase dash-transformed variables, then splits target into `SCRIPT_URI` and `QUERY_STRING`. Response methods write into `txbuf` and flush at key boundaries. If a request expected `100-continue` but final status is sent before `100 Continue`, keepalive is disabled to avoid body bytes being misinterpreted as the next request.

## State and Persistence
Runtime state includes the parser reference, local/remote endpoints, `RGWEnv`, output buffer, and keepalive/continue flags. No durable state is persisted.

## Dependencies and Integration Points
Depends on Boost.Beast HTTP parser, Boost.Asio endpoints, RGW `RestfulClient`/`BuffererSink`, output buffering, and RGW perf counters. Used by the beast frontend request path.

## Risks and Edge Cases
The adapter emits raw HTTP/1.1 bytes and relies on callers to avoid header injection in names/values. It preserves the raw request target for `REQUEST_URI` and only simple-splits on `?`. Keepalive handling for early final responses to `Expect: 100-continue` is subtle and important for protocol correctness.

## Test Signals
Tests should cover header environment mapping, query splitting, SSL/server port flags, keepalive/close response headers, early status with `Expect: 100-continue`, date header presence, content length formatting, and perf counter increments/decrements.
