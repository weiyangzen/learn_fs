# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsSyncPathCache.java

## Purpose
`UfsSyncPathCache` tracks when Alluxio paths were synchronized with UFS and whether later invalidations require another sync. It is a core decision helper for metadata sync, mapping path strings to `SyncState` objects with exact, direct-child, recursive-child sync and invalidation timestamps.

## Important APIs, types, and functions
The constructor builds a Guava cache sized by `MASTER_UFS_PATH_CACHE_CAPACITY` and concurrency-level configured by `MASTER_UFS_PATH_CACHE_THREADS`. `recordStartSync()` returns the current clock time. `getSyncTimesForPath(AlluxioURI)` returns direct and recursive sync times if cached. `shouldSyncPath(AlluxioURI, long, DescendantType)` computes a `SyncCheck`. `notifyInvalidation(AlluxioURI)` and `notifySyncedPath(AlluxioURI, DescendantType, long, Long, boolean)` update invalidation and validation state. Root state is held separately in `mRoot` behind `mRootLock`.

## Control flow
`shouldSyncPath` walks from the target path to root, selecting the strongest usable sync timestamp based on whether the request covers no children, one level, or all descendants. At the base path it considers file syncs, direct-child syncs, recursive syncs, and invalidation fields; at parent and ancestor levels it uses direct or recursive sync times depending on child/file semantics. `computeSyncResult` then compares interval policy, validation time, invalidation time, and current clock time: interval `0` always syncs, negative intervals suppress sync unless invalidated, and non-negative intervals sync when stale. `notifyInvalidationInternal` updates the path and all ancestors. `notifySyncedPath` writes validation time and clears invalidation fields only when no newer invalidation arrived after sync start.

## State and persistence behavior
The cache is in-memory only. Root is never evicted; non-root paths can be evicted by Guava. The removal listener currently does not call `onCacheEviction` because invalidation propagation on eviction was disabled due to issue commentary in the source. Sync times are based on the injected `Clock`, making test-time control possible.

## Dependencies and integration points
It depends on `AlluxioURI`, `PathUtils`, `DescendantType`, `SyncState`, `SyncCheck`, Guava cache, Alluxio configuration, and `LockResource`. It is called from inode sync paths and file-master sync decisions, including external invalidation notifications.

## Risks
The state machine is subtle: wrong descendant type, file flag, or timestamp ordering can either skip needed UFS syncs or trigger excessive syncs. Eviction invalidation propagation is disabled, so eviction can lose invalidation history. Root locking differs from non-root `Cache.asMap().compute` updates, so code changing root handling needs concurrency scrutiny.

## Test signals
Tests should cover all `DescendantType` combinations, file versus directory base paths, direct and recursive ancestor validation, negative/zero/positive intervals, invalidation after sync start, root path updates, eviction behavior, path cleanup, and injected-clock boundary cases.
