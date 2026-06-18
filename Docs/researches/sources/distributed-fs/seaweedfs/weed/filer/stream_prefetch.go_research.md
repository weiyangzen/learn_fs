# sources/distributed-fs/seaweedfs/weed/filer/stream_prefetch.go

## Purpose

`stream_prefetch.go` implements concurrent chunk prefetch streaming using `io.Pipe` to overlap network fetches while preserving response order. It was read as a complete 274-line file.

## Important APIs, Types, and Functions

`chunkPipeResult` tracks one prefetched chunk, its pipe reader, fetch error, bytes written, completion channel, and URL snapshot. `streamChunksPrefetched` is the main pipeline. `retryWithCacheInvalidation` mirrors sequential retry behavior for failed zero-byte fetches.

## Control Flow

The function creates a local cancellable context, a bounded result channel, and a semaphore sized by `prefetchAhead`. A producer walks chunk views in file order, starts fetch goroutines that stream into pipe writers, and sends results in order. The consumer reads each pipe in order, zero-fills gaps, waits for fetch completion, handles retries, updates metrics/throttling, cancels on error, drains remaining pipes, and writes trailing zeroes.

## State and Persistence Behavior

State is transient goroutine, channel, pipe, and pooled copy-buffer state. No data is persisted.

## Dependencies and Integration Points

Depends on `retriedStreamFetchChunkData`, `ChunkView`, `CacheInvalidator`, `urlSlicesEqual`, stats counters, write throttler, and SeaweedFS memory pool.

## Risks and Edge Cases

Deadlock/leak prevention depends on closing pipes, draining results, and waiting on producer/fetch goroutines. Retrying after partial writes is intentionally avoided. `fileId2Url` is read-only during the pipeline.

## Test Signals

`stream_prefetch_test.go` covers ordering, fallback to sequential, cancellation, ranges, oversized prefetch count, and concurrent streams.
