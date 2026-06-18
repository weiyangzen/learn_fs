
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerTestUtil.java

## Purpose
`BlockManagerTestUtil` is a package-local/public test utility for manipulating and inspecting `BlockManager`, `DatanodeManager`, `HeartbeatManager`, storage reports, reconstruction queues, corrupt replicas, decommission state, and test datanodes. It deliberately reaches into package-private fields and white-box state so tests can drive block-management internals without full cluster flows.

## Important APIs, Types, and Functions
The utility exposes queue and work helpers such as `setNodeReplicationLimit`, `updateState`, `getComputedDatanodeWork`, `computeInvalidationWork`, `computeAllPendingWork`, and `checkRedundancy`. It provides inspection helpers including `getDatanode`, `getBlockIterator`, `getReplicaInfo`, `getCorruptReplicas`, `getHeartbeatManager`, and `isDatanodeRemoved`. Datanode/storage factories include `getLocalDatanodeDescriptor`, overloaded `getDatanodeDescriptor`, `newDatanodeStorageInfo`, `updateStorage`, and `getStorageReportsForDatanode`.

## Control Flow and State
The methods typically acquire the appropriate `FSNamesystem` read or write lock using `RwLockMode.BM`, then query or mutate `BlockManager` state. Replica topology counts ignore decommissioned/decommissioning and corrupt replicas while counting racks and upgrade domains. Administrative helpers wake pending reconstruction timers, stop the redundancy thread, force startup safe mode via `Whitebox`, run decommission monitors, and simulate dead datanodes by marking descriptors dead then invoking heartbeat checks.

## Dependencies and Integration Points
This file is tightly integrated with HDFS block-management internals: `blocksMap`, `neededReconstruction`, `corruptReplicas`, `pendingReconstruction`, datanode admin monitors, and safe mode private fields. It also bridges tests to `DFSTestUtil`, `DatanodeStorage`, `StorageReport`, `NameNode`, and `DFSConfigKeys`.

## Risks and Test Signals
The utility is intentionally invasive; risks include lock-order mistakes, stale assumptions about private field names, and tests depending on exact internal queue behavior. Its value is high signal for tests that need deterministic block placement, corruption, decommission, heartbeat, or reconstruction behavior without waiting for background threads.
