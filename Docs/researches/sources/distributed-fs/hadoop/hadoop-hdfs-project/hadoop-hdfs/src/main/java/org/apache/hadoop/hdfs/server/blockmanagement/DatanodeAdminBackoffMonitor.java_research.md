# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminBackoffMonitor.java

## Purpose

`DatanodeAdminBackoffMonitor` is the backoff-oriented decommission and maintenance monitor. It tracks datanodes leaving service without flooding the global replication queue, feeding only a bounded number of blocks into pending replication and advancing nodes to decommissioned or maintenance states once their blocks are sufficiently covered.

## Important APIs and types

- `outOfServiceNodeBlocks` maps tracked datanodes to blocks still needing processing; null means the node has not been scanned yet.
- `pendingRep` maps datanodes to blocks already queued for reconstruction and waiting to become sufficiently replicated.
- `processConf` reads `pendingRepLimit` and `blocksPerLock`.
- `run` is the monitor tick entry point.
- `processPendingNodes`, `processCancelledNodes`, `check`, `processMaintenanceNodes`, `processPendingReplication`, `moveBlocksToPending`, `scanDatanodeStorage`, and `processCompletedNodes` implement the state machine.
- `isBlockReplicatedOk` verifies and optionally schedules reconstruction.
- `BlockStats` accumulates open-file and out-of-service-only block metrics for datanode leaving-service status.

## Control flow

Each tick skips work if the namesystem is stopped, resets checked-block counters, takes the block-management write lock, processes cancellations before new pending nodes, optionally requeues unhealthy tracked nodes if concurrency is over the configured limit, and moves new pending nodes into the tracked map. The later `check` phase scans newly tracked nodes under read locks, expires maintenance nodes under the global write lock, prunes pending replication blocks that now satisfy redundancy, moves more blocks into pending replication up to the limit, rescans apparently complete nodes, and finally transitions healthy completed nodes.

Initial scans add all decommissioning-node blocks to the to-process map but immediately filter maintenance or rescan blocks through sufficiency checks. `moveBlocksToPending` creates per-node iterators and cycles them round-robin, dropping and retaking the global write lock after `blocksPerLock` blocks. `nextBlockAddedToPending` removes each processed block from the unprocessed map and queues it only if `isBlockReplicatedOk` says it still needs work. Pending replication processing updates per-node leaving-service metrics and removes blocks once sufficient.

## State and persistence behavior

All tracking state is in-memory and rebuilt from datanode/block state as nodes enter decommission or maintenance. It mutates datanode admin state through `dnAdmin`, datanode leaving-service metrics, and the block reconstruction queue. Persistent admin intent comes from host configuration and datanode admin state maintained elsewhere.

## Dependencies and integration points

It extends `DatanodeAdminMonitorBase` and uses `DatanodeAdminMonitorInterface`, `BlockManager`, `DatanodeAdminManager`, `FSNamesystem` locks, `DatanodeDescriptor`, `DatanodeStorageInfo`, `BlockInfo`, `BlockCollection`, `NumberReplicas`, `INodeFile`, low-redundancy queues, and maintenance/decommission configuration keys.

## Risks and edge cases

The monitor deliberately drops and reacquires locks, so it must re-check storage existence and tolerate concurrent block state changes. `getYetToBeProcessedCount` assumes every tracked value is non-null; the code scans null entries before calling it in normal flow. Orphan blocks return false from `isBlockReplicatedOk`, keeping them pending until invalidation paths handle them. Requeueing unhealthy nodes trades fairness and completion latency against concurrency limits.

## Test signals

Tests should cover invalid config fallback, cancellation-before-pending ordering, max concurrent tracked-node requeue, initial scan differences for decommission and maintenance, lock-yield block batching, pending limit enforcement, round-robin scheduling across nodes, maintenance expiry, final state transitions, open-file/out-of-service metrics, and orphan or unknown block handling.
