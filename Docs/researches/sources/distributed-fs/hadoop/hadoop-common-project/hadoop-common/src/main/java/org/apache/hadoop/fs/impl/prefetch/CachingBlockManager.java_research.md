<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/CachingBlockManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/CachingBlockManager.java

## Purpose
Provides block-oriented reads with optional asynchronous prefetching and a local disk cache. It sits between a concrete stream reader (`read(ByteBuffer, offset, size)` inherited from `BlockManager`) and higher-level prefetching input stream logic.

## Important APIs, Types, And Functions
Public behavior comes through `get`, `release`, `requestPrefetch`, `cancelPrefetches`, `requestCaching`, `close`, and counters such as `numAvailable`, `numCached`, `numCachingErrors`, and `numReadErrors`. `PrefetchTask` and `CachePutTask` run in `ExecutorServiceFuturePool`. `readBlock`, `prefetch`, `read`, `addToCacheAndRelease`, `cachePut`, and `createCache` are the core extension/control points.

## Control Flow
`get` acquires a buffer from `BufferPool`, then `getInternal` either consumes a `READY` prefetched block, waits if another task is using it, or synchronously reads a blank block. `readBlock` first checks `BlockCache`, then reads the underlying file into the buffer, flips it, and marks `READY`. `requestPrefetch` opportunistically claims a free blank buffer and schedules `PrefetchTask`. `cancelPrefetches` turns active prefetch/ready buffers into cache requests so work is not wasted. `requestCaching` schedules `CachePutTask`, which waits on any prefetch future, writes the buffer to cache, marks it `DONE`, and disables future caching if a cache write exceeds the slow-operation threshold.

## State And Persistence
The manager owns a `BufferPool`, a `BlockCache` (`SingleFilePerBlockCache` by default), atomic error counters, an atomic `cachingDisabled` flag, `BlockOperations` diagnostics, and a `closed` flag. Cached blocks persist only as temporary local files owned by the cache and are deleted on close.

## Dependencies And Integration Points
Integrates `BlockData`, `BufferData`, `BlockOperations`, `LocalDirAllocator`, Hadoop `Configuration`, `DurationTrackerFactory`, `PrefetchingStatistics`, and the executor wrapper. Concrete subclasses provide the actual remote/source read.

## Risks
Concurrency depends on repeated state checks outside and inside `synchronized(data)`. A stuck prefetch can delay cache-put for up to `TIMEOUT_MINUTES`. `closed` is not atomic/volatile, so callers rely on synchronization and stream lifecycle discipline. Slow local cache writes permanently disable caching for the stream. Errors during prefetch are logged and swallowed by task wrappers, so tests must inspect counters/state, not just thrown exceptions.

## Test Signals
Cover cache hit before source read, synchronous read fallback, duplicate prefetch requests, prefetch cancellation followed by cache population, slow cache disabling, read/cache error counters, close idempotency, and executor queue-time statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/CachingBlockManager.java -->
