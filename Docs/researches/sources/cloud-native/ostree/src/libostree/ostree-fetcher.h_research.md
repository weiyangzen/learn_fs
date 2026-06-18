# sources/cloud-native/ostree/src/libostree/ostree-fetcher.h

## Purpose
This private header defines the common `OstreeFetcher` GObject API implemented by curl, libsoup2, and libsoup3 backends, plus the `OstreeFetcherURI` abstraction.

## Important APIs, Types, And Functions
It defines type macros and `OstreeFetcherClass`, `OstreeFetcherConfigFlags` (`TLS_PERMISSIVE`, `TRANSFER_GZIP`, `DISABLE_HTTP2`), and `OstreeFetcherRequestFlags` (`NUL_TERMINATION`, `OPTIONAL_CONTENT`, `LINKABLE`). URI helpers parse/clone/modify/get/validate URIs. Fetcher construction takes a tmpdir fd, remote name, and config flags. Setters cover anonymous tmpfiles, cookie jar, proxy, client cert, low-speed, retry-all, max outstanding requests, TLS database, extra headers, and user agent. Async APIs fetch to tmpfile or memory with cache validators, max size, priority, cancellable, and finish metadata outputs. `_ostree_fetcher_bytes_transferred()` reports progress.

## Control Flow, State, And Persistence
The header defines asynchronous request contracts but no implementation. Tmpfile requests return ownership through `GLnxTmpfile`; memory requests return `GBytes`. Cache validators and response metadata support HTTP conditional fetch persistence in higher layers.

## Dependencies And Integration Points
It depends on libglnx and GLib/GObject/GIO types. Pull, summary, and remote code integrate through this header while the build selects a backend implementation.

## Risks And Test Signals
Backend parity is the biggest risk: some setters are TODO in soup backends while implemented in curl. Tests should run common fetcher behavior against each configured backend, including request flags, output ownership, cancellation, ETag/Last-Modified, TLS/proxy/cookie/header settings, and byte accounting.
