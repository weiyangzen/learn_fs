<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks.go

## Purpose
Implements core file chunk accounting and visibility logic. Filer entries store file data as ordered `filer_pb.FileChunk` metadata; this file determines logical file size, ETags, visible intervals after overwrites, read views, compaction candidates, and chunk deltas.

## Important APIs and Types
`TotalSize`, `FileSize`, `ETag`, `ETagEntry`, and `ETagChunks` derive entry metadata from chunk and remote-entry state. `CompactFileChunks`, `SeparateGarbageChunks`, and `FindGarbageChunks` classify current versus garbage chunk IDs. `MinusChunks`, `DoMinusChunks`, and `DoMinusChunksBySourceFileId` compute deletion deltas, including sync cases where a destination chunk records its source file ID. `ChunkView` represents a client-visible slice of a chunk. `VisibleInterval` represents the newest visible owner of a logical file byte range.

## Control Flow and State
`FileSize` uses the max of stored attributes, remote metadata when newer, and chunk extent. `CompactFileChunks` resolves manifests, computes non-overlapping visible intervals, then keeps chunks whose file IDs are present in those intervals. `ViewFromChunks` resolves visible intervals for a requested offset and size, then projects them into `ChunkView` values with `OffsetInChunk`, `ViewOffset`, and `ViewSize`.

## Persistence Behavior
This file does not persist data. It computes metadata used by readers and by deletion code that later enqueues volume file IDs. Manifest resolution can involve lookups through `wdclient.LookupFileIdFunctionType`.

## Dependencies and Integration Points
Uses `filer_pb.FileChunk`, interval-list helpers from the filer package, manifest resolution helpers, `util` MD5 helpers, and `wdclient` lookup callbacks. It feeds read streaming, entry updates, metadata notifications, and delete cleanup.

## Risks
Correctness depends on timestamp ordering: newer `ModifiedTsNs` wins overlapping ranges. Tie handling and manifest resolution failures can affect compaction and deletion safety. `ETagChunks` assumes chunk ETags decode as base64 MD5 values. `ViewFromChunks` ignores errors from `NonOverlappingVisibleIntervals`, so callers may get partial or empty views if manifest resolution fails.

## Test Signals
Covered by `filechunks_test.go`, `filechunks2_test.go`, and `filechunks_read_test.go`, including overwrite cases, random writes, source-file-ID deltas, read views, and real bug cases. Tests emphasize interval correctness more than error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks.go -->
