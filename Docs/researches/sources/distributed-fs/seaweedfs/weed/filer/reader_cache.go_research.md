# sources/distributed-fs/seaweedfs/weed/filer/reader_cache.go

## Purpose

`reader_cache.go` implements an in-process chunk reader cache used by filer reads to deduplicate and prefetch volume-server chunk downloads. It was read as a complete 276-line file.

## Important APIs, Types, and Functions

`ReaderCache` owns a `chunk_cache.ChunkCache`, a `LookupFileIdFunctionType`, a bounded `downloaders` map, and a limit. `SingleChunkCacher` owns one fileId download, its pooled buffer, completion/error state, `done` signal, and wait group. Main APIs are `NewReaderCache`, `MaybeCache`, `ReadChunkAt`, `UnCache`, `destroy`, `startCaching`, and `readChunkAt`.

## Control Flow

`MaybeCache` walks future `ChunkView` intervals, skips existing/in-cache chunks, creates a `SingleChunkCacher`, starts it in a goroutine, waits only until the goroutine has begun, and records it. `ReadChunkAt` first waits on an existing cacher, falls back to the persistent chunk cache, evicts the oldest completed cacher when at capacity, then starts one shared download.

## State and Persistence Behavior

Downloaded data is held in memory allocated through `mem.Allocate`; optional persistence into `chunkCache.SetChunk` happens only when `shouldCache` is true. Completion time is stored atomically for eviction. `destroy` waits for active readers before freeing memory.

## Dependencies and Integration Points

It integrates with `ChunkView`/interval reader logic, `wdclient` fileId lookup, `util_http.RetriedFetchChunkData`, SeaweedFS chunk cache, and pooled memory. The shared download intentionally uses `context.Background()` so one request cancellation does not abort other readers waiting for the same chunk.

## Risks and Edge Cases

Risk concentrates around lock ordering, `done` always closing, memory frees after concurrent reads, and the `n=0, err=nil` path that must fall back to `chunkCache`. A lookup/download failure is shared by all waiters. Eviction only removes completed downloaders, so a full map of active downloads can temporarily block new prefetches.

## Test Signals

Covered by `reader_cache_test.go`: cancellation while waiting, fallback cache reads, partial offsets, downloader cleanup, lookup errors, in-flight deduplication, and one cancelled reader not cancelling the shared download for others.
