<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaManager.java

## Purpose
`RouterQuotaManager` maintains the router's in-memory quota cache for mount-table paths. It supports lookup of applicable ancestor quotas, child path scans, parent quota scans, and cache updates/removals under a read/write lock.

## Important APIs, Types, and Functions
`getAll` returns all cached mount paths. `getQuotaUsage` returns the nearest quota-set usage for a path or ancestor. `getPaths` returns cached entries under a parent path. `getParentsContainingQuota` returns quota-set ancestors for a child. `put`, `updateQuota`, `remove`, and `clear` mutate the cache. `isQuotaSet` checks namespace, space, or per-storage-type quota values against `HdfsConstants.QUOTA_RESET`.

## Control Flow
Lookups use the sorted `TreeMap` to find exact, descendant, or floor entries. `getQuotaUsage` recurses toward parent paths until it finds a quota-set entry or reaches no parent. `getPaths` scans a `subMap` bounded by parent path and `Character.MAX_VALUE`, then filters with `DFSUtil.isParentEntry`. `updateQuota` preserves existing usage counters while replacing quota limits.

## State and Persistence Behavior
The only state is a process-local `TreeMap<String, RouterQuotaUsage>` guarded by `ReentrantReadWriteLock`. It is a cache of mount table quota information and aggregated usage; durable mount-table quota state is elsewhere.

## Dependencies and Integration Points
Dependencies include `RouterQuotaUsage`, `QuotaUsage`, `Path`, `HdfsConstants`, NameNode `Quota` storage-type iteration, and `DFSUtil.isParentEntry`. `RouterQuotaUpdateService` refreshes this cache and `Quota` uses it for enforcement.

## Risks
`getAll` returns the live `keySet` view after releasing the read lock, so concurrent mutation can affect callers. `getQuotaUsage` recursively reacquires the read lock, which works with `ReentrantReadWriteLock` but can be surprising. Cache correctness depends on periodic refresh and explicit updates from mount-table changes. Path prefix scans must be paired with `isParentEntry` to avoid false positives.

## Test Signals
Tests should cover exact and ancestor quota lookup, unset quota skipping, root and parent recursion, child path scans with prefix collisions, parent quota collection order, update preserving usage, stale removal/clear, per-storage-type quota detection, and concurrent read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaManager.java -->
