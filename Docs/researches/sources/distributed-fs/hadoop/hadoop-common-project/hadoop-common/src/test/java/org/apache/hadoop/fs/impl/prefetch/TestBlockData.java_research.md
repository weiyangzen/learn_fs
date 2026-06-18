# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBlockData.java

## Purpose
`TestBlockData` validates block metadata calculations and per-block state transitions for prefetching.

## Important APIs, Types, And Functions
It constructs `BlockData(fileSize, blockSize)` and tests `getFileSize()`, `getBlockSize()`, `getNumBlocks()`, `isLastBlock()`, `isValidOffset()`, `getSize()`, `getBlockNumber()`, `getStartOffset()`, `getRelativeOffset()`, `getState()`, `setState()`, and `getStateString()`.

## Control Flow
`testArgChecks()` checks valid constructors and invalid negative/zero arguments or out-of-range block numbers. `testComputedFields()` runs helper cases for zero and nonzero file sizes. The helper verifies zero-file methods reject invalid ranges, computes expected block counts and last block size, iterates offsets to validate mapping to blocks/relative offsets, and exercises state transitions through `NOT_READY`, `QUEUED`, `READY`, and `CACHED`.

## State And Persistence
State is in-memory block metadata and state array inside `BlockData`. No persistence occurs.

## Dependencies And Integration Points
It depends on `ExceptionAsserts`, Hadoop test intercepts, and `BlockData.State`. Prefetch scheduling/cache code relies on these calculations.

## Risks
Off-by-one errors at EOF or last block size can corrupt prefetch reads. Zero-length files have intentionally empty valid ranges that must be handled carefully.

## Test Signals
Signals are exact block counts, start/relative offsets, last-block detection, and accepted/rejected state access for edge cases.
