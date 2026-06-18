# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/underfs/UfsStatusCache.java

Purpose: thread-safe cache from Alluxio namespace paths to UFS statuses and directory child listings, with optional asynchronous prefetch and absent-path integration.

Important APIs/types/functions: `addStatus`, `addChildren`, `remove`, `getStatus`, `hasStatus`, `fetchStatusIfAbsent`, `fetchChildrenIfAbsent`, package-private `getChildrenIfAbsent`, `getChildren`, `prefetchChildren`, and `cancelAllPrefetch`.

Control flow: explicit adds validate status name against URI basename, update absent cache, store status, and update global metrics. Child adds derive child paths and store each status plus the parent listing. Fetching a missing file resolves the mount, calls UFS `getStatus`, increments sync metrics, rewrites the status name to the Alluxio path name, and caches or records absence. Fetching children first waits for active prefetch with timeout/retry/cancel checks, then uses cached children, then optionally falls back to synchronous UFS listing.

State and persistence: all state is in concurrent maps for statuses, active prefetch jobs, and child collections. Absent state is delegated to `UfsAbsentPathCache`. No journal persistence. Metrics counters track cache size, child size, prefetch operations, retries, successes, failures, cancellations, and paths.

Dependencies/integration: integrates with `MountTable`, `RpcContext` cancellation, `UnderFileSystem`, `DefaultFileSystemMaster.Metrics`, `UfsAbsentPathCache`, and metadata sync code.

Risks: `fetchChildrenIfAbsent` removes the active prefetch job in the `finally` block even after a timeout, so later loops no longer find it in the map though they still wait on the local future. `remove` decrements status cache size for removed children even though those child statuses also remain in `mStatuses`, which can skew counters. Cached `Collection<UfsStatus>` objects may be externally mutable unless callers pass immutable collections.

Test signals: add validation, absent cache short-circuit, UFS fetch success/null/not-found/IOException, child cache metrics, prefetch reuse/cancel/failure/retry, RPC cancellation while waiting, executor rejection, and `cancelAllPrefetch`.
