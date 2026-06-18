# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStats.java

## Purpose

`DatanodeStats` is the synchronized aggregate implementation behind `HeartbeatManager` statistics. It keeps cluster-wide totals for capacity, usage, cache, xceiver load, in-service counts, expired heartbeats, and per-storage-type statistics.

## Important APIs, Types, and State

Fields track `capacityTotal`, `capacityUsed`, `capacityUsedNonDfs`, `capacityRemaining`, `blockPoolUsed`, `xceiverCount`, `cacheCapacity`, `cacheUsed`, `nodesInService`, `nodesInServiceXceiverCount`, `nodesInServiceAvailableVolumeCount`, and `expiredHeartbeats`. `StorageTypeStatsMap` maintains an `EnumMap<StorageType, StorageTypeStats>` and separates adding/subtracting storage capacity from adding/subtracting node counts by storage type.

Package-private synchronized methods include `add(DatanodeDescriptor)`, `subtract(DatanodeDescriptor)`, getters, percent helpers, and `incrExpiredHeartbeats()`.

## Control Flow

`HeartbeatManager` subtracts a node's old contribution, updates descriptor heartbeat state through `BlockManager`, and adds the updated contribution. `add()` counts xceivers for all live nodes, counts capacity and cache fully only for in-service nodes, and counts cache capacity/used for decommission-in-progress or entering-maintenance nodes. Failed storages are excluded from storage-type stats. For each distinct storage type on a node, node count is updated once even if the node has multiple storages of that type.

## State and Persistence Behavior

All data is in-memory runtime aggregation and is recalculated incrementally. The class does not persist state or rebuild from disk itself; correctness depends on balanced `add()`/`subtract()` calls around liveness and heartbeat transitions.

## Dependencies and Integration Points

It depends on `DatanodeDescriptor`, `DatanodeStorageInfo`, `DatanodeStorage.State`, `StorageType`, `StorageTypeStats`, and `DFSUtilClient` percent helpers. `HeartbeatManager` is the sole implementation-facing owner.

## Risks and Edge Cases

The main risk is imbalance between `add()` and `subtract()`, which would corrupt totals. Administrative state affects accounting: decommissioned nodes do not contribute writable capacity, while decommissioning/entering-maintenance nodes still contribute cache stats. Storage-type node counts require distinct storage type tracking to avoid overcounting a node with multiple volumes of the same type.

## Test Signals

`TestHeartbeatHandling`, `TestBlockStatsMXBean`, `TestNamenodeCapacityReport`, `TestNameNodeMetrics`, and storage policy/placement tests should reveal incorrect aggregate totals. Unit-style tests should verify add/subtract symmetry and storage-type stats removal when the last in-service node of a type is subtracted.
