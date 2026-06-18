# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/TtlBucket.java

## Purpose
`TtlBucket` is the in-memory container used by the file master TTL checker to group inode ids whose expiration timestamps fall in the same checker interval. The interval length is `MASTER_TTL_CHECKER_INTERVAL_MS`, captured in the static `sTtlIntervalMs`, and each bucket is ordered by its interval start time.

## Important APIs, types, and functions
The class exposes interval metadata through `getTtlIntervalStartTimeMs()`, `getTtlIntervalEndTimeMs()`, and static `getTtlIntervalMs()`. `getInodeIds()` returns an unmodifiable key-set view, while `getInodeExpiries()` exposes inode ids with remaining TTL-processing retry counts. `addInode(Inode)` uses `DEFAULT_RETRY_ATTEMPTS`; `addInode(Inode, int)` records the smaller remaining retry count if the inode already exists. `removeInode(InodeView)` and `size()` provide mutation and accounting. `compareTo`, `equals`, and `hashCode` define bucket identity solely by interval start time.

## Control flow
There is no background processing in this class. Callers compute the correct interval, construct or find a bucket, then call `addInode`. The `ConcurrentHashMap.compute` call makes duplicate insertion deterministic under concurrency by keeping the lower retry count. Ordering is delegated to `Long.compare` on interval start times for use in sorted sets.

## State and persistence behavior
State is volatile in memory: `mTtlIntervalStartTimeMs` and `mInodeToRetryMap`. This class does not write journal entries or checkpoints itself; `TtlBucketList` checkpoints inode ids and reconstructs buckets from the inode store. The static interval is intentionally non-final so tests can alter it.

## Dependencies and integration points
It depends on Alluxio configuration/property keys for the TTL interval, `Inode`/`InodeView` for id extraction, Guava `Objects`, and JDK concurrent collections. It integrates with `TtlBucketList` and ultimately with the inode TTL checker.

## Risks
Bucket equality ignores retry map contents, so callers must not use equal buckets as distinct state containers. The unmodifiable views are live views over a concurrent map, so iteration can observe concurrent changes. Changing `sTtlIntervalMs` after buckets are created can make existing interval boundaries inconsistent with lookup logic.

## Test signals
Useful tests should cover interval boundary inclusion, zero interval handling, duplicate insertion retry-min behavior, remove semantics, compare/equality/hash consistency, and concurrent add/remove visibility through `TtlBucketList`.
