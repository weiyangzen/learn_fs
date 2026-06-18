# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBufferPool.java

## Purpose
`TestBufferPool` validates the prefetch-specific pool of `BufferData` objects.

## Important APIs, Types, And Functions
It constructs `BufferPool(size, bufferSize, PrefetchingStatistics)` and tests `acquire(blockNumber)`, `tryAcquire(blockNumber)`, `release(BufferData)`, `getAll()`, `numCreated()`, and `numAvailable()`. Helper `acquire()` asserts same block acquisition returns the same `BufferData`.

## Control Flow
Argument tests reject invalid pool/buffer sizes, null statistics, negative block numbers, and null release. `testGetAndRelease()` verifies initial empty iteration, acquires two buffers, sees `tryAcquire()` return null when full, iterates two active entries, releases only after setting state to `READY`, and observes availability restored. `testRelease()` verifies release is rejected from `BLANK`, `PREFETCHING`, and `CACHING`, but accepted from `READY`.

## State And Persistence
State is in-memory buffer ownership, block-number mapping, active buffer collection, and pool counters. No persistence.

## Dependencies And Integration Points
It depends on `BufferPool`, `BufferData.State`, `PrefetchingStatistics`, and `EmptyPrefetchingStatistics`. Prefetch readers rely on this pool to avoid over-allocation.

## Risks
Releasing buffers before they are ready can expose partially filled data. Same-block acquisition identity must be stable while a block is active.

## Test Signals
Signals are active iteration counts, null `tryAcquire()` at capacity, same-object acquire for the same block, counter changes after release, and release rejection for unsafe states.
