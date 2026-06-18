# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeDescriptor.java

## Purpose

`DatanodeDescriptor` extends client-visible `DatanodeInfo` with NameNode-private, ephemeral state: storage membership, block lists, heartbeat-derived capacity, admin status, queued commands, cache directives, volume failure state, and scheduling counters. It is the central in-memory object used by block management, heartbeat handling, block placement, decommission, maintenance, cache management, and reports.

## Important APIs, Types, and State

Nested `BlockTargetPair` represents a block plus target storages for transfer commands. `BlockQueue<E>` is a synchronized FIFO used for replication, EC replication, EC reconstruction, and lease recovery work. `CachedBlocksList` is an intrusive list for pending cached, cached, and pending uncached block state. `LeavingServiceStatus` stores decommission/maintenance counters: low-redundancy blocks, low-redundancy open files, open file IDs, out-of-service-only replicas, and start time.

Important fields include `storageMap` keyed by storage ID, per-node work queues (`replicateBlocks`, `ecBlocksToBeReplicated`, `ecBlocksToBeErasureCoded`, `recoverBlocks`, `invalidateBlocks`), approximate scheduled-block counters split into current/previous windows by storage type, `isAlive`, `needKeyUpdate`, `forceRegistration`, `disallowed`, `heartbeatedSinceRegistration`, `volumeFailures`, `volumeFailureSummary`, and `numVolumesAvailable`.

Key methods include `updateHeartbeat()`, `updateHeartbeatState()`, `updateStorageStats()`, `updateStorage(DatanodeStorage)`, `injectStorage()`, `pruneStorageMap()`, `getBlockIterator()`, `addBlockToBeReplicated()`, `addECBlockToBeReplicated()`, `addBlockToBeErasureCoded()`, `addBlockToBeRecovered()`, `addBlocksToBeInvalidated()`, command pollers, `chooseStorage4Block()`, scheduled-block increment/decrement, `updateRegInfo()`, `checkBlockReportReceived()`, and `dumpDatanode()`.

## Control Flow

Registration creates or updates the descriptor through `DatanodeManager`, then heartbeat processing calls `HeartbeatManager.updateHeartbeat()`, which delegates to `BlockManager.updateHeartbeat()` and ultimately descriptor heartbeat update methods. `updateStorageStats()` refreshes capacity, usage, cache, transfer count, volume failure state, storage heartbeats, available volumes, and stale/missing storage detection. If volume failures increased or a node has just registered, missing storages are marked `FAILED`; later `HeartbeatManager.heartbeatCheck()` removes blocks from failed storage.

Block work is enqueued by block-management logic and drained by `DatanodeManager.handleHeartbeat()`. Replication and EC replication queues produce `BlockCommand` transfer work; EC reconstruction queue produces `BlockECReconstructionCommand`; recovery queue produces `BlockRecoveryCommand`; invalidation set is drained into invalidate commands. Cache lists are protected by the FSNamesystem lock and converted to cache/uncache commands.

Storage membership is maintained carefully. `updateStorage()` adds new `DatanodeStorageInfo` objects, updates type/state for compatibility, and notifies `DFSTopologyNodeImpl` parents when storage types appear or disappear. `pruneStorageMap()` removes stale storage entries only when they have no associated blocks, preventing block-map loss before block reports reconcile.

## State and Persistence Behavior

This object is runtime state derived from datanode registration, heartbeats, block reports, and NameNode block maps. It is not persisted directly. Block list links live in `DatanodeStorageInfo` and `BlockInfo`; admin state is inherited from `DatanodeInfo`; command queues are transient and can be cleared on failover or safe-mode events. `markStaleAfterFailover()` on storages and `forceRegistration` prevent unsafe reuse of stale knowledge after failover or registration changes.

## Dependencies and Integration Points

`DatanodeDescriptor` integrates with nearly every block-management component: `DatanodeManager`, `HeartbeatManager`, `BlockManager`, `BlockPlacementPolicy`, `CacheReplicationMonitor`, `DatanodeStorageInfo`, `BlockInfo`, `BlockInfoStriped`, `BlockECReconstructionCommand`, `BlockRecoveryCommand`, and topology classes. It uses `StorageReport` and `VolumeFailureSummary` from datanode protocol messages and exposes storage reports for NameNode reports/MXBeans.

## Risks and Edge Cases

High-risk areas are synchronization boundaries and stale storage/block state. `storageMap` has explicit synchronization; block command queues use synchronized helper queues; invalidations synchronize on `invalidateBlocks`. Capacity accounting ignores `PROVIDED` storage for node-local totals. Duplicate mounts are counted once for non-DFS usage. A storage removed from heartbeats cannot be pruned while it still has blocks, so leaked stale storage entries are possible until block reports or block cleanup complete. Scheduled-block counters are approximate by design and roll every ten minutes.

## Test Signals

Direct tests include `TestDatanodeDescriptor`, `TestNameNodePrunesMissingStorages`, `TestHeartbeatHandling`, `TestBlockReportLease`, `TestProvidedStorageMap`, `TestBlockInfo`, and block placement tests. Integration signals include decommission/maintenance tests for `LeavingServiceStatus`, cache tests for cached lists, and EC tests that verify EC replication/reconstruction command queues.
