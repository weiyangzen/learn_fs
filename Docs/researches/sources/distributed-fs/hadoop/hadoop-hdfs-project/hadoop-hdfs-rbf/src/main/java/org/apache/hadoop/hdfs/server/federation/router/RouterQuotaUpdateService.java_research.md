<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUpdateService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUpdateService.java

## Purpose
`RouterQuotaUpdateService` periodically reconciles router quota cache entries with mount-table quota definitions and actual downstream namespace usage. It also fixes remote quota settings that differ from the global router quota.

## Important APIs, Types, and Functions
The constructor validates that the router quota manager exists. `serviceInit` sets the periodic interval from `DFS_ROUTER_QUOTA_CACHE_UPDATE_INTERVAL`. `periodicInvoke` is the main refresh loop. `getMountTableStore`, `getMountTableEntries`, and `getQuotaSetMountTables` retrieve mount-table records and update/remove cache entries. `fixGlobalQuota` pushes global quota values to remote locations through `Quota.setQuotaInternal`. `generateNewQuota` combines old quota limits with current usage counters.

## Control Flow
Each tick loads quota-set mount tables, initializes a remote-usage map, then for each quota entry checks whether the federated source exists. Missing or zero-mtime destinations reset usage to zero while preserving limits. Existing entries ask the quota module for per-location usage, aggregate it, store remote usage for later consistency repair, update the quota manager, and write the new quota back to the `MountTable` record object. After scanning, every observed remote quota is compared to the global quota and corrected if namespace, space, or type quota differs.

## State and Persistence Behavior
The service mutates the in-memory `RouterQuotaManager` cache. It reads mount-table entries from the state store and calls downstream quota-setting APIs to repair remote quota values. It does not explicitly write modified `MountTable` objects back to the state store in this class; durable updates are expected from store/cache behavior or other quota paths.

## Dependencies and Integration Points
Dependencies include `Router`, `RouterRpcServer`, `RouterQuotaManager`, `MountTableStore`, `MountTable`, `Quota`, `RemoteLocation`, `QuotaUsage`, `RouterQuotaUsage`, `StorageType`, `HdfsFileStatus`, state-store request/response types, and async `syncReturn`.

## Risks
A broad catch logs errors and continues, which keeps the service alive but can leave stale quota cache. Existing-path detection treats `ret == null` or modification time zero as absent, which relies on router virtual mount-status conventions. `fixGlobalQuota` can issue writes to remote namespaces during a periodic refresh. Async mode depends on `syncReturn` matching the immediately preceding call. Cache `getAll` returns a live key view, so stale-path set construction must copy before mutations, which this code does.

## Test Signals
Tests should cover constructor failure without quota manager, interval config, mount-store lookup failure, stale cache removal, quota-set filtering, missing destination zero-usage generation, successful aggregate usage update, IO failure for one entry continuing others, global quota repair for namespace/space/type quotas, async `syncReturn` paths, and `generateNewQuota` preservation of limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUpdateService.java -->
