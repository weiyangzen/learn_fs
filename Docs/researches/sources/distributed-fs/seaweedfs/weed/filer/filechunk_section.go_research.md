# sources/distributed-fs/seaweedfs/weed/filer/filechunk_section.go

## Purpose
This file defines `FileChunkSection`, the per-64-MiB section structure used by `ChunkGroup` to track overlapping chunks, compute visible intervals, create chunk views, read data, and locate data/hole boundaries.

## Important APIs, Types, and Functions
- `SectionSize` is 64 MiB and `SectionIndex` identifies section numbers.
- `FileChunkSection` stores section index, raw chunks, visible intervals, chunk views, a `ChunkReadAt`, a lock, and preparation flag.
- `NewFileChunkSection` constructs a section.
- `addChunk` adds a chunk and incrementally updates visibility/views.
- `removeGarbageChunks` removes chunks made obsolete by newer visibility.
- `setupForRead` lazily computes visible intervals, removes garbage chunks, builds chunk views, and creates a reader.
- `readDataAt`, `DataStartOffset`, and `NextStopOffset` serve reads and seek helpers.

## Control Flow and State
Chunks are clipped to section bounds before merging into visible intervals. The first preparation computes visible intervals and chunk views if they do not already exist, creates a `ChunkReadAt` through the group's reader cache, and records the current file size. Later preparations update reader file size. Reads lock for preparation then use the reader under RLock. Seek helpers walk visible intervals to return candidate data or hole offsets.

## State and Persistence Behavior
The section is in-memory derived state from persisted chunk metadata. It may drop garbage chunks from its local list after visibility analysis but does not delete persisted chunks itself.

## Dependencies and Integration Points
It depends on interval-list helpers (`readResolvedChunks`, `MergeIntoVisibles`, `FindGarbageChunks`, `SeparateGarbageChunks`, `ViewFromVisibleIntervals`, `MergeIntoChunkViews`) and `NewChunkReaderAtFromClient`. `ChunkGroup` owns sections and calls these methods.

## Risks and Edge Cases
- Incremental `addChunk` must keep `visibleIntervals`, `chunkViews`, and `chunks` consistent.
- `setupForRead` closes any old reader when garbage separation changes chunks.
- `DataStartOffset` appears to return the requested offset even if the next visible interval starts later; intended seek-data semantics should be verified.
- Locks prevent concurrent mutation/read races within a section, but callers must avoid deadlock with group-level locks.

## Test Signals
No direct tests are listed. Behavior is indirectly exercised by chunk group and manifest tests, but section interval merging, garbage removal, and seek helpers need focused coverage.
