# sources/distributed-fs/seaweedfs/weed/filer/reader_at.go

## Purpose

`reader_at.go` implements random/sequential `io.ReaderAt` access over SeaweedFS file chunk views. It reconstructs sparse files from visible intervals, zero-fills holes, reads chunk slices from cache or volume servers, uses parallel fetching for multi-chunk sequential reads, and triggers prefetch.

## Important APIs, Types, and Functions

`ChunkReadAt` holds master client, interval-list chunk views, file size, reader cache, read-pattern detector, last chunk file ID, prefetch count, and context. Public methods include `NewChunkReaderAtFromClient`, `Size`, `Close`, `ReadAt`, and `ReadAtWithTime`. `LookupFn` builds a legacy volume lookup function. Internal helpers include `doReadAt`, `readChunkSliceAt`, `readChunkSliceAtForParallel`, `zero`, and `chunkReadTask`.

## Control Flow

`ReadAt` records access pattern, locks the chunk interval list for reading, and delegates to `doReadAt`. `doReadAt` walks visible chunk intervals, records gaps to zero-fill, builds read tasks for overlapping chunk slices, then either reads sequentially for one chunk/random mode or uses an `errgroup` with concurrency bounded by prefetch count and `minReadConcurrency`. It aggregates bytes and max modified timestamp, triggers prefetch for following chunks in sequential mode, zero-fills trailing sparse regions up to file size, and returns `io.EOF` when the requested range reaches or passes file size.

`LookupFn` caches volume lookup responses up to 10,000 volume IDs, prefers same data center URLs, shuffles targets for load spreading, and is marked deprecated in favor of `wdclient.FilerClient`.

## State and Persistence Behavior

Reader state is in-memory: read pattern, last chunk ID, cache contents, and lookup cache. It does not mutate filer metadata or chunk data. Sparse regions are represented by absent chunk intervals and returned as zeroes.

## Dependencies and Integration Points

The file depends on interval lists, `ChunkView`, `ReaderCache`, `ReaderPattern`, volume lookup RPCs, `wdclient`, chunk fetch helpers, and `errgroup`. It integrates with mount, WebDAV, query, and streaming reads that need `ReaderAt` semantics.

## Risks and Edge Cases

Sparse zero-fill must overwrite caller buffers or stale bytes can leak; tests cover this. Parallel reads write into disjoint buffer slices, so task boundaries must be correct. The legacy lookup cache is bounded but has no eviction/TTL and can become stale after volume moves. `ReadAt` returns EOF when the requested end reaches file size, consistent with many ReaderAt users but important for callers to handle.

## Test Signals

Tests should cover gapped chunks, sparse files, EOF boundaries, random versus sequential mode, parallel multi-chunk reads, cache prefetch/un-cache behavior, lookup cache limits, same-DC ordering, and context cancellation propagation.
