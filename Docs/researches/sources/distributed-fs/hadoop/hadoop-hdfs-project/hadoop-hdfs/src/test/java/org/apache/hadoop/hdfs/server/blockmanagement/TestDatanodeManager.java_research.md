# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeManager.java

## Purpose
`TestDatanodeManager` is a broad unit/integration-style test suite for datanode registration bookkeeping, host maps, software-version counts, topology resolution, located-block sorting, include-list reports, heartbeat reconstruction task allocation, network-topology implementation selection, and reconstruction task count computation.

## Important APIs, Types, and Functions
Important types include `DatanodeManager`, `DatanodeRegistration`, `DatanodeDescriptor`, `HostFileManager`, `HostSet`, `LocatedBlock`, `DatanodeInfoWithStorage`, `StorageType`, `DFSNetworkTopology`, `NetworkTopology`, `BlockCommand`, and `BlockECReconstructionCommand`. Helpers include `mockDatanodeManager`, `entry`, `HelperFunction`, `verifyPendingRecoveryTasks`, and `verifyComputeReconstructedTaskNum`. The inner `MyResolver` simulates unresolved topology and `MockDfsNetworkTopology` verifies configurable topology class loading.

## Control Flow
Registration tests create mocked namesystems and registrations, register or re-register nodes, remove nodes, and validate software-version maps and host maps. Sorting tests register synthetic datanodes, optionally configure topology scripts, create `LocatedBlock` arrays with storage IDs/types, and call `sortLocatedBlocks` for clients inside and outside the cluster. Load and storage-type tests enable read preference flags and check sorted order. Include-list tests refresh `HostFileManager` include sets and verify reports. Heartbeat tests mock queue lengths and command methods to verify task splitting and command creation.

## State and Persistence Behavior
State is mostly in-memory manager state: `datanodeMap`, host-to-node mappings, software-version counters, topology tree membership, host include/exclude sets, datanode admin state, xceiver counts, storage types, and per-node pending reconstruction queues. No persistent namespace is required.

## Dependencies and Integration Points
The suite integrates mocked `BlockManager` dependencies, `BlockReportLeaseManager`, topology script resources, AssertJ/JUnit assertions, white-box host manager injection, and heartbeat command generation. It is a key regression surface for client block-location ordering and namenode datanode report behavior.

## Risks and Edge Cases
Covered risks include stale software-version counts after re-registration, old IP/hostname mappings remaining visible, unresolved topology acceptance when configured to reject, broken topology scripts, storage ID/type misalignment after sorting, decommissioned nodes appearing before healthy nodes, dead reader locality, equal-distance randomization, provided storage ordering, include-list empty semantics, and excessive transfer counts suppressing tasks.

## Test Signals
Signals include exact version maps, null/non-null host lookups, thrown `UnresolvedTopologyException`, sorted datanode/storage alignment, expected first and last locations, dead-node fallback locality, randomized equal-distance coverage, report list sizes, command classes and counts from `handleHeartbeat`, topology implementation classes, and captured reconstruction task counts being non-positive once in-progress transfers exceed limits.
