# sources/cloud-native/ostree/src/libostree/ostree-fetcher-soup3.c

## Purpose
This file implements the fetcher backend using libsoup3. Compared with libsoup2, it avoids a dedicated session thread and instead keeps a `SoupSession` per caller `GMainContext`.

## Important APIs, Types, And Functions
`FetcherRequest` stores mirror/file/message/session/main-context state, output mode, cache validators, response metadata, size counters, and tmpfile/memory streams. `struct OstreeFetcher` stores remote name, tmpdir fd, force-anonymous flag, main-context-to-session hash, proxy resolver, cookie jar, TLS interaction/database, extra headers, user agent, byte count, and max outstanding request setting. Setters configure proxy, cookies, client certs, TLS database, extra headers, user agent, and max connections; low-speed/retry-all remain TODO stubs.

## Control Flow, State, And Persistence
`create_request_message()` creates either a `GFile` for `file://` URIs or a `SoupMessage` for HTTP, attaches conditional headers, TLS permissive acceptance, and extra headers. `_ostree_fetcher_request_async()` selects or creates a session for the current thread-default main context, weakly removes sessions when finalized, creates a `GTask`, and calls `initiate_task_request()`. Completion handles `GFile` or Soup response streams, HTTP 304, mirror fallback, ETag/Last-Modified, content length, then chunked async reading and splicing to tmpfile or memory. Finish functions transfer the tmpfile or bytes.

## Dependencies And Integration Points
It depends on libsoup3, GIO, libglnx, fetcher util, URI helpers, and TLS cert interaction. The common fetcher header lets pull code use this backend interchangeably with curl/libsoup2.

## Risks And Test Signals
Session-per-main-context storage uses a hash with weak refs and shared configuration snapshots; changes after a session is created may not update existing sessions. Low-speed/retry-all are not implemented. Content length is ignored when content encoding is present. Tests should cover file URI handling, session reuse/removal across contexts, TLS permissive acceptance, proxy resolver, cookie jar, extra headers, ETag/Last-Modified parsing via soup date APIs, mirror fallback, max-size errors, incomplete tmpfile detection, and bytes-transferred accounting.
