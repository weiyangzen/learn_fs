<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks_test.go

## Purpose
Main regression suite for chunk compaction, visible interval merging, read-view construction, and range projection.

## Important APIs and Functions
Tests `CompactFileChunks`, `NonOverlappingVisibleIntervals`, `ViewFromChunks`, `ViewFromVisibleIntervals`, and helper `addVisibleInterval`. `BenchmarkCompactFileChunks` measures compaction over interleaved chunks.

## Control Flow and State
The interval tests use table-driven cases for simple adjacent chunks, full overwrites, partial overwrites, disjoint writes, same-offset updates, large real updates, and a documented real bug. Read tests project logical ranges into `ChunkView` slices and assert file ID, chunk offset, view size, and view offset.

## Persistence Behavior
No persistence. State is in-memory slices and interval lists.

## Dependencies and Integration Points
Depends on `filer_pb.FileChunk`, package interval types, `assert`, and random generation. It is the closest direct test coverage for reader planning and garbage compaction behavior used by filer writes and deletes.

## Risks
Some tests use `t.Fatalf` after indexing `Expected[x]`; if the function returns more intervals than expected, the failure can be an index panic instead of a cleaner assertion. Random compaction test depends on random data but uses deterministic logical checks.

## Test Signals
Strong coverage of normal and edge overlap semantics. It validates both visible intervals and read views, including very large file offsets. Error paths, manifest resolution failures, and ETag behavior are not covered here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_test.go -->
