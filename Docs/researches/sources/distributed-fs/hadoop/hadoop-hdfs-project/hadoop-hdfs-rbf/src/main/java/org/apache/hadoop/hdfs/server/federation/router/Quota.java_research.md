# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/Quota.java

## Purpose
`Quota` implements router-side handling for `ClientProtocol#setQuota` and `getQuotaUsage` across federated mount points. It fans quota mutations out to relevant remote locations and aggregates remote quota usage into a federation-level result.

## Important APIs, Types, And Functions
- `setQuota` checks quota enablement, optionally blocks direct mount-entry quota changes, and delegates to `setQuotaInternal`.
- `setQuotaInternal` resolves quota remote locations and invokes `setQuota` concurrently on NameNodes using `RemoteMethod` and `RemoteParam`.
- `getEachQuotaUsage` resolves valid quota locations and invokes `getQuotaUsage` concurrently.
- `aggregateQuota` sums counts and storage consumption, chooses quota limits, handles unset quotas, and uses global mount-table quota for mount entries.
- `getGlobalQuota` walks parent quota records from `RouterQuotaManager` to resolve inherited quota values.
- `getValidQuotaLocations` filters duplicate parent-child destinations within the same nameservice to avoid double-counting.

## Control Flow
Writes require `OperationCategory.WRITE`, reads require `READ`, and both fail when router quota is disabled. If the quota manager has child paths under the requested path, those child mount locations are used; otherwise the direct path locations are used. Aggregation treats mount entries differently from non-mount paths: mount entries sum usage across children and take quota limits from global mount-table metadata, while non-mount paths take returned NameNode quota values unless any returned usage reports quota unset.

## State And Persistence
The class itself holds references to `Router`, `RouterRpcServer`, and `RouterRpcClient`. Persistent quota intent lives in mount-table `RouterQuotaUsage` records managed by `RouterQuotaManager` and state store; actual quota application is persisted on downstream NameNodes by remote `setQuota` calls.

## Dependencies And Integration Points
It integrates with `RouterRpcServer`, `RouterRpcClient`, `RouterQuotaManager`, `RouterQuotaUsage`, `RemoteLocation`, `RemoteMethod`, `RemoteParam`, HDFS quota constants, `StorageType`, and NameNode operation categories. `RouterAdminServer` calls it to synchronize quotas after mount table updates and removals.

## Risks And Edge Cases
Quota aggregation can be wrong if parent-child destination filtering misses a topology case or if remote locations change while quota synchronization is running. `setQuota` intentionally rejects direct quota changes on mount entries when `checkMountEntry` is true, but admin synchronization bypasses this check. If any non-mount remote usage reports quota unset, the aggregate quota limits are reset even when other locations have quotas. Storage-type quota handling must keep arrays aligned with `StorageType.values()`.

## Test Signals
`TestRouterQuota`, `TestDisableRouterQuota`, and quota sections of `TestRouterAdminCLI` cover enablement, set/clear quota, storage-type quotas, aggregation, and admin synchronization. Multi-destination router RPC tests add signal for remote fan-out and aggregation behavior.
