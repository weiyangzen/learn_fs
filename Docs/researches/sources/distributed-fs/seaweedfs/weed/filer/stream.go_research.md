# sources/distributed-fs/seaweedfs/weed/filer/stream.go

## Purpose

`stream.go` streams filer entry content from inline bytes or volume-server chunks, implements sequential chunk streaming, and provides `ChunkStreamReader`. It was read as a complete 532-line file.

## Important APIs, Types, and Functions

Key APIs are `JwtForVolumeServer`, `HasData`, `IsSameData`, `NewFileReader`, `PrepareStreamContentWithThrottler`, `PrepareStreamContentWithPrefetch`, `StreamContent`, `writeZero`, `ChunkStreamReader` constructors, `Read`, `ReadAt`, `Seek`, `Close`, and `VolumeId`. `CacheInvalidator` allows failed chunk reads to invalidate lookup caches.

## Control Flow

Streaming builds `ChunkView` intervals for a requested range, resolves each fileId with retry/backoff, and returns a closure that writes zero-filled gaps and streams chunks with optional throttling. On zero-byte fetch failure it can invalidate cached locations, re-lookup, and retry if locations changed. `ChunkStreamReader` lazily fetches whole chunk views into an internal buffer for read/seek/read-at operations.

## State and Persistence Behavior

State is transient: JWT signing config is loaded once, stream closures hold lookup URL maps, and `ChunkStreamReader` holds current buffer/offset. No metadata persistence occurs.

## Dependencies and Integration Points

Depends on filer protobuf chunks, `wdclient` lookup, security JWT generation, HTTP chunk streaming helpers, stats metrics, throttling utilities, and `ViewFromChunks`.

## Risks and Edge Cases

`IsSameData` sorts chunk slices in place, mutating callers. `ChunkStreamReader.doRead` loops until the caller buffer is full and may return `io.EOF` after partial copy behavior that deserves scrutiny. Retry logic only retries when no bytes were written.

## Test Signals

`stream_prefetch_test.go` and `stream_benchmark_test.go` cover prefetch and sequential benchmarks. Additional tests should cover `ChunkStreamReader` seeks, zero gaps, in-place chunk sorting, and lookup retry failures.
