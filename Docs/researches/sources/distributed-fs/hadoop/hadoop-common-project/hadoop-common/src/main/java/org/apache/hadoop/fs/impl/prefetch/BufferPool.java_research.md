<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BufferPool.java

## Purpose
Manages a bounded pool of `ByteBuffer` instances for the prefetching stream implementation. It prevents unbounded allocation by keeping buffers either free in a `BoundedResourcePool` or associated with a `BufferData` object for one block.

## Important APIs, Types, And Functions
The public surface is `acquire(int)`, `tryAcquire(int)`, `release(BufferData)`, `getAll()`, `numCreated()`, `numAvailable()`, and `close()`. Internally `acquireHelper`, `releaseDoneBlocks`, `releaseReadyBlock`, `find`, and `canRelease` implement the block-to-buffer ownership protocol. Allocation records memory through `PrefetchingStatistics.memoryAllocated`, and `close` reports freed memory.

## Control Flow
`acquire` loops through `Retryer`, periodically logging state and forcing a distant `READY` block to `DONE` if progress stalls. `tryAcquire` performs a non-blocking acquisition. Both first release `DONE` buffers, reuse existing non-DONE buffers for the same block, or allocate/claim a cleared buffer and wrap a duplicate in `BufferData`. `release` accepts only `READY` or `DONE` data, clears the backing buffer, returns it to the pool, and recursively frees newly done blocks.

## State And Persistence
State is in-memory only: `allocated` is an `IdentityHashMap<BufferData, ByteBuffer>` and `pool` owns reusable buffers. There is no disk persistence. `close` cancels outstanding action futures on all tracked `BufferData` instances before destroying maps and the pool.

## Dependencies And Integration Points
Used by `CachingBlockManager` to gate read, prefetch, and cache-put concurrency. It depends on `BoundedResourcePool`, `BufferData.State`, `Retryer`, `Validate`, Hadoop preconditions, and `PrefetchingStatistics`.

## Risks
Correctness depends on the `BufferData` state machine and on callers eventually marking blocks `DONE`. `releaseReadyBlock` intentionally discards a ready block under pressure, which may trade locality for liveness. The identity map means equivalent `BufferData` values are not interchangeable. `close` nulls fields, so post-close callers can see null failures if higher layers do not stop first.

## Test Signals
Exercise pool exhaustion, duplicate acquisition for the same block, `DONE` release, slow-acquire forced release of a `READY` block, action future cancellation on close, and memory allocation/free counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BufferPool.java -->
