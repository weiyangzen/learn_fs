# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InvalidationSyncCacheTest.java

## Purpose
This test focuses on `UfsSyncPathCache` invalidation semantics after interval-based invalidation callers were removed. It establishes how explicit sync notifications and invalidations interact for root, child, and multi-level paths.

## Important APIs, Types, and Functions
The test uses `UfsSyncPathCache.recordStartSync`, `notifySyncedPath`, `notifyInvalidation`, and `shouldSyncPath`, with `DescendantType.NONE`, `ONE`, and `ALL`. It also configures `MASTER_UFS_PATH_CACHE_CAPACITY` and observes cache eviction through the constructor callback and direct `mItems.cleanUp()`.

## Control Flow, State, and Persistence
A mocked `Clock` advances an `AtomicLong` on `millis()` calls, making sync timestamps deterministic. Tests first assert unsynced paths require sync, then notify syncs at different descendant depths and invalidate paths to verify upward and downward freshness propagation. Eviction fills a cache under `/one`, then checks evicted paths require sync while retained entries stay valid.

## Dependencies and Integration Points
The cache depends on Alluxio URI ancestry, global configuration, Caffeine-like cache cleanup behavior, and `DescendantType` semantics shared by metadata sync/listing APIs.

## Risks
The tests encode intentionally conservative invalidation behavior: after invalidating and resyncing a child, the root can still require descendant sync. This is called out as an improvement opportunity and is a compatibility risk for future cache optimizations.

## Test Signals
Coverage includes direct validation, one-level propagation, multi-level propagation, parent invalidation invalidating descendants, sync interval coexistence, and invalidations racing with in-progress syncs.
