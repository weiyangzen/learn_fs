# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/AsyncUfsAbsentPathCache.java

Purpose: asynchronous implementation of `UfsAbsentPathCache` that caches Alluxio paths known to be absent in the mounted UFS. It avoids repeated expensive UFS existence checks for missing paths while handling invalidation races when paths are created.

Important APIs and types: constructor wires mount table, thread pool, clock, Guava cache, in-flight path locks, and metrics. Public methods are `processAsync`, `addSinglePath`, `processExisting`, and `isAbsentSince`. Internal `processPathSync`, `processSinglePath`, `getMountInfo`, `getNestedPaths`, and `PathLock` implement traversal and locking.

Control flow: `processAsync` submits a path check. `processPathSync` finds the first non-persisted component under the mount and checks nested paths one by one. `processSinglePath` ensures one processor per path, resolves the path against the original mount id, calls `ufs.exists`, caches the first absent component, and stops traversal. `processExisting` marks in-flight locks for invalidation and removes cache entries for nested components.

State and persistence behavior: in-memory cache mapping path string to `(sync time, mount id)`. No journaled state. `isAbsentSince` walks ancestors until mount base and returns true only when a cached entry is newer than the requested timestamp and belongs to the same mount id.

Dependencies and integration points: integrates `MountTable`, `MountInfo`, `UnderFileSystem.exists`, `Inode` persistence state, configuration capacities/thread counts, metrics gauges, and sync/load code that updates absent cache.

Risks: asynchronous races are subtle; invalidation intent must be set before cache removal to avoid stale absent entries after creation. Mount changes invalidate by mount id check. Unbounded task submission to the thread pool queue could lag under heavy missing-path traffic. UFS existence errors are logged and stop traversal.

Test signals: tests should cover absent hit/miss, ancestor lookup, timestamp and mount id filtering, processExisting race invalidation, duplicate in-flight path processing, mount changes, persisted-prefix base index, and metrics.
