<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks2_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks2_test.go

## Purpose
Adds regression tests for chunk delta and compaction behavior, especially sync scenarios where file IDs differ between clusters but `SourceFileId` links chunks back to their origin.

## Important APIs and Functions
`TestDoMinusChunks` exercises `DoMinusChunks` and `DoMinusChunksBySourceFileId`. `TestCompactFileChunksRealCase` runs `CompactFileChunks` against a real chunk layout and logs compacted versus garbage chunks through `printChunks`.

## Control Flow and State
The sync test models cluster A and cluster B appending and overwriting the same file. It first computes chunks deleted by an "empty file" event, then uses source-file-ID aware subtraction to ensure cluster A also removes chunks that correspond to B's source IDs.

## Persistence Behavior
No persistence. All test state is in-memory chunk slices.

## Dependencies and Integration Points
Depends on `filer_pb.FileChunk`, `assert`, package chunk helpers, and logging. The scenario integrates with filer sync semantics outside this file by validating the chunk ID mapping logic used when remote metadata events delete or replace data.

## Risks
The real-case compaction test logs results but has no assertions, so it is diagnostic rather than protective. The source-file-ID test is valuable but narrow.

## Test Signals
Strong signal that cross-cluster deletions require comparing both `FileId` and `SourceFileId`. Weak signal for the logged compaction case because failures would not fail the test unless the function panics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks2_test.go -->
