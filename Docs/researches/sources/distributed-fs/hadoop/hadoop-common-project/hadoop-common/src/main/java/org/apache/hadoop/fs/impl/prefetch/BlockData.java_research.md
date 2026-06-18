# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockData.java

## Purpose
Represents block geometry and per-block readiness state for a file read through prefetching.

## Important APIs, Types, and Functions
State enum NOT_READY/QUEUED/READY/CACHED; constructor; getBlockSize/getFileSize/getNumBlocks; isLastBlock; getBlockNumber; getSize; isValidOffset; getStartOffset; getRelativeOffset; getState/setState; getStateString().

## Control Flow
Constructor validates file/block sizes, computes numBlocks by ceiling division, and initializes every block NOT_READY. Offset/block accessors validate ranges. Last block size is shortened to remaining file bytes.

## State and Persistence Behavior
Stores immutable fileSize/blockSize/numBlocks and mutable State[] per block. No persistence.

## Dependencies and Integration Points
Used by BlockManager and caching/prefetch managers to coordinate reads.

## Risks and Test Signals
Risks include zero-length file edge cases, int truncation for huge block counts, offset end boundary validation, and unsynchronized state mutation. Tests should cover zero file, exact multiple, partial last block, invalid offsets, and state strings.
