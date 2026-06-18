<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/StorageTypeStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/StorageTypeStats.java

## Purpose

`StorageTypeStats` aggregates capacity and service counts for one HDFS storage type, including special accounting for shared `PROVIDED` storage.

## Important APIs and types

The class tracks total, used, non-DFS used, remaining, block-pool used, nodes in service, and aggregate xceiver count. Public getters expose raw capacities adjusted for `PROVIDED`, percentage helpers via `DFSUtilClient`, and node counts. Package methods add/subtract `DatanodeStorageInfo` and `DatanodeDescriptor` contributions.

## Control flow

`addStorage` and `subtractStorage` assert the storage type, always adjust used/non-DFS/block-pool usage, and include full capacity/remaining only for in-service nodes. Out-of-service nodes contribute DFS-used to total capacity instead. `addNode` and `subtractNode` update in-service node counts and xceiver totals. Getters divide capacity values by nodes in service for `PROVIDED` storage to avoid counting the same logical storage once per reporting DataNode.

## State and persistence behavior

State is in-memory cluster-statistics aggregation. It is rebuilt from DataNode heartbeats/storage reports and not persisted. The copy constructor copies capacity fields and node count but does not copy `storageType` or xceiver count, which is notable for consumers.

## Dependencies and integration points

It integrates with `DatanodeStats`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `StorageType`, provided-storage accounting, and JMX/metrics bean exposure through constructor properties.

## Risks and edge cases

`PROVIDED` division depends on a positive in-service node count. The copy constructor omission of `storageType` can change provided-storage getter behavior if used. Percent remaining uses `getPercentUsed` helper for remaining/total, which is semantically a percentage calculation despite the method name.

## Test signals

Tests should cover in-service and out-of-service accounting, add/subtract symmetry, provided-storage de-duplication, xceiver counts, copy constructor behavior, and percentage zero-total handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/StorageTypeStats.java -->
