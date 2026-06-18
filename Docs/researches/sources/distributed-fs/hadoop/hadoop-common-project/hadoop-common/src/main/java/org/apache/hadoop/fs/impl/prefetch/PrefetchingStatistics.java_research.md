<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchingStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchingStatistics.java

## Purpose
Defines the statistics callback contract for prefetch streams, file-cache activity, executor queue latency, and buffer memory accounting.

## Important APIs, Types, And Functions
The interface extends `IOStatisticsSource` and declares `prefetchOperationStarted`, `blockAddedToFileCache`, `blockRemovedFromFileCache`, `blockEvictedFromFileCache`, `prefetchOperationCompleted`, `executorAcquired`, `memoryAllocated`, and `memoryFreed`.

## Control Flow
Implementations are called around prefetch operation start/end, cache add/remove/evict, executor acquisition, and buffer pool allocation/free. `prefetchOperationStarted` returns a `DurationTracker` that callers close or mark failed.

## State And Persistence
This file stores no state. Implementations decide whether counters are in-memory, exported via `IOStatistics`, or no-op.

## Dependencies And Integration Points
Consumed by `BufferPool`, `CachingBlockManager`, and `SingleFilePerBlockCache`. It aligns stream-level prefetch events with Hadoop's statistics framework.

## Risks
Implementations must be thread-safe because callbacks occur from caller and executor threads. Incorrect memory/cache counter pairing can produce misleading stream statistics.

## Test Signals
Use a recording implementation to assert callback order and counts for buffer allocation, prefetch success/failure, cache insertion, eviction, close, and executor queue waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchingStatistics.java -->
