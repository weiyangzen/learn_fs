# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/CachedRecordStore.java

## Purpose
`CachedRecordStore` is the base class for state-store APIs that keep an in-memory cache of persistent records.

## Important APIs, Types, And Functions
It extends `RecordStore<R>` and implements `StateStoreCache`. Important methods are `loadCache(boolean)`, `overrideExpiredRecords`, `overrideExpiredRecord`, `getCachedRecords`, and `getCachedRecordsAndTimeStamp`. It uses read/write locks to protect cached record lists and tracks cache timestamp, initialization, and last update.

## Control Flow
`loadCache` throttles refreshes to at most once every 500 ms unless forced. It fetches all records through the driver, optionally commits expired-record overrides/deletions, atomically replaces the cache under the write lock, updates metrics, and records local update time. Reads validate driver readiness and initialization, then copy cached records under the read lock.

## State, Persistence, And Dependencies
In-memory state includes cached records, the driver timestamp, initialized flag, update timestamps, locks, and the override-expired flag. Persistent state is owned by the `StateStoreDriver`; this class writes only when overriding expired/deletable records. It depends on `QueryResult`, `BaseRecord` expiration methods, metrics, and driver overwrite/delete handling.

## Integration Points
`MembershipStore`, `RouterStore`, `MountTableStore`, and `DisabledNameserviceStore` inherit this cache behavior. `StateStoreCacheUpdateService` calls `loadCache` periodically.

## Risks
`getCachedRecordsAndTimeStamp` returns the internal list object rather than a copy, unlike `getCachedRecords`. Async driver override mode returns null and leaves stale records until a later refresh. Cache refresh failures return false but keep old data. The 500 ms throttle can surprise explicit callers unless `force` is true.

## Test Signals
Tests should cover forced and throttled refresh, unavailable cache exceptions, expired-record override/delete behavior in sync and async driver modes, metrics updates, concurrent readers during refresh, and copy versus internal-list exposure.
