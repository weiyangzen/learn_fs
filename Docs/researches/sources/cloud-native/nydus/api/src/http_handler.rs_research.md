# sources/cloud-native/nydus/api/src/http_handler.rs

Purpose: provides the Unix-domain HTTP server, route table, common request parsing/response helpers, and channel bridge between HTTP endpoint handlers and the Nydus API service.

Important APIs/types/functions: `HttpResult`, `EndpointHandler`, `HttpRoutes`, `HTTP_ROUTES`, `extract_query_part`, `parse_body`, `translate_status_code`, `success_response`, `error_response`, and `start_http_thread`. `HTTP_ROUTES` is a lazy static map from exact URI paths to boxed endpoint handlers across common, v1, and v2 APIs.

Control flow: `start_http_thread` removes any existing socket path, builds a `dbs_uhttp::HttpServer`, registers the server epoll fd and an exit `Waker` with `mio::Poll`, then spawns `nydus-http-server`. The loop polls for `REQUEST_TOKEN`, drains `server.requests()`, invokes `handle_http_request`, and responds; `EXIT_TOKEN` sends `None` on the API channel and exits. `handle_http_request` parses the absolute path with `http::Uri`, finds the route, calls `EndpointHandler::handle_request`, and converts handler errors to bad requests or missing routes to not found. Successful and error responses are marked with server name and JSON content type.

State and persistence: runtime state is in the route map and mpsc channels. The only filesystem mutation is removing/recreating the Unix socket path. API requests are synchronized through `Sender<Option<ApiRequest>>` and `Receiver<ApiResponse>`.

Dependencies and integration points: integrates `dbs_uhttp`, `mio`, `url`, endpoint modules, and `crate::http` error types. It is exported by `lib.rs` behind the `handler` feature.

Risks: `kick_api_server` blocks waiting for a backend response, so a stalled API receiver stalls HTTP handling. `server.start_server().unwrap()` panics on startup failure inside the spawned thread. Query parsing prepends `http:` to absolute paths to satisfy `Url`. The route table is exact-path based and ignores path parameters.

Test signals: tests assert route registration, channel bridge error behavior, query extraction, thread exit via waker, status-code translation, JSON body parsing, and response constructors.
