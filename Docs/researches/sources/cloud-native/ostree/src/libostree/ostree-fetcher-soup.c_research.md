# sources/cloud-native/ostree/src/libostree/ostree-fetcher-soup.c

## Purpose
This file implements the internal fetcher backend using libsoup2. It maintains a dedicated session thread and exposes the same async memory/tmpfile request surface as the curl backend.

## Important APIs, Types, And Functions
`ThreadClosure` owns the session thread state: `SoupSession`, main context, remote name, tmpdir fd, extra headers, transfer-gzip flag, outstanding requests, active output stream set, total downloaded bytes, and OOB proxy auth error. `OstreeFetcherPendingURI` stores mirror state, request object, cache validators, output stream/tmpfile/memory state, size limits, and response metadata. Setters enqueue session-thread callbacks for proxy, cookie jar, TLS interaction/database, extra headers, user agent, and max connections. Low-speed and retry-all setters are TODO stubs.

## Control Flow, State, And Persistence
Construction creates a private `GMainContext` and session thread, then initializes a `SoupSession` in that thread. Public request APIs create a `GTask`, attach a pending request, and schedule `session_thread_request_uri()`. That builds a `SoupRequest`, adds conditional headers and extra headers, starts async send, handles HTTP status and mirror fallback in `on_request_sent()`, then reads the stream in 8192-byte chunks through `on_stream_read()` and `on_out_splice_complete()`. Output streams are created lazily and tracked for byte accounting. Finalization stops the thread and joins it.

## Dependencies And Integration Points
It depends on libsoup2 unstable request APIs, GIO Unix streams, libglnx, TLS cert interaction when available, fetcher util, and repo-private helpers. It shares `OstreeFetcher` ABI with the other backends.

## Risks And Test Signals
The private thread model adds synchronization and lifecycle risk; proxy auth OOB errors can override final HTTP errors. Low-speed/retry-all configuration is not implemented here, unlike curl. Tests should cover thread shutdown, proxy credentials, TLS DB initialization errors, cookie jar and headers, mirror fallback, optional content, incomplete downloads via content length, NUL termination, memory/tmpfile transfer, file descriptor usage, and bytes-transferred during active downloads.
