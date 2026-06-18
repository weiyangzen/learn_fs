<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_read_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filechunks_read_test.go

## Purpose
Tests `readResolvedChunks` over overlapping, random, sequential, and production-like chunk layouts.

## Important APIs and Functions
`TestReadResolvedChunks`, `TestReadResolvedChunks2`, `TestRandomizedReadResolvedChunks`, `TestSequentialReadResolvedChunks`, `TestActualReadResolvedChunks`, and `TestActualReadResolvedChunks2` all call `readResolvedChunks`. `randomWrite` writes expected timestamp ownership into an array and returns a matching chunk.

## Control Flow and State
Most tests construct chunk slices and inspect or print visible intervals. The randomized test builds a 1 MiB logical array and verifies every visible interval maps to the timestamp stored by simulated writes.

## Persistence Behavior
No persistence. The tests model only chunk metadata and in-memory expected state.

## Dependencies and Integration Points
Uses `filer_pb.FileChunk`, `math.MaxInt64`, random generation, and the package-private visible interval fields. It directly protects the sweep-line algorithm consumed by read planning and compaction.

## Risks
Several tests print output without assertions, so they are useful during manual debugging but weak in CI. Randomized testing lacks an explicit deterministic seed in this file, which can make rare failures harder to reproduce.

## Test Signals
The randomized test is the strongest signal because it verifies byte-range ownership. Actual-case tests document known layouts from production or bugs, but would not fail unless manually inspected or expanded with assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filechunks_read_test.go -->
