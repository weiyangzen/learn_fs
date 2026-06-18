# sources/distributed-fs/seaweedfs/weed/filer/filechunk_group.go

## Purpose
This file implements `ChunkGroup`, the read-side structure that organizes file chunks into fixed-size sections, resolves chunk manifests, supports zero-fill holes, parallel section reads, read-ahead tuning, and seek-data/seek-hole style queries.

## Important APIs, Types, and Functions
- `ChunkGroup` stores a volume lookup function, section map, section lock, `ReaderCache`, and concurrency setting.
- `NewChunkGroup` caps/defaults concurrency, creates a reader cache, and calls `SetChunks`.
- `GetPrefetchCount` derives read-ahead count from concurrency.
- `AddChunk` incrementally adds a chunk to affected sections.
- `ReadDataAt`, `readDataAtSequential`, and `readDataAtParallel` read file data into a buffer.
- `sectionReadResult` aggregates parallel read results.
- `SetChunks` resolves manifest chunks and rebuilds the section map.
- `SearchChunks` and `doSearchChunks` implement data/hole search using section visibility.

## Control Flow and State
Chunks are mapped to all 64 MiB sections they overlap. Reads reject offsets at or beyond file size with `io.EOF`, then select sequential or parallel mode based on section count and concurrency. Missing sections are zero-filled up to file size. Existing sections delegate to `FileChunkSection.readDataAt`, returning bytes read, max modified timestamp, and errors. Parallel reads use `errgroup` with a limit, write to disjoint buffer slices, and aggregate results after all goroutines finish. `SetChunks` resolves manifest chunks before building fresh sections.

## State and Persistence Behavior
`ChunkGroup` is in-memory. It reads persisted chunk metadata from `filer_pb.FileChunk` entries and fetches actual chunk data via volume-server lookup/read functions.

## Dependencies and Integration Points
It integrates with `FileChunkSection`, chunk manifest resolution, `ReaderCache`, `chunk_cache.ChunkCache`, volume lookup via `wdclient`, and file metadata from protobuf chunks.

## Risks and Edge Cases
- Parallel result writes rely on each goroutine owning a disjoint buffer slice and result index.
- `errgroup` cancels context on first non-EOF error, which can reduce later read results.
- Missing sections zero-fill, so sparse-file semantics depend on file size boundaries.
- `DataStartOffset` currently returns the offset even when it is before visible data, which should be checked against intended `SEEK_DATA` behavior.
- Manifest resolution in `SetChunks` uses `context.Background`, so construction is not caller-cancellable.

## Test Signals
`filechunk_group_test.go` covers empty group reads, EOF behavior, error-masking regression intent, and context propagation smoke tests. It has a placeholder table for `doSearchChunks`, so seek behavior lacks substantive tests.
