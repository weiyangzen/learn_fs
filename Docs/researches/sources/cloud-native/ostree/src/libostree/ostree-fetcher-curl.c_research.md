# sources/cloud-native/ostree/src/libostree/ostree-fetcher-curl.c

## Purpose
This file implements the internal `OstreeFetcher` backend using libcurl multi/easy APIs integrated with GLib `GMainContext`, supporting HTTP/HTTPS/file fetches to memory or tmpfiles.

## Important APIs, Types, And Functions
`struct OstreeFetcher` stores config flags, remote/proxy/TLS/cookie/header/user-agent settings, tmpdir fd, libcurl multi handle, timer/socket sources, outstanding `GTask`s, socket table, and byte count. `FetcherRequest` tracks mirror list, filename, request/cache headers, size limits, tmpfile/memory buffer, response ETag/Last-Modified, curl easy handle, and write errors. `_ostree_fetcher_new()` constructs the GObject. Setters configure proxy, TLS DB, client cert/key including pkcs11 handling, cookies, extra headers, user agent, low-speed thresholds, retry-all, HTTP2 disable, and outstanding request count. `_ostree_fetcher_request_to_tmpfile()` and `_ostree_fetcher_request_to_membuf()` share `_ostree_fetcher_request_async()`. Finish functions transfer `GLnxTmpfile` or `GBytes`.

## Control Flow, State, And Persistence
Requests bind to one thread-default main context at a time. `initiate_next_curl_request()` creates/configures an easy handle, attaches request headers, auth, protocol restrictions, HTTP2 settings, callbacks, and adds it to the multi handle. `sock_cb()`, `event_cb()`, and `timer_cb()` drive `curl_multi_socket_action()`. `check_multi_info()` handles completions, maps curl/HTTP errors to `G_IO_ERROR`, logs failures, advances to the next mirror when possible, returns memory/tmpfile results, and clears main context when no requests remain. Tmpfiles are created lazily and rewound before transfer.

## Dependencies And Integration Points
It depends on libcurl, GLib Unix sources, libglnx tmpfile/write helpers, fetcher util, date parsing, enumtypes, and repo-private config. Pull and remote code use the common fetcher API without selecting this backend directly.

## Risks And Test Signals
Risks include single-main-context assertions, callback behavior during finalization, max-size enforcement, mirror fallback differences, HTTP2/libcurl version behavior, and security of protocol/TLS options. Tests should cover HTTP 304, ETag/Last-Modified parsing, optional 404 suppression at util level, file URI not found, max-size failure, retry-all mapping, TLS permissive/client cert/proxy/cookie settings, multiple mirrors, bytes-transferred accounting, and cancellation/finalization with outstanding sockets.
