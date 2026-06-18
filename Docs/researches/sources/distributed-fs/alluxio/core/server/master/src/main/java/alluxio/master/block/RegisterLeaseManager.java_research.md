# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/RegisterLeaseManager.java

## Purpose
`RegisterLeaseManager` bounds concurrent worker registration work by issuing time-limited leases. It protects the master from too many simultaneous large registration streams and can optionally reject leases based on JVM heap availability.

## Important APIs and Types
- Uses a `Semaphore` sized by `MASTER_WORKER_REGISTER_LEASE_COUNT`.
- Tracks active leases in `ConcurrentHashMap<Long, RegisterLease>` keyed by worker ID.
- `tryAcquireLease(GetRegisterLeasePRequest)` returns an existing lease, creates a new lease, or rejects.
- `hasLease(long)` and `releaseLease(long)` are used by `DefaultBlockMaster`.
- Optional `JvmSpaceReviewer` is enabled by `MASTER_WORKER_REGISTER_LEASE_RESPECT_JVM_SPACE`.

## Control Flow
Construction validates positive concurrency and initializes the semaphore and optional JVM reviewer. Acquisition first returns an existing lease for the same worker, then checks JVM space, lazily recycles expired leases, and tries to acquire a semaphore permit. On success it records a new `RegisterLease` with the configured TTL; on failure it returns empty. Release removes the worker lease and releases the semaphore, logging if the lease was already recycled or absent.

## State and Persistence Behavior
All lease state is in-memory runtime coordination. Leases are not journaled and do not survive master restart. Expiration is lazy: expired leases are recycled only when another acquisition attempt calls `tryRecycleLease`.

## Dependencies and Integration Points
The manager depends on Alluxio configuration, `CommonUtils` time, `RegisterLease`, and `JvmSpaceReviewer`. `DefaultBlockMaster` exposes lease APIs to worker RPC handlers and releases leases when streaming registration finishes.

## Risks and Edge Cases
The `containsKey` plus `get` pattern can race with release/recycle and could theoretically return null in a concurrent edge. Lazy expiration means stale leases can keep capacity occupied until the next request. Releasing after lazy recycle logs and does not release again, preventing permit over-release. Existing leases bypass fresh JVM-space review.

## Test Signals
`RegisterLeaseManagerTest` covers granting, limits, repeated worker requests, release behavior, and lease expiration/recycling under configured counts and TTLs.
