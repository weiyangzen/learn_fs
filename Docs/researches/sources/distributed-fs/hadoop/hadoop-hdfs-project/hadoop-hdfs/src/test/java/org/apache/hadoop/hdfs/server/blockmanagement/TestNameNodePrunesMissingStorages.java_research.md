# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestNameNodePrunesMissingStorages.java

## Purpose
`TestNameNodePrunesMissingStorages` verifies how the namenode handles datanode storage volumes that disappear, fail, or change storage IDs. It ensures empty missing storages are pruned, storages with blocks are protected until block state is handled, zombie storages are not created, renamed storage IDs are recognized, and unreported failed storages are eventually removed.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DataNode`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `StorageReport`, `DataNodeTestUtils.triggerBlockReport`, `FsVolumeReferences`, `FsVolumeSpi`, `StorageLocation`, `BlockManager`, and `DatanodeManager`. Helpers are `runTest` and `rewriteVersionFile`.

## Control Flow
`runTest` starts a one-datanode cluster with configurable storages, optionally creates a file, sends a fake heartbeat missing one storage, and checks whether the descriptor storage count is pruned. Other tests remove a storage directory by replacing it with a file, restart datanodes, and wait for the missing storage to disappear; edit a VERSION file to rename a storage ID and verify block-to-storage mapping updates; and restart a datanode with one of two data directories removed, checking failed-storage handling before pruning.

## State and Persistence Behavior
This file manipulates real MiniDFSCluster data directories and VERSION files. It tests persistent storage identity, in-memory descriptor storage arrays, block-to-storage maps, failed-storage flags, and heartbeat/block-report reconciliation.

## Dependencies and Integration Points
Integration points include datanode volume discovery, block reports, heartbeats, namenode storage pruning, filesystem block creation, and low-level disk directory mutation via `FileUtil` and VERSION-file rewriting.

## Risks and Edge Cases
Key risks include pruning a storage that still owns blocks, leaving zombie storage entries after restart, losing block mappings after storage ID rename, and failing to clear `areBlocksOnFailedStorage` before removing an unreported volume.

## Test Signals
Assertions check descriptor storage counts, block storage IDs, absence of removed storage IDs, failed-storage flag counts, `areBlocksOnFailedStorage` clearing after heartbeat check, and final storage-info count matching datanode configured storage locations.
