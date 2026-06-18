# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CachePool.java

## Purpose
`CachePool` is the NameNode-internal representation of a path-based cache pool. It carries ownership, permission, quota-like limits, default directive parameters, current aggregate cache statistics, and an intrusive list of member `CacheDirective` objects.

## Important APIs and Types
`DirectiveList` extends `IntrusiveCollection<CacheDirective>` and binds directives back to their pool. Factory methods `createFromInfoAndDefaults` and `createFromInfo` transform client-facing `CachePoolInfo` into fully populated internal state. Getters/setters expose pool metadata, while `resetStatistics`, `addBytesNeeded`, `addBytesCached`, `addFilesNeeded`, and `addFilesCached` maintain counters.

## Control Flow
Pool creation fills missing owner and group from `NameNode.getRemoteUser`, default mode from `FsPermission.getCachePoolDefault`, default limit/replication/expiry from `CachePoolInfo`, and stores a defensive copy of permissions. `getEntry` performs read permission filtering: callers without `FsAction.READ` see only the pool name and empty stats.

## State and Persistence
The object itself is in-memory, but its fields are serialized by `CacheManager` into fsimage/edit-log representations. Statistics are recomputed by cache scans and are not independent durable records.

## Dependencies and Integration
`CachePool` is used by `CacheManager`, `CacheDirective`, `FSPermissionChecker`, `CachePoolInfo`, `CachePoolEntry`, and `CachePoolStats`. The intrusive directive list is a central integration point for efficient pool removal and directive enumeration.

## Risks and Test Signals
All access is documented as requiring the `FSNamesystem` lock; missing lock coverage can corrupt counters or intrusive list membership. Permission-filtered listing should be tested for both privileged and unprivileged users. Default-owner/group resolution is RPC-context sensitive. Tests should also cover statistic reset/rebuild and pool limit overrun calculations through `CacheManager`.
