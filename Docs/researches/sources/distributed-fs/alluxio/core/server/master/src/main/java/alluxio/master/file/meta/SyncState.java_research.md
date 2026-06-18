# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SyncState.java

## Purpose
`SyncState` is the per-path mutable timestamp record used by `UfsSyncPathCache`. It tracks invalidation and validation times for the exact path, direct children, and recursive descendants, plus whether the path is known to be a file.

## Important APIs, Types, and Functions
Fields are package-private volatile timestamps: `mDirectChildrenInvalidation`, `mRecursiveChildrenInvalidation`, `mInvalidationTime`, `mSyncTime`, `mDirectChildrenSyncTime`, `mRecursiveSyncTime`, and volatile `mIsFile`. Methods update these monotonically: `setInvalidationTime()`, `setDirectChildInvalidation()`, `setRecursiveChildInvalidation()`, `setIsFile()`, and `setValidationTime(long, DescendantType)`.

## Control Flow, State, and Persistence
State is in-memory cache state only. The class assumes at most one writer per sync state and multiple volatile readers. Invalidation setters keep the maximum timestamp. `setValidationTime()` always updates exact sync time if newer, updates direct-child sync time for `DescendantType.ONE` or `ALL`, and updates recursive sync time for `ALL`. `setIsFile()` only transitions from file to directory/unknown by setting false when the new value is false and current value is true; it intentionally does not transition false to true.

## Dependencies and Integration Points
`UfsSyncPathCache` owns instances and interprets timestamps to decide whether future RPCs need UFS sync. `DescendantType` controls whether validation covers the path only, direct children, or all descendants. `LockingScheme` indirectly depends on this state through `UfsSyncPathCache.shouldSyncPath()`.

## Risks
The one-writer assumption is not enforced by the class. Because fields are volatile but updates are compound comparisons, concurrent writers can lose updates. The file-to-directory-only transition for `mIsFile` is subtle: callers needing to mark an unknown path as a file cannot do it through `setIsFile(true)` once false.

## Test Signals
Tests should cover monotonic timestamp updates, descendant-type validation effects, invalidation versus validation comparisons in `UfsSyncPathCache`, volatile-reader expectations under controlled concurrency, and `mIsFile` transition semantics.
