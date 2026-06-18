# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/AsyncUfsAbsentPathCacheTest.java

## Purpose
Unit tests for `AsyncUfsAbsentPathCache`, validating detection and caching of absent UFS paths under a mount, cache invalidation on mount/path changes, capacity-limited metrics, and hit/miss counters.

## Important APIs/types/functions
- Sets `MASTER_UFS_PATH_CACHE_CAPACITY` to 3 with `ConfigurationRule`.
- Builds `MasterUfsManager`, `MountTable`, and `AsyncUfsAbsentPathCache`.
- `before()` mounts a temporary local UFS at `/mnt`.
- Helper `process(path)` calls `processPathSync(path, Collections.emptyList())`.
- Helper `checkPaths(firstAbsent)` asserts descendants of first absent path are cached absent while ancestors are not.
- Nested `TestAsyncUfsAbsentPathCache` overrides cached gauge timeout for metrics tests.

## Control flow
- `isAbsent` checks unknown path, processes absent path, verifies descendant absence, then creates a UFS folder and verifies it is not absent.
- Root/directory tests process paths where different ancestor levels are the first missing UFS component.
- Add/remove UFS directory tests show processing adapts when UFS directories appear or disappear.
- `removeMountPoint` unmounts and remounts the same UFS and expects old cache entries to be gone.
- `removePath` creates previously absent paths and reprocesses to clear cached absence.
- Metric tests reset metrics, add paths, wait for cached gauge refresh, and assert cache size/hit/miss values.

## State and persistence behavior
- Uses real local filesystem directories under a temporary folder as UFS state.
- Cache state is in-memory, capacity-bounded, and tied to mount table/mount ids.
- Metrics are global and reset before gauge tests.

## Dependencies and integration points
- Integrates absent path cache, mount table resolution, UFS manager, local UFS configuration, Alluxio metrics registry, and path normalization.

## Risks and edge cases
- Metrics tests rely on sleeps around cached gauges; they can be timing-sensitive.
- Capacity is small and intentional, so eviction behavior affects metric expectations.
- Mount id changes on remount are important for invalidation; tests would catch stale mount-scoped cache keys.

## Test signals
- Strong signal for absent-path cache correctness, especially first-missing-ancestor detection and invalidation after UFS/mount changes.
