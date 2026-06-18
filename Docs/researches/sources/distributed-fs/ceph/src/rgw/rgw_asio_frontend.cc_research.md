# sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_asio_frontend.cc` implements RGW's Boost.Asio/Beast HTTP frontend behind the public `RGWAsioFrontend` wrapper. It configures TCP and SSL listeners, accepts client sockets, parses HTTP requests, adapts Beast streams into RGW's `ClientIO`/`RGWRestfulIO`, dispatches `process_request()`, logs access records, supports pause/unpause for dynamic config reload, and shuts down listeners/connections. The source was read as a complete 1411-line implementation.

## Important APIs, Types, and Functions

Important local types are `RGWAsioBackoff`, `StreamIO<Stream>`, `Connection`, `ConnectionList`, and private `AsioFrontend`. `StreamIO` implements `write_data()` and `recv_body()` around Beast read/write and timeout handling. `handle_connection()` is the per-connection request loop. `AsioFrontend::init()` parses frontend configuration and starts accept coroutines. SSL builds are centered on `ssl_init()`, `ssl_reload()`, `ssl_reload_timer_start()`, `ssl_set_private_key()`, and `ssl_set_certificate_chain()`. Socket lifecycle is driven by `accept()`, `on_accept()`, `stop()`, `join()`, `pause()`, and `unpause()`. The public `RGWAsioFrontend` methods simply delegate to `Impl`.

## Control Flow

Initialization reads `prefix`, `request_timeout_ms`, `max_header_size`, TCP/SSL ports/endpoints, `tcp_nodelay`, `so_reuseport`, and backlog options. It opens acceptors, applies IPv6-only and reuse options, binds/listens, spawns one accept coroutine per listener, and finally drops privileges. `accept()` loops on `async_accept()`, backs off on resource exhaustion, and hands accepted sockets to `on_accept()`. `on_accept()` spawns a strand-bound coroutine per connection; SSL listeners perform a timed server handshake before entering `handle_connection()`.

`handle_connection()` repeatedly creates a Beast parser, reads headers under `timeout_timer`, obtains a shared pause lock, constructs `RGWRequest`, extracts endpoints, wraps the stream in buffering/chunking/content-length/reordering filters, and calls `process_request()`. It emits an access log entry when enabled, checks `StreamIO` for fatal transport errors, honors keep-alive, and discards unread body bytes before the next request. Bad headers receive a 400 response; reset/abort/end-of-stream exits quietly.

## State and Persistence Behavior

The frontend owns in-memory listener state, an intrusive list of live `Connection` objects, pause/shutdown flags, timeout/header-limit configuration, optional dmClock scheduler, and optional shared SSL context. There is no direct file persistence. SSL material may be loaded from filesystem paths or from RGW config-key storage via `config://`. Runtime SSL reload swaps the shared context atomically where supported and keeps existing connections on their previous context. Pause and graceful stop coordinate outstanding requests with `SharedMutex`.

## Dependencies and Integration Points

The file depends on Boost.Asio, Boost.Beast HTTP parsers, optional OpenSSL, Ceph clocks/logging/config parsing, RGW SAL driver services, zone metadata expansion, `rgw_asio_client`, `rgw_dmclock_async_scheduler`, and `rgw_asio_frontend_timer`. The major integration point is `process_request(env, req, uri_prefix, client, optional_yield, scheduler, ...)`, which connects accepted HTTP traffic to the RGW REST operation stack. ASIO coroutine execution interacts with `rgw_asio_thread` warnings through `is_asio_thread` checks in stop paths and async-yield choices.

## Risks and Edge Cases

Header size is capped by the fixed 64 KiB parse buffer; invalid configured values are warned and defaulted or capped. The `SO_REUSEADDR | SO_REUSEPORT` `setsockopt()` call uses a bitwise OR as the option name, which is platform-sensitive. SSL reload failure keeps the old context but repeated bad config logs periodically. Timeout handlers cancel and shut down sockets asynchronously, so connection lifetime relies on intrusive references. `std::localtime()` in access logging is process-global and may be a concurrency concern. `pause()` cancels accept loops and optionally closes active connections depending on graceful-stop config. Errors after partial request processing can break keep-alive and stop the loop.

## Test Signals

Useful tests include endpoint parsing for IPv4, IPv6 bracket syntax, default ports, bad ports, and oversized header limits; listener bind smoke tests with and without SSL; request timeout tests for header, body, write, and SSL handshake paths; keep-alive tests with unread body discard; graceful pause/unpause tests under active requests; SSL config-key and file loading tests including reload failure retention; resource-limit accept backoff tests; and access-log assertions for method, target, HTTP version, byte counts, TLS metadata, and latency.
