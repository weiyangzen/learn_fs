# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/StreamsRestServiceHandler.java

## Purpose
`StreamsRestServiceHandler` exposes data operations for streams previously opened through the proxy path API. It lets clients read, write, and close cached stream IDs under `/streams`.

## Important APIs, Types, and Functions
Endpoints are `POST /streams/{id}/close`, `POST /streams/{id}/read`, and `POST /streams/{id}/write`. The handler uses `StreamCache.invalidate`, `getInStream`, `getOutStream`, and Guava `ByteStreams.copy`.

## Control Flow, State, and Persistence
The constructor retrieves `StreamCache` from the servlet context. `close` invalidates the stream ID, relying on the cache removal listener to close the underlying stream, and throws if no stream exists. `read` returns the cached `FileInStream` as an octet-stream response. `write` copies the request body into the cached `FileOutStream` and returns the byte count. Filesystem persistence occurs through the underlying stream writes and close semantics.

## Dependencies and Integration Points
This handler pairs with `PathsRestServiceHandler.createFile` and `openFile`, which create stream IDs. It integrates Jersey media types, `RestUtils`, `StreamCache`, and Alluxio file stream classes.

## Risks
There is no range-read support and write copies the entire request body in one call. Invalid or expired IDs produce an `IllegalArgumentException` through `RestUtils`. Clients must close output streams to commit/flush according to Alluxio stream semantics.

## Test Signals
Signals should cover successful read/write/close flows, invalid IDs, expired streams, close idempotency expectations, and byte-count reporting for writes.
