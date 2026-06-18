# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/MetadataSyncLockManager.java

## Purpose
`MetadataSyncLockManager` provides path-based read/write locks used to deduplicate or serialize metadata sync operations before corresponding inodes may exist. It locks path prefixes rather than inode objects.

## Important APIs, types, and functions
`lockPath(AlluxioURI)` returns a `MetadataSyncPathList`, acquiring read locks for every prefix and a write lock for the final path. `getLockPoolSize()` exposes the weak-value lock pool size for tests/metrics. Nested `MetadataSyncPathList` implements `Closeable` and releases locks in reverse order.

## Control flow
`lockPath` splits the URI path into components, builds normalized prefix keys ending in `/`, and obtains locks from `LockPool` in order. If any acquisition fails, it closes already-acquired locks. The caller uses try-with-resources to release the list.

## State and persistence behavior
The lock manager stores only in-memory lock-pool state. It does not persist metadata. Weak lock-pool values allow unused path locks to be reclaimed.

## Dependencies and integration points
It depends on `LockPool`, `LockMode`, configuration keys for pool sizing, `PathUtils`, and `LockResource`. `InodeSyncStream` uses a static instance when concurrent metadata sync deduplication is enabled.

## Risks
Path-key construction must be consistent for all callers or deduplication fails. The method catches `Throwable` but does not rethrow after cleanup in the catch block, so callers could receive a partially constructed list if an error path is not propagated by the thrown exception; this should be reviewed. Invalid path handling is covered by `PathUtils`. Prefix lock ordering avoids deadlocks only if all metadata sync callers use the same order.

## Test signals
`MetadataSyncLockManagerTest` covers pool sizing, invalid paths, lock compatibility, and garbage collection of weak locks. Concurrency tests with overlapping paths provide the most important integration signal.
