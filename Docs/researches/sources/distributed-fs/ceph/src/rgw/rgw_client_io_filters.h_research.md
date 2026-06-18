# sources/distributed-fs/ceph/src/rgw/rgw_client_io_filters.h

## Purpose
`rgw_client_io_filters.h` implements reusable `RestfulClient` decorators for RGW response and request IO. These filters adapt imperfect caller behavior, add byte accounting, synthesize missing content length headers, emit HTTP chunked transfer framing, and suppress prohibited `Content-Length` headers for selected statuses.

## Important APIs, Types, And Functions
`AccountingFilter<T>` counts bytes sent and received while accounting is enabled. It wraps `send_status()`, `send_100_continue()`, header calls, body sends, body receives, and `complete_request()`, adding returned byte counts to `total_sent` or `total_received`.

`BufferingFilter<T>` buffers response body data in a `ceph::bufferlist` when callers complete headers without declaring a length or chunked transfer. On `complete_request()`, it sends the calculated `Content-Length`, completes the header, then replays buffered body segments.

`ChunkingFilter<T>` turns `send_chunked_transfer_encoding()` into `Transfer-Encoding: chunked` and wraps each `send_body()` payload with hexadecimal size and CRLF delimiters. `complete_request()` writes the terminal `0\r\n\r\n` chunk.

`ConLenControllingFilter<T>` records the status sent and inhibits `send_content_length()` for HTTP 204 and 304 unless `rgw_print_prohibited_content_length` is enabled.

`ReorderingFilter<T>` buffers headers and an early content length until status has been sent and header completion begins. This is a compatibility shim for callers that invoke the REST IO methods in the wrong order.

## Control Flow
Filters are stacked via `RGWRestfulIO::add_filter()`, so each override usually does local state handling and forwards to `DecoratedRestfulClient<T>`. Accounting is passive and depends on wrapped calls returning accurate byte counts. Buffering turns `complete_header()` into a no-op when content length is unknown, then defers header completion until `complete_request()`. Chunking is enabled by a single call and remains active until request completion.

## State And Persistence Behavior
All state is per-request and in memory. Accounting counters survive enable/disable toggles but are not reset by `set_account()`. Buffering stores all deferred body bytes in memory until completion, then clears the buffer and disables buffering. Chunking stores only a boolean. Reordering stores vectors of copied header strings plus an optional content length until `complete_header()`.

## Dependencies And Integration Points
The filters depend on `DecoratedRestfulClient` from `rgw_client_io.h`, `CephContext` logging, `ceph::bufferlist`, `boost::optional`, and global configuration through `g_conf()`. They integrate with the high-level `RGWRestfulIO` chain and therefore affect all REST handlers that emit responses through `req_state::cio`.

## Risks And Edge Cases
`BufferingFilter` can accumulate large responses in memory when no length/chunked marker is provided, so callers should avoid relying on it for large bodies. Its synthetic header bytes are deliberately not counted as body/accounting bytes after it forces `sent = 0`, making byte accounting semantics subtle. `ConLenControllingFilter::send_content_length()` returns `-EINVAL` if status has not been observed, even though the method returns `size_t`; callers expecting exceptions or signed errors must handle this carefully. `ChunkingFilter` does not support chunk extensions or trailers. Reordering can mask caller bugs and may preserve header order differently than direct emission.

## Test Signals
Tests should verify byte counters across enabled/disabled intervals, synthetic content length generation, memory replay of multiple bufferlist segments, chunk framing including the terminal chunk, 204/304 content-length suppression under both config settings, and early header/content-length reordering.
