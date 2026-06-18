# sources/distributed-fs/seaweedfs/weed/filer/stream_prefetch_test.go

## Purpose

`stream_prefetch_test.go` validates pipe-based prefetch streaming behavior with mock volume servers. It was read as a complete 365-line file.

## Important APIs, Types, and Functions

Helpers include `testMasterClient`, `noopJwt`, `createTestServer`, and `makeChunksAndServer`. Tests cover in-order delivery, single chunk, fallback to sequential for `prefetchAhead <= 1`, context cancellation, range requests, prefetch count larger than chunk count, and concurrent downloads.

## Control Flow

Tests create random chunk data, serve it over `httptest.Server` with range support, map fileIds to URLs, call `PrepareStreamContentWithPrefetch`, execute the returned stream closure, and compare byte slices or sizes.

## State and Persistence Behavior

State is in-memory chunk maps, URL maps, and request counters. No filer store or volume server persistence is used.

## Dependencies and Integration Points

Depends on streaming APIs, `filer_pb.FileChunk`, `wdclient.LookupFileIdFunctionType`, `httptest`, and Go concurrency primitives.

## Risks and Edge Cases

The cancellation test accepts prepare-time cancellation as expected and logs if all chunks were requested, so it is a softer leak/backpressure signal. Failure retry paths are only indirectly represented by the mock invalidator.

## Test Signals

Strong functional signal for ordering, range correctness, and concurrent use. Additional tests should force fetch failure and URL cache invalidation success/failure.
