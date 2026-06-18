# Research: subset-b-007348

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/EmptyPrefetchingStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/EmptyPrefetchingStatistics.java

## Purpose
Provides a singleton no-op implementation of `PrefetchingStatistics` for callers that do not want to publish IO statistics.

## Important APIs, Types, And Functions
`getInstance()` returns the singleton. All statistic methods are implemented as no-ops except `prefetchOperationStarted`, which returns a stub `DurationTracker`.

## Control Flow
There is no branching or mutable workflow. Callers receive a reusable object and can invoke every statistics callback without null checks.

## State And Persistence
Only a private static singleton exists. No counters are stored and no statistics persist.

## Dependencies And Integration Points
Used wherever prefetch components require a non-null `PrefetchingStatistics`. It depends on `IOStatisticsSupport.stubDurationTracker`.

## Risks
Using this in production disables visibility into prefetch latency, cache occupancy, eviction, executor wait time, and buffer memory accounting. That is acceptable only when statistics are intentionally unavailable.

## Test Signals
Verify singleton identity, no exceptions from all callback methods, and that returned duration trackers can be closed/failed safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/EmptyPrefetchingStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ExecutorServiceFuturePool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ExecutorServiceFuturePool.java

## Purpose
Adapts a Java `ExecutorService` to the minimal future-pool API needed by the prefetch layer, avoiding a dependency on Twitter/Scala future pools.

## Important APIs, Types, And Functions
`executeFunction(Supplier<Void>)` submits supplier work, `executeRunnable(Runnable)` submits runnable work and casts the returned future, `shutdown(Logger, timeout, unit)` delegates to `HadoopExecutors.shutdown`, and `toString` exposes executor identity.

## Control Flow
Calls are direct pass-throughs to the wrapped executor. Supplier tasks run through `f::get`; runnable tasks run through `r::run`.

## State And Persistence
The only state is the wrapped `ExecutorService`. Task completion and cancellation semantics are those of the executor and returned `Future`.

## Dependencies And Integration Points
Used by `CachingBlockManager` for prefetch and cache-put tasks. Depends on Java concurrency APIs and Hadoop executor shutdown utilities.

## Risks
The class does not add cancellation beyond standard `Future.cancel`; comments note started work cannot really be cancelled by this abstraction. `executeRunnable` uses an unchecked cast from `Future<?>` to `Future<Void>`. Rejected execution and null task failures propagate from the underlying executor.

## Test Signals
Use direct executors or small thread pools to verify supplier/runnable execution, exception propagation through futures, shutdown timeout behavior, and rejected execution behavior after shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ExecutorServiceFuturePool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/FilePosition.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/FilePosition.java

## Purpose
Tracks the current absolute and buffer-relative read position for a prefetching stream. It binds a `BufferData` block to an absolute file offset and records per-buffer read statistics.

## Important APIs, Types, And Functions
Key methods are `setData`, `buffer`, `data`, `absolute`, `setAbsolute`, `relative`, `isWithinCurrentBuffer`, `blockNumber`, `isLastBlock`, `invalidate`, `bufferFullyRead`, `incrementBytesRead`, and read-stat accessors.

## Control Flow
Construction validates file and block sizes and creates `BlockData`; no position is valid until `setData`. `setData` validates offsets, duplicates the buffer, stores the buffer start and read-start offsets, seeks the duplicate to the requested read offset, and resets counters. Reads then advance the duplicate buffer externally while `incrementBytesRead` updates statistics. `setAbsolute` only moves within the current buffer; otherwise it leaves state unchanged.

## State And Persistence
State is in-memory: `BlockData`, current `BufferData`, duplicated `ByteBuffer`, `bufferStartOffset`, `readStartOffset`, and counters. `invalidate` clears the active buffer and marks offsets invalid.

## Dependencies And Integration Points
Used by prefetching input stream code to decide whether a seek can stay inside the current buffer, whether the current block is fully consumed, and which block should be released or cached.

## Risks
`isWithinCurrentBuffer` treats `pos == bufferEndOffset` as inside, allowing position at limit. Callers must pair `incrementBytesRead` with actual reads or `bufferFullyRead` will be wrong. Duplicated buffers share content but not position, so direct use of the original `BufferData` buffer can diverge from `FilePosition`.

## Test Signals
Cover zero-length files, start/read offsets at buffer boundaries, in-buffer and out-of-buffer seeks, last-block detection, invalid access exceptions, and single-byte versus bulk-read counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/FilePosition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchConstants.java

## Purpose
Centralizes prefetch implementation constants, currently the timeout used while acquiring cache-entry write locks during eviction and close.

## Important APIs, Types, And Functions
Defines package-private `PREFETCH_WRITE_LOCK_TIMEOUT = 5` and `PREFETCH_WRITE_LOCK_TIMEOUT_UNIT = TimeUnit.SECONDS`.

## Control Flow
No runtime control flow beyond class initialization. Constructor is private to prevent instantiation.

## State And Persistence
Contains only static constants. No mutable state or persistence.

## Dependencies And Integration Points
`SingleFilePerBlockCache` uses these constants when trying to acquire per-entry write locks before deleting cache files.

## Risks
The constants are package-private and fixed. If cache file deletion regularly blocks longer than five seconds, eviction/close logs errors and leaves files behind rather than waiting.

## Test Signals
Simulate held read locks in `SingleFilePerBlockCache` and verify eviction/close respects the configured five-second timeout path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/PrefetchConstants.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ResourcePool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ResourcePool.java

## Purpose
Abstract base for fixed/reusable resource pools used by the prefetch implementation.

## Important APIs, Types, And Functions
Subclasses implement `acquire`, `tryAcquire`, `release`, and `createNew`. `close()` is a no-op hook, and protected `close(T)` lets subclasses clean individual items.

## Control Flow
This base class defines contracts only. Concrete implementations such as `BoundedResourcePool` provide blocking, non-blocking, and lifecycle behavior.

## State And Persistence
No state is stored in this class.

## Dependencies And Integration Points
`BufferPool` uses a bounded subclass to manage `ByteBuffer` instances. Other resource types can reuse the abstraction if they match the acquire/release model.

## Risks
The base class does not enforce bounds, closed state, null handling, or duplicate release protection. Those guarantees must be supplied by subclasses and callers.

## Test Signals
Tests belong mostly to subclasses: acquire/release ordering, close cleanup, item creation limits, and behavior after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ResourcePool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Retryer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Retryer.java

## Purpose
Provides simple sleep-and-retry timing for prefetch buffer acquisition and block retrieval loops.

## Important APIs, Types, And Functions
The constructor validates per-retry delay, max delay, and status interval. `continueRetry()` sleeps for `perRetryDelay`, increments accumulated delay, and reports whether retrying remains allowed. `updateStatus()` tells callers when to log or perform maintenance.

## Control Flow
Callers loop until work completes or `continueRetry` returns false. Status updates occur only after at least one sleep and when the accumulated delay is divisible by the status interval.

## State And Persistence
State is the accumulated `delay` and fixed delay parameters. There is no persistence.

## Dependencies And Integration Points
Used by `BufferPool.acquire` and `CachingBlockManager.get` to avoid indefinite silent waits and to trigger periodic state logging or ready-block release.

## Risks
Interrupted sleeps are ignored and the interrupt flag is not restored, so cancellation responsiveness is weak. The retry loop uses fixed sleep intervals, not exponential backoff or deadlines.

## Test Signals
Use small delays to verify max-delay termination, status-update cadence, constructor validation, and behavior when the sleeping thread is interrupted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Retryer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/SingleFilePerBlockCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/SingleFilePerBlockCache.java

## Purpose
Implements `BlockCache` by storing each cached block as a separate temporary local file and evicting entries with an LRU list.

## Important APIs, Types, And Functions
Public methods are `containsBlock`, `blocks`, `size`, `get`, `put`, `close`, `isCacheSpaceAvailable`, and `toString`. The internal `Entry` stores block number, file path, size, checksum, per-entry lock, and linked-list pointers. `readFile`, `writeFile`, `getEntry`, `addToLinkedListAndEvictIfRequired`, `deleteBlockFileAndEvictCache`, `deleteCacheFiles`, `validateEntry`, and `getTempFilePath` provide the core behavior.

## Control Flow
`put` validates duplicates by checksum, creates a temp file through `LocalDirAllocator`, writes the buffer, records size/checksum, updates statistics, moves the entry to the LRU head, and evicts the tail when the count exceeds `maxBlocksCount`. `get` looks up the entry, moves it to the head, reads the file into the caller's buffer, rewinds, and validates size/checksum. Eviction and close attempt timed write locks before deleting files.

## State And Persistence
State includes a concurrent block map, LRU `head`/`tail`, `entryListSize`, `numGets`, closed flag, and temporary files on local disk. Files persist only until eviction or cache close; failed deletion can leave temp files behind.

## Dependencies And Integration Points
Used by `CachingBlockManager`. Integrates Hadoop `LocalDirAllocator`, `Configuration`, stream statistics, `DurationTrackerFactory`, `STREAM_FILE_CACHE_EVICTION`, Guava `ImmutableSet`, Java NIO channels, and POSIX file permissions.

## Risks
LRU list state is separate from the concurrent map and must remain synchronized under `blocksLock`. Duplicate `put` validates against the caller's buffer rather than rewriting. Deletion can fail if locks are held past timeout, leaving cache files and statistic mismatches. `getTempFilePath` assumes POSIX permissions are supported.

## Test Signals
Test put/get checksum validation, duplicate put, LRU eviction order, close deletion, lock-timeout paths, cache-space probing, non-POSIX local FS behavior, and statistic updates for add/remove/evict.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/SingleFilePerBlockCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Validate.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Validate.java

## Purpose
Supplies prefetch-package validation helpers with consistent argument and state error messages.

## Important APIs, Types, And Functions
Provides null, positive, non-negative, required, valid, non-empty, exact-size, equality, multiple, greater, greater-or-equal, less-or-equal, range, path-exists/file/dir, and `checkState` helpers.

## Control Flow
All methods validate conditions and throw `IllegalArgumentException` through Hadoop `Preconditions.checkArgument`, except `checkState`, which throws `IllegalStateException`. Collection and iterable helpers reduce to length/existence checks.

## State And Persistence
No state. Constructor is private.

## Dependencies And Integration Points
Used throughout prefetch classes to keep parameter checking concise. Path helpers depend on `java.nio.file.Files`.

## Risks
`checkNotNullAndNotEmpty(Iterable)` calls `iterator().hasNext()` once; unusual iterables with side effects may be affected. Numeric helpers accept `long` but messages do not distinguish integer overflow at caller sites.

## Test Signals
Assert exception types/messages for each helper, especially range boundaries, empty arrays/iterables, path checks, and `checkState`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/Validate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/package-info.java

## Purpose
Declares the `org.apache.hadoop.fs.impl.prefetch` package as private, unstable block caching support for object store clients.

## Important APIs, Types, And Functions
No runtime APIs. The file contains package documentation and `InterfaceAudience.Private` / `InterfaceStability.Unstable` annotations.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Provides package-level metadata for all prefetch classes.

## Risks
The annotations warn downstream callers not to treat this implementation package as stable public API.

## Test Signals
Documentation/annotation checks only; no runtime tests are needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalConfigKeys.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalConfigKeys.java

## Purpose
Defines local filesystem default configuration constants and builds `FsServerDefaults` for the `file://` AbstractFileSystem implementation.

## Important APIs, Types, And Functions
Constants include block size, replication, stream buffer size, bytes per checksum, write packet size, encryption flag, trash interval, checksum type, and key provider URI. `getServerDefaults()` constructs the defaults object.

## Control Flow
`getServerDefaults` returns a new `FsServerDefaults` populated from static constants. There is no configuration lookup in this class.

## State And Persistence
Static constants only. No persisted state.

## Dependencies And Integration Points
Used by `RawLocalFs.getServerDefaults`. Extends `CommonConfigurationKeys` and depends on `DataChecksum.Type` and `FsServerDefaults`.

## Risks
Comments note some settings are placeholders ignored by local/raw/checksum FS behavior. Consumers should not assume local checksums or encryption follow these values.

## Test Signals
Verify defaults exposed through local AFS match constants and remain compatible with legacy local filesystem expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalFs.java

## Purpose
Implements the checksum-wrapped local `AbstractFileSystem` by extending `ChecksumFs` over `RawLocalFs`.

## Important APIs, Types, And Functions
The package-private constructors `LocalFs(Configuration)` and `LocalFs(URI, Configuration)` are the key entry points used by AFS creation.

## Control Flow
Construction creates a new `RawLocalFs` and passes it to `ChecksumFs`. The URI constructor delegates to the configuration constructor to satisfy `AbstractFileSystem#createFileSystem`.

## State And Persistence
State is inherited from `ChecksumFs` and the delegated raw filesystem. This file stores no additional fields.

## Dependencies And Integration Points
Integrates the newer `AbstractFileSystem` API with local checksum behavior and `RawLocalFs`.

## Risks
Constructors are package-private and assume creation through Hadoop filesystem factories. Behavior is mostly inherited, so regressions in `RawLocalFs` or `ChecksumFs` define the actual risk.

## Test Signals
Instantiate through `AbstractFileSystem`, create/read local files with checksum wrapper behavior, and verify URI construction works for `file://` local paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/RawLocalFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/RawLocalFs.java

## Purpose
Adapts the legacy `RawLocalFileSystem` to the `AbstractFileSystem` API through `DelegateToFileSystem`.

## Important APIs, Types, And Functions
Constructors bind `FsConstants.LOCAL_FS_URI`, `RawLocalFileSystem`, and the `file` scheme. Overrides include `getUriDefaultPort`, `getServerDefaults(Path)`, deprecated `getServerDefaults()`, and `isValidName`.

## Control Flow
Construction delegates all filesystem operations to a new `RawLocalFileSystem`. Server defaults come from `LocalConfigKeys`. Name validation always returns true so OS-specific validation happens in the underlying local filesystem.

## State And Persistence
State is inherited delegate state. No extra fields are stored in this class.

## Dependencies And Integration Points
Used by `LocalFs` and AFS factory paths. Depends on local constants, `FsServerDefaults`, and `Path`.

## Risks
Skipping name validation is intentional but means invalid paths fail later and differently by platform. Defaults are generic and may not describe the actual local device.

## Test Signals
Verify `file://` AFS creation, no default port, server defaults, and path handling on platform-specific invalid names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/RawLocalFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/package-info.java

## Purpose
Documents the local `AbstractFileSystem` package and marks it limited private and unstable.

## Important APIs, Types, And Functions
No runtime APIs; only package annotations.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Applies metadata to `LocalFs`, `RawLocalFs`, and local config classes.

## Risks
Signals that these adapter classes are not stable public API outside the named Hadoop components.

## Test Signals
Annotation/documentation verification only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntry.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntry.java

## Purpose
Defines immutable Hadoop ACL entries with scope, type, optional name, and optional permission, plus stable parsing/formatting for shell and API use.

## Important APIs, Types, And Functions
Accessors expose `type`, `name`, `permission`, and `scope`. `Builder` creates entries. `toStringStable`, `parseAclSpec`, `parseAclEntry`, and `aclSpecToString` implement the string contract.

## Control Flow
Parsing splits ACL specs by comma, then entry strings by colon. Optional `default:` changes scope, type is parsed case-insensitively through enum uppercasing, name is optional, and permission is required only when `includePermission` is true. Extra or missing fields throw `HadoopIllegalArgumentException`.

## State And Persistence
Instances are immutable value objects. Stable string output is a persistence/compatibility format for shell output and specs.

## Dependencies And Integration Points
Used by ACL filesystem APIs, `AclStatus`, `AclUtil`, `ScopedAclEntries`, shell ACL commands, and protobuf/RPC-facing permission flows.

## Risks
`String.split(":")` drops trailing empty fields, so parsing relies on explicit length checks and examples. `aclSpecToString` assumes a non-empty list and would fail on empty input. `toString()` delegates to stable form today but is annotated unstable.

## Test Signals
Round-trip access/default ACLs, removal specs without permissions, invalid types/permissions, named and unnamed entries, empty specs, equality/hash behavior, and stable lowercase formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryScope.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryScope.java

## Purpose
Defines whether an ACL entry enforces access on the owning inode or supplies defaults for children.

## Important APIs, Types, And Functions
Enum values are `ACCESS` and `DEFAULT`.

## Control Flow
No behavior beyond enum identity.

## State And Persistence
Enum constants are stable public API and appear in ACL object state and parsing/formatting.

## Dependencies And Integration Points
Used by `AclEntry`, `AclUtil`, `ScopedAclEntries`, `AclStatus`, and shell ACL commands to separate access and default ACL handling.

## Risks
Adding or renaming values would break stable ACL string and API compatibility.

## Test Signals
Verify parsing of `default:` entries and correct access/default partitioning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryScope.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryType.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryType.java

## Purpose
Defines ACL subject classes: owner/specific user, owning/specific group, mask, and other.

## Important APIs, Types, And Functions
Enum values are `USER`, `GROUP`, `MASK`, and `OTHER`. `toStringStable()` returns the enum name; `toString()` delegates to it but is annotated unstable.

## Control Flow
No branching beyond string conversion.

## State And Persistence
Enum values are public stable API and are serialized through ACL string specs.

## Dependencies And Integration Points
Used by ACL parsing, effective-permission calculation, ACL shell output, and logical ACL assembly.

## Risks
The ordinal/name contract is relied on indirectly by parsing and stable output; changes must preserve names.

## Test Signals
Parse and format all types, especially mask and named user/group effective-permission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntryType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclStatus.java

## Purpose
Represents ACL metadata for a path, including owner, group, sticky bit, ordered ACL entries, and optional permission bits used to calculate effective ACL permissions.

## Important APIs, Types, And Functions
`Builder` collects owner/group/entries/sticky/permission. Accessors expose state. `getEffectivePermission(AclEntry)` and `getEffectivePermission(AclEntry, FsPermission)` apply mask/group permissions for access and default ACL entries.

## Control Flow
Effective permission requires either server-provided permission or caller-provided fallback. Named entries and group entries are intersected with the access group action or, for default ACLs, the penultimate ACL entry's permission. Owner and other entries return their own permission directly.

## State And Persistence
The constructor copies entries into a new list but does not wrap it unmodifiable. The object is intended immutable but exposes the internal list through `getEntries`.

## Dependencies And Integration Points
Returned by filesystem ACL APIs and consumed by shell `getfacl` for effective comments. Depends on `AclEntry`, `FsPermission`, `FsAction`, and Hadoop `Preconditions`.

## Risks
`equals`/`hashCode` ignore the `permission` field, which may surprise callers. Default effective-permission logic assumes ACL ordering and at least three entries. The mutable returned list can violate immutability expectations.

## Test Signals
Validate effective permissions for named user/group, mask, minimal/default ACLs, old NameNode fallback permission, equality behavior, and mutation attempts on `getEntries`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclUtil.java

## Purpose
Builds logical ACL lists by combining permission bits with extended ACL entries, and identifies minimal ACLs.

## Important APIs, Types, And Functions
`getAclFromPermAndEntries`, `getMinimalAcl`, and `isMinimalAcl` are the public helpers.

## Control Flow
`getAclFromPermAndEntries` emits owner from user bits, copies access extended entries until the first default entry, emits either a mask or group entry from group bits depending on whether access ACLs exist, emits other, then appends default entries. `getMinimalAcl` creates the three permission-derived access entries.

## State And Persistence
Stateless utility class.

## Dependencies And Integration Points
Used by shell `getfacl` and ACL consumers that need a full logical ACL from compact permission + extended-entry storage.

## Risks
The function assumes extended entries are ordered with all access entries before default entries. Misordered input can produce incorrect logical ACLs.

## Test Signals
Check minimal ACL, access-only extended ACLs, default-only ACLs, mixed access/default ordering, and mask/group entry selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ChmodParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ChmodParser.java

## Purpose
Parses chmod-style octal or symbolic modes and applies them to an existing `FileStatus`.

## Important APIs, Types, And Functions
The constructor supplies chmod-specific regexes to `PermissionParser`. `applyNewPermission(FileStatus)` combines the parsed mode with existing permission bits.

## Control Flow
Octal modes can have an optional leading `+` and optional sticky bit. Symbolic modes allow `u/g/o/a`, `+/-/=`, `r/w/x/X/t`, comma-separated clauses, and whitespace. `applyNewPermission` enables capital `X` when the target is a directory or any execute bit is already set.

## State And Persistence
Parsed symbolic/octal mode state is inherited from `PermissionParser`; no additional fields.

## Dependencies And Integration Points
Used by chmod shell command flows. Depends on `FileStatus` and `FsPermission`.

## Risks
Regex behavior defines user-facing chmod compatibility. Incorrect `X` handling changes executable bits for files. Parser state is not reusable for multiple different mode strings.

## Test Signals
Exercise octal with and without sticky bit, symbolic add/remove/set, comma clauses, `X` on files/directories, invalid modes, and whitespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ChmodParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsAction.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsAction.java

## Purpose
Models POSIX read/write/execute action sets as bit-compatible enum ordinals with symbolic strings.

## Important APIs, Types, And Functions
Values range from `NONE` to `ALL`. `implies`, `and`, `or`, `not`, and `getFsAction(String)` implement permission algebra and parsing.

## Control Flow
Permission operations use ordinal bit operations and return from a cached `values()` array. `getFsAction` linearly matches the three-character symbol.

## State And Persistence
Enum constants and `SYMBOL` strings form a stable public API. Ordinal ordering is semantically important.

## Dependencies And Integration Points
Used by `FsPermission`, ACL entries/status, permission parsers, and shell ACL display.

## Risks
Changing enum order would break bit arithmetic. `and`/`or` assume non-null operands. Symbol parsing accepts only exact canonical strings like `rw-`.

## Test Signals
Truth tables for implies/and/or/not, symbol parsing for all actions, and null handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsCreateModes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsCreateModes.java

## Purpose
Wraps a masked create permission together with its original unmasked mode so create APIs can preserve both values.

## Important APIs, Types, And Functions
`applyUMask(FsPermission, FsPermission)` returns an existing create-mode wrapper or creates one. `create(masked, unmasked)` constructs the wrapper. Overrides `getMasked`, `getUnmasked`, and `toString`.

## Control Flow
If a mode already has an unmasked value, `applyUMask` returns it unchanged. Otherwise it applies the umask, then stores masked state in the superclass and unmasked state in a final field.

## State And Persistence
State is the inherited masked `FsPermission` plus final `unmasked`. Serialization follows `FsPermission` behavior unless callers inspect the extra getter.

## Dependencies And Integration Points
Used by create/mkdir flows that need to pass both requested and effective permissions through filesystem layers.

## Risks
Uses Java `assert` for invariant checks, so production does not enforce them. Subclassing `FsPermission` means code that copies or serializes only base fields can lose unmasked information.

## Test Signals
Verify idempotent wrapping, masked/unmasked getters, string format, and behavior when passed through APIs typed as `FsPermission`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsCreateModes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsPermission.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsPermission.java

## Purpose
Represents Hadoop POSIX-style permission bits and sticky bit, with writable serialization, string parsing, umask handling, defaults, and compatibility hooks for extended status flags.

## Important APIs, Types, And Functions
Constructors accept actions, short/int mode, copy, or raw string. Core methods include `fromShort`, `toShort`, `toOctal`, `toString`, `applyUMask`, `getUMask`, `setUMask`, default permission factories, `valueOf`, `read/write/readFields`, `createImmutable`, and extended-bit hooks.

## Control Flow
Short modes map bit groups to `FsAction` values and sticky bit. Integer modes mask native stat values with `01777`. `getUMask` reads configuration, parses with `UmaskParser`, logs and rethrows clearer errors on invalid values. `valueOf` parses 10-character Unix symbolic strings, ignoring the file-type character and mapping `t/T` to sticky bit.

## State And Persistence
Stores user/group/other actions and sticky bit. Writable serialization writes a short. `ImmutableFsPermission` blocks `readFields`. Java deserialization validates fields through `ObjectInputValidation`.

## Dependencies And Integration Points
Used throughout Hadoop file status, ACL, create, chmod, local/SFTP status, and protobuf conversion code. Depends on `RawParser`, `UmaskParser`, configuration keys, writable factories, and SLF4J logging.

## Risks
Enum ordinal bit layout is fundamental. Deprecated extended-bit methods return false unless subclasses override. `getMasked/getUnmasked` are extension hooks used by `FsCreateModes`. Configuration parsing error type affects user diagnostics.

## Test Signals
Round-trip short/octal/string/writable forms, native stat masking, sticky bit display, umask config parsing, immutable read rejection, default permissions, and `valueOf` edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsPermission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionParser.java

## Purpose
Shared parser engine for chmod, umask, and raw permission strings.

## Important APIs, Types, And Functions
The constructor applies caller-provided symbolic and octal patterns. `combineModes` combines parsed sticky/user/group/other segments with existing bits. `combineModeSegments` implements `+`, `-`, `=`, and capital `X`.

## Control Flow
The parser first tries the symbolic regex, then octal regex. Symbolic parsing walks comma-separated clauses, determines affected classes, builds mode bits, records operation type per segment, and marks the parser symbolic. Octal parsing sets all segment operations to `=` and extracts optional sticky bit plus three octal digits.

## State And Persistence
Stores parsed segment modes and operation characters in protected fields for subclasses. No persistence.

## Dependencies And Integration Points
Base for `ChmodParser`, `UmaskParser`, and `RawParser`.

## Risks
Regexes are supplied by subclasses, so subtle differences define command compatibility. State fields represent only the final parsed effect per class, so malformed comma handling must be caught during parsing. `X` logic depends on caller-provided `exeOk`.

## Test Signals
Use subclass parsers to cover symbolic class defaults, comma separation, sticky bit, `+/-/=`, `X`, octal parsing, and invalid trailing input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionStatus.java

## Purpose
Bundles owner, group, and `FsPermission` into a writable value object used in filesystem metadata.

## Important APIs, Types, And Functions
Constructors, `createImmutable`, getters, `applyUMask`, `write`, `readFields`, static `read`, and `toString` form the API.

## Control Flow
`applyUMask` returns a new `PermissionStatus` with the same owner/group and masked permission. Serialization writes owner/group strings with `Text` and delegates permission serialization.

## State And Persistence
Stores `username`, `groupname`, and `permission`. Writable factory registration supports Hadoop serialization. The immutable subclass rejects `readFields`.

## Dependencies And Integration Points
Used by filesystem metadata paths needing ownership plus mode. Depends on `FsPermission`, `Text`, and `WritableFactories`.

## Risks
The no-arg constructor exists for writable deserialization and can produce partially initialized objects before `readFields`. Immutability is enforced only by the private subclass.

## Test Signals
Writable round-trip, immutable read rejection, umask application preserving owner/group, and null/empty owner/group handling as expected by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/PermissionStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/RawParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/RawParser.java

## Purpose
Parses raw permission modes used by `new FsPermission(String)`.

## Important APIs, Types, And Functions
The constructor uses raw symbolic and octal regexes. `getPermission()` combines parsed bits against zero and returns a short.

## Control Flow
Raw symbolic parsing accepts full nine-character permission strings with optional sticky forms, while octal parsing accepts optional sticky plus three octal digits. `getPermission` treats execute as allowed for capital-X-style combination.

## State And Persistence
Parsed mode state is inherited from `PermissionParser`.

## Dependencies And Integration Points
Used only through `FsPermission(String)`.

## Risks
Raw parsing is stricter than chmod symbolic clauses. Tests must distinguish raw full-mode strings from chmod expressions like `u+r`.

## Test Signals
Parse `rwxr-x---`, sticky variants, octal modes, invalid lengths/characters, and compare resulting shorts to expected modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/RawParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ScopedAclEntries.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ScopedAclEntries.java

## Purpose
Splits an ordered ACL entry list into access and default scopes.

## Important APIs, Types, And Functions
Constructor partitions entries. `getAccessEntries()` and `getDefaultEntries()` return the two lists. `calculatePivotOnDefaultEntries` finds the first default entry.

## Control Flow
The constructor finds the first `AclEntryScope.DEFAULT`. If none exists, all entries are access and default is empty. Otherwise entries before the pivot are access and entries from the pivot onward are default.

## State And Persistence
Stores sublist views or empty lists. There is no copying, so lists reflect the source list's backing behavior.

## Dependencies And Integration Points
Used by `AclCommands.GetfaclCommand` and any code that needs scope-specific ACL processing.

## Risks
Assumes ACLs are sorted by scope with all default entries after access entries. Misordered input leaves later access entries in the default slice. Sublist views can be affected by source-list mutation.

## Test Signals
Partition access-only, default-only, mixed ordered ACLs, empty lists, and intentionally misordered lists to document behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/ScopedAclEntries.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/UmaskParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/UmaskParser.java

## Purpose
Parses filesystem umask configuration values in octal or symbolic form.

## Important APIs, Types, And Functions
The constructor supplies umask-specific regexes to `PermissionParser` and computes `umaskMode`. `getUMask()` returns the parsed short.

## Control Flow
Octal umasks accept optional sticky bit plus three digits. Symbolic umasks allow `u/g/o/a`, `+/-/=`, and `r/w/x` but intentionally do not allow `X` or `t`. Symbolic values combine against `0777` and invert chmod-like semantics as needed by `combineModes`.

## State And Persistence
Stores final `umaskMode` plus inherited parse fields.

## Dependencies And Integration Points
Used by `FsPermission.getUMask(Configuration)`.

## Risks
The symbolic semantics differ from chmod: `+` clears bits in the mask and `-` sets bits because a umask denies permissions. User-facing errors are wrapped by `FsPermission.getUMask`.

## Test Signals
Parse common octal values like `022`, symbolic values like `u=rwx,g=rx,o=`, invalid `X`/`t`, and verify resulting mask application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/UmaskParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/package-info.java

## Purpose
Marks the permission package private and unstable at package level.

## Important APIs, Types, And Functions
No runtime APIs; package annotations only.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Applies package metadata to Hadoop permission and ACL classes, although several individual classes expose stronger public/stable annotations.

## Risks
Package-level metadata can be broader than individual class annotations; callers should follow the class-level annotations for API stability.

## Test Signals
Annotation/documentation verification only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/PBHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/PBHelper.java

## Purpose
Converts Hadoop filesystem structures between in-memory Java objects and protobuf messages.

## Important APIs, Types, And Functions
`convert(FsPermissionProto)`, `convert(FsPermission)`, `convert(FileStatusProto)`, and `convert(FileStatus)` are the public static helpers.

## Control Flow
Permission conversion stores the short mode. FileStatus conversion switches on proto file type to set directory, symlink, or file fields; file replication is checked to fit 16 bits. Owner and group are weak-interned on proto-to-object conversion. Object-to-proto conversion sets type-specific fields, permission, owner/group, times, and flags for ACL, encryption, erasure coding, and snapshot support.

## State And Persistence
Stateless utility class. Protobuf output is a serialized compatibility format for filesystem RPC/protocol layers.

## Dependencies And Integration Points
Depends on `FSProtos`, `FileStatus`, `Path`, `FsPermission`, and `StringInterner`. Used by protobuf-based filesystem protocols.

## Risks
Replication overflow throws `IOException`; unknown file type throws `IllegalStateException`. Path and symlink are serialized via `toString`, so URI/path formatting compatibility matters. Only `FsPermission.toShort()` is preserved, not subclass create-mode metadata.

## Test Signals
Round-trip file, directory, and symlink statuses; all attribute flags; owner/group interning; replication overflow; and permission short preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/PBHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/package-info.java

## Purpose
Declares the protobuf filesystem helper package.

## Important APIs, Types, And Functions
No runtime APIs; only the `org.apache.hadoop.fs.protocolPB` package declaration.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Provides package-level documentation for protobuf helpers such as `PBHelper`.

## Risks
None beyond documentation drift.

## Test Signals
No runtime tests required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/protocolPB/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPConnectionPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPConnectionPool.java

## Purpose
Maintains reusable JSch SFTP channels keyed by host, port, and user for `SFTPFileSystem`.

## Important APIs, Types, And Functions
`connect`, `disconnect`, `shutdown`, `getFromPool`, `returnToPool`, connection count accessors, and nested `ConnectionInfo` define the pool. `setMaxConnection` changes the threshold for keeping idle channels.

## Control Flow
`connect` first tries an idle channel. If none is connected, it creates a JSch session, optionally adds an identity file, fills missing user/password defaults, disables strict host key checking, connects a session/channel, and records it. `disconnect` closes the channel/session only when live connections exceed `maxConnection`; otherwise it returns the channel to the idle map. `shutdown` sets max to zero and disconnects every known channel.

## State And Persistence
State includes `maxConnection`, `liveConnectionCount`, `idleConnections`, and `con2infoMap`. Connections are live network/session resources, not persistent state.

## Dependencies And Integration Points
Used exclusively by `SFTPFileSystem`. Depends on JSch `Session`/`ChannelSftp`, Hadoop `StringUtils`, and SLF4J.

## Risks
Host key checking is disabled, which is a security risk. `getFromPool` removes the entire idle set for a `ConnectionInfo` when taking one channel, potentially losing references to other idle channels. A disconnected borrowed channel path removes `null` after assigning `channel = null`, leaving stale map entries. Count accessors are not synchronized.

## Test Signals
Pool reuse, max-connection eviction, shutdown idempotency, disconnected idle channels, key/password auth paths, host/user case-insensitive keys, and stale idle map behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPConnectionPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPFileSystem.java

## Purpose
Implements Hadoop `FileSystem` over SFTP using JSch channels and a small connection pool.

## Important APIs, Types, And Functions
Overrides `initialize`, `getUri`, `open`, `create`, `append`, `rename`, `delete`, `listStatus`, `mkdirs`, `getFileStatus`, working-directory/home methods, and `close`. Helpers handle URI-derived configuration, connect/disconnect, absolute path resolution, status lookup, permission conversion, recursive delete, mkdir recursion, and same-channel operations.

## Control Flow
Initialization extracts host, port, user, password, keyfile, and pool size from URI/config. Each public operation borrows a channel, performs SFTP calls, and returns the channel in `finally` or stream close. `open` resolves symlinks and wraps `SFTPInputStream`. `create` optionally deletes existing files, creates parent directories, and returns a stream whose close disconnects. Status lookup lists the parent directory and matches by filename; symlinks are resolved with `realpath` and restatted.

## State And Persistence
State includes the configured URI, connection pool, and closed flag. Remote filesystem metadata and data persist on the SFTP server; local state does not.

## Dependencies And Integration Points
Integrates Hadoop `FileSystem`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, and JSch `ChannelSftp`.

## Risks
Append is unsupported. Rename rejects existing destinations and claims same-directory limitations in constants, though implementation calls SFTP rename with paths. Recursive delete builds child paths from qualified statuses in a way that needs path coverage. `getHomeDirectory` returns null on errors. Permission/user/group are derived from numeric SFTP attrs. Stream users must close outputs before other APIs to avoid channel blocking.

## Test Signals
URI/config parsing, open/read/seek, create overwrite/non-overwrite, recursive mkdir/delete, directory listing, symlink status, rename failures, closed filesystem behavior, connection return on stream close, and auth/keyfile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPInputStream.java

## Purpose
Provides an `FSInputStream` wrapper around a JSch SFTP input stream with Hadoop seek and statistics behavior.

## Important APIs, Types, And Functions
Implements `seek`, `available`, `seekToNewSource`, `getPos`, `read`, `close`, and private `seekInternal`/`checkNotClosed`.

## Control Flow
Construction opens `channel.get(path)` and reads length via `lstat`. `seek` records the desired `nextPos`. `read` checks EOF, calls `seekInternal`, reads one byte, updates `pos` and `nextPos`, and increments statistics. Forward seek skips on the current stream; backward seek closes and reopens the remote stream, then skips to the target.

## State And Persistence
Holds the SFTP channel, path, wrapped stream, optional statistics, `closed`, actual `pos`, desired `nextPos`, and content length. Remote data is not modified.

## Dependencies And Integration Points
Created by `SFTPFileSystem.open` and closed by its wrapping `FSDataInputStream`, which returns the channel to the pool.

## Risks
`skip` may skip fewer bytes than requested; the code does not loop to reach `nextPos`. Backward seek reopens the file and may see changed remote content. The stats condition uses single `&`, which still works for booleans but does not short-circuit. Only single-byte `read()` is implemented here; bulk reads rely on `InputStream` defaults unless inherited behavior wraps it.

## Test Signals
Read EOF, negative seek, forward/backward seek with partial skip behavior, statistics increments, close idempotency, and remote file changes across backward seek.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/SFTPInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/package-info.java

## Purpose
Documents the SFTP filesystem package.

## Important APIs, Types, And Functions
No runtime APIs.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Applies to `SFTPFileSystem`, `SFTPConnectionPool`, and `SFTPInputStream`.

## Risks
Documentation is minimal and does not capture security/compatibility caveats.

## Test Signals
No runtime tests required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/sftp/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/AclCommands.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/AclCommands.java

## Purpose
Registers and implements FsShell ACL commands `-getfacl` and `-setfacl`.

## Important APIs, Types, And Functions
`registerCommands` adds command classes. `GetfaclCommand` parses `-R`, prints owner/group/sticky flags and access/default ACL entries. `SetfaclCommand` parses `-b`, `-k`, `-R`, `-m`, `-x`, and `--set`, then calls filesystem ACL APIs.

## Control Flow
`getfacl` expands one path, optionally recursively, builds a logical ACL from permission bits plus extended entries, partitions scopes, and prints effective permissions when masks restrict entries. `setfacl` rejects incompatible remove/modify/set flag combinations, parses ACL specs with or without permissions depending on remove mode, and in recursive mode filters default ACL entries out for files.

## State And Persistence
Command state includes parsed options and ACL entry lists. Persistent effects happen through filesystem ACL mutations.

## Dependencies And Integration Points
Extends `FsCommand` and uses `CommandFormat`, `PathData`, `AclEntry`, `AclStatus`, `AclUtil`, `ScopedAclEntries`, `FsPermission`, and filesystem ACL APIs.

## Risks
Recursive filtering must avoid applying default ACLs to files. Effective-permission output depends on ACL ordering and available permission bits. Option validation uses one generic error for several invalid combinations.

## Test Signals
Shell tests for getfacl minimal/extended/default ACLs, sticky flags, recursive traversal, every setfacl option, invalid option mixes, remove specs without permissions, and recursive file-vs-directory ACL filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/AclCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Command.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Command.java

## Purpose
Provides the base execution framework for Hadoop filesystem shell commands: option processing, argument expansion, path recursion, error reporting, usage reflection, and command factory access.

## Important APIs, Types, And Functions
Subclasses implement `getCommandName`, `run(Path)` or path-processing hooks. Main hooks include `processOptions`, `processRawArguments`, `expandArguments`, `expandArgument`, `processArguments`, `processArgument`, `processPathArgument`, `processPaths`, `processPath`, `postProcessPath`, `recursePath`, `isSorted`, and `getListingGroupSize`.

## Control Flow
`run(String...)` warns for deprecated commands, processes options, expands raw arguments into `PathData`, and processes each item. Existing paths flow through `processPathArgument` and `processPaths`; missing paths go to `processNonexistentPath`. Recursive traversal performs post-visit DFS over directory contents, optionally using sorted listings or grouped iterator batches. Errors are caught per argument/path, recorded, printed, and converted into non-zero exit codes.

## State And Persistence
Per-command state includes args/name/exit code/error count/recursive flag/depth/exceptions/output streams and factory reference. No filesystem persistence except subclass operations.

## Dependencies And Integration Points
Used by FsShell command classes. Depends on `PathData`, Hadoop configuration, remote iterators, logging, and reflection for static `NAME`, `USAGE`, and `DESCRIPTION` fields.

## Risks
Subclass contracts are flexible; missing `processPath` implementations fail at runtime. Error handling intentionally continues after many IOExceptions. Reflection-based usage fails if static fields are absent. Recursion depth is mutable shared command state.

## Test Signals
Command lifecycle unit tests for option parsing hooks, glob expansion failures, nonexistent paths, recursive traversal, sorted vs iterator listings, interrupted IO exit code 130, usage/description reflection, and error counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Command.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFactory.java

## Purpose
Registers shell command names and creates command instances for FsShell.

## Important APIs, Types, And Functions
`registerCommands` reflectively invokes a class's static `registerCommands(CommandFactory)`. `addClass`, `addObject`, `getInstance`, and `getNames` manage command mappings.

## Control Flow
Class registrations map names to command classes. Object registrations map names to reusable instances and put null in the class map so names appear in listings. `getInstance` returns a registered object or reflectively instantiates a class with the provided configuration, then sets command name and factory.

## State And Persistence
In-memory maps from command name to class or object. No persistence.

## Dependencies And Integration Points
Used by FsShell startup and help/usage commands. Depends on Hadoop `ReflectionUtils`, `Configured`, and command registration conventions.

## Risks
`getInstance` requires non-null configuration. Reusable object registrations can retain state across invocations if the command object is mutable. Reflection failures are wrapped as runtime exceptions with stringified stack traces.

## Test Signals
Register class/object commands, instantiate with config, list sorted names, unknown command returns null, null configuration failure, and registrar reflection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFormat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFormat.java

## Purpose
Parses simple FsShell command options and validates remaining positional argument counts.

## Important APIs, Types, And Functions
Constructors define min/max parameters and allowed options. `addOptionWithValue`, `parse`, `getOpt`, `getOptValue`, and `getOpts` are the API. Nested exceptions report too many/few arguments, unknown options, and duplicate options.

## Control Flow
Parsing destructively walks the argument list until a non-option, `-` stdin marker, or `--`. Known boolean options are removed and marked true. Known value options remove their value if present and not option-looking; otherwise they store an empty string. Unknown options are skipped only when `null` was supplied as a possible option. After option removal, positional count bounds are enforced.

## State And Persistence
Parser instances retain option states and option values, so they are not automatically reset between parses.

## Dependencies And Integration Points
Used by shell commands such as ACL commands and many FsShell operations.

## Risks
Options with values cannot accept values beginning with `-` except the literal `-`. Reusing a `CommandFormat` instance across parses can leak prior option state. `args.size() > minPar` influences value consumption, so edge cases near minimum positional counts need coverage.

## Test Signals
Boolean options, value options, `--`, stdin `-`, unknown-ignore mode, duplicate option declaration, min/max failures, value missing, and parser reuse behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandUtils.java

## Purpose
Provides a tiny formatting helper for multi-line command descriptions.

## Important APIs, Types, And Functions
`formatDescription(String usage, String... desciptions)` builds `usage: first` followed by tab-indented continuation lines. The parameter name contains a typo but does not affect behavior.

## Control Flow
The method assumes at least one description string, appends the first after the usage, then appends remaining descriptions on new indented lines.

## State And Persistence
Stateless package-private utility class.

## Dependencies And Integration Points
Used by shell command classes that want consistent help text formatting.

## Risks
Calling with zero descriptions throws `ArrayIndexOutOfBoundsException`. It hardcodes tab indentation and newline formatting.

## Test Signals
Format one-line and multi-line descriptions and verify zero-description behavior if callers can reach it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/CommandUtils.java -->
