# Research: subset-b-007536

This grouped report covers the exact source files assigned to `subset-b-007536`. Each file section preserves the source path in its title and is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestKeyManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestKeyManager.java

## Purpose
`TestKeyManager` validates HDFS balancer-side block-token key management, especially the generation, caching, expiry, clearing, and refresh behavior of `KeyManager` data encryption keys. The test class is focused on security-sensitive data-transfer encryption paths where the balancer asks the NameNode for exported block keys through `NamenodeProtocol`.

## Important APIs, Types, and Functions
The central production types are `KeyManager`, `BlockTokenSecretManager`, `DataEncryptionKey`, `ExportedBlockKeys`, and `NamenodeProtocol`. The tests use `HdfsConfiguration` with `DFS_ENCRYPT_DATA_TRANSFER_KEY` and `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY` enabled. `FakeTimer` and `Whitebox.setInternalState` replace internal timers in both `KeyManager` and its `BlockTokenSecretManager` so expiry behavior is deterministic. `createNamenode` builds a dynamic proxy for `NamenodeProtocol`, supporting only `getBlockKeys` and optionally counting calls.

## Control Flow and State
`testNewDataEncryptionKey` exports keys from a `BlockTokenSecretManager`, constructs a `KeyManager`, gets a DEK, advances fake time beyond the key interval, then checks that `newDataEncryptionKey` returns a new non-expired key. `testClearDataEncryptionKey` proves the unexpired DEK is cached by identity, then calls `clearDataEncryptionKey` and verifies a replacement object is generated. `testUpdateBlockKeysThenClearDataEncryptionKey` combines `updateBlockKeys` with cache clearing and verifies the NameNode key fetch count reaches two.

## Dependencies and Integration Points
This file integrates balancer key handling with HDFS configuration keys, block-token secret manager exports, NameNode protocol fetches, and test-only reflection utilities. It does not start a MiniDFSCluster; it isolates the protocol dependency with Mockito or a dynamic proxy.

## Risks and Test Signals
The main risks are stale encryption-key reuse, expired DEK issuance after clock advancement, and accidental loss of NameNode key refresh behavior when the cache is cleared. Strong signals are identity assertions (`assertSame`/`assertNotSame`), fake-time expiry assertions, and proxy call counting. Reflection into private timers is brittle but appropriate for deterministic expiry testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestKeyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/BaseReplicationPolicyTest.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/BaseReplicationPolicyTest.java

## Purpose
`BaseReplicationPolicyTest` is an abstract fixture for block-placement-policy tests. It constructs a lightweight NameNode with a configurable `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY`, installs synthetic datanodes into the `NetworkTopology` and heartbeat manager, and exposes helper methods for subclasses to call `BlockPlacementPolicy.chooseTarget`.

## Important APIs, Types, and Functions
Important fields include `cluster`, `dataNodes`, `storages`, `namenode`, `dnManager`, `replicator`, and `striptedPolicy`. Subclasses implement `getDatanodeDescriptors(Configuration)`. `setupCluster` formats and starts a local NameNode using `DFSTestUtil.formatNameNode`, wires the selected placement policy, populates `NetworkTopology`, and initializes heartbeat stats. `updateHeartbeatWithUsage` writes storage utilization through `DatanodeStorageInfo.setUtilizationForTesting` and updates `HeartbeatManager`. Several overloaded `chooseTarget` helpers normalize writer, chosen-node, and excluded-node inputs.

## Control Flow and State
The setup path creates a fresh `HdfsConfiguration`, sets local NameNode URI and dirs, selects the policy class from `blockPlacementPolicy`, enables stale-node avoidance, then adds every synthetic datanode to both topology and heartbeat tracking. The fixture gives each datanode enough remaining capacity for writes by default. `tearDown` stops the NameNode after each test.

## Dependencies and Integration Points
The class depends on the NameNode/block manager stack, `DFSTestUtil`, `TestBlockStoragePolicy.DEFAULT_STORAGE_POLICY`, `PathUtils`, and `GenericTestUtils` log configuration. It exposes both replicated and striped placement policy handles, so subclasses can test policy variants without repeating cluster bootstrap.

## Risks and Test Signals
Risks include fixture state leaking through the NameNode or static temp dirs, spelling drift around `striptedPolicy`, and synthetic datanodes missing heartbeat/topology registration. Test signal is indirect: subclasses rely on this fixture to make placement decisions realistic enough to include capacity, rack, stale-node, and storage-policy inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/BaseReplicationPolicyTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerTestUtil.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockManagerTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceBPPBalanceLocal.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceBPPBalanceLocal.java

## Purpose
This class tests `AvailableSpaceBlockPlacementPolicy` when local-node balancing is enabled. It verifies that a lightly used writer-local datanode is always selected for a single replica, while a heavily used writer-local datanode loses preference often enough to favor less-loaded nodes.

## Important APIs, Types, and Functions
Key configuration uses `DFS_NAMENODE_AVAILABLE_SPACE_BLOCK_PLACEMENT_POLICY_BALANCED_SPACE_PREFERENCE_FRACTION_KEY` set to `0.6f`, `DFS_NAMENODE_AVAILABLE_SPACE_BLOCK_PLACEMENT_POLICY_BALANCE_LOCAL_NODE_KEY` set to true, and `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` set to `AvailableSpaceBlockPlacementPolicy`. `setupCluster` creates two racks with three nodes each through `DFSTestUtil.createDatanodeStorageInfos`. `setupDataNodeCapacity` alternates 100 percent remaining and 25 percent remaining nodes.

## Control Flow and State
The static `@BeforeAll` setup formats and starts a NameNode, installs synthetic datanodes in network topology, and sets per-storage utilization through `updateHeartbeatWithUsage`. `testChooseLocalNode` loops 10,000 times with a zero-usage local node and expects that local node every time. `testChooseLocalNodeWithLocalNodeLoaded` loops 10,000 times with a 75-percent-used local node and asserts the non-local path wins more often than the local path.

## Dependencies and Integration Points
The tests integrate NameNode placement policy wiring, storage reports from `BlockManagerTestUtil`, rack topology, `TestBlockStoragePolicy.DEFAULT_STORAGE_POLICY`, and the policy's probabilistic selection algorithm.

## Risks and Test Signals
Because these are statistical tests, probability drift or random changes can create flakiness. The chosen thresholds are broad for the loaded-local-node case but exact for the unloaded-local-node case. Strong signal is that the balance-local feature does not erase locality when the writer is healthy and does not over-prefer locality when the writer is comparatively full.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceBPPBalanceLocal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceBlockPlacementPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceBlockPlacementPolicy.java

## Purpose
`TestAvailableSpaceBlockPlacementPolicy` validates the available-space-aware replicated block placement policy. It checks that the policy can be installed by configuration, favors nodes with more remaining space at the expected probability, handles fully excluded candidate sets, and compares datanodes using tolerance rules.

## Important APIs, Types, and Functions
The setup uses four racks, five nodes per rack, three replicas, and 10,000 placement trials. It sets `DFS_NAMENODE_AVAILABLE_SPACE_BLOCK_PLACEMENT_POLICY_BALANCED_SPACE_PREFERENCE_FRACTION_KEY` to `0.6f`, tolerance limit to `93`, and policy class to `AvailableSpaceBlockPlacementPolicy`. Helpers update `DatanodeStorageInfo` utilization and synthetic heartbeats. Tests exercise `chooseTarget`, `chooseDataNode`, and `compareDataNode`.

## Control Flow and State
`setupCluster` creates 20 datanodes spread across racks, starts a local NameNode, installs all nodes into topology, and alternates 100-percent and 50-percent remaining capacity. `testChooseTarget` repeatedly chooses three targets and computes the fraction of selected nodes whose remaining percent is above 60, expecting about 52-55 percent. `testChooseDataNode` excludes all nodes to verify no NPE. `testChooseSimilarDataNode` and `testCompareDataNode` create ad hoc datanode sets with precise used-percent values to verify tolerance equality and ordering.

## Dependencies and Integration Points
This file touches the NameNode block manager, `NetworkTopology`, `DFSTestUtil`, storage reports from `BlockManagerTestUtil`, and storage policy selection. It integrates directly with the policy's comparison logic as well as the higher-level `chooseTarget` API.

## Risks and Test Signals
Statistical assertions can fail if random selection logic changes or if capacity percentages are calculated differently. The comparison tests provide deterministic signal for tolerance-limit behavior, while the replacement and excluded-node tests catch configuration and null-handling regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceBlockPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceRackFaultTolerantBPP.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceRackFaultTolerantBPP.java

## Purpose
This class tests `AvailableSpaceRackFaultTolerantBlockPlacementPolicy`, combining available-space preference with rack-fault-tolerant target spread. It verifies policy replacement, probabilistic preference for less-used nodes, null-safe exclusion handling, maximum rack distribution, and comparison of similarly used datanodes.

## Important APIs, Types, and Functions
The configuration sets `DFS_NAMENODE_AVAILABLE_SPACE_RACK_FAULT_TOLERANT_BLOCK_PLACEMENT_POLICY_BALANCED_SPACE_PREFERENCE_FRACTION_KEY` to `0.6f` and installs `AvailableSpaceRackFaultTolerantBlockPlacementPolicy`. `setupCluster` builds four racks with five datanodes each. `testMaxRackAllocation` checks that a three-replica placement uses three distinct racks.

## Control Flow and State
The setup mirrors the non-rack-fault-tolerant available-space test: a local NameNode is formatted and started, all synthetic datanodes are added to topology, and capacity alternates between 100-percent and 50-percent remaining. `testChooseTarget` runs 10,000 target selections and expects the high-remaining selections to land between 52 and 55 percent. `testChooseDataNode` excludes all known nodes and fails only on NPE. `testChooseSimilarDataNode` creates three custom nodes and verifies tolerance comparison results.

## Dependencies and Integration Points
The tests integrate rack topology, block placement policy configuration, `DFSTestUtil`, `BlockManagerTestUtil.getStorageReportsForDatanode`, and default storage policy. The policy is accessed both through the `BlockPlacementPolicy` interface and via its concrete `chooseDataNode` and `compareDataNode` methods.

## Risks and Test Signals
The statistical target-selection assertion is sensitive to random distribution and policy probability changes. The rack allocation test provides a direct signal that the rack-fault-tolerant policy spreads replicas across racks, while null-handling catches failures in all-excluded candidate paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestAvailableSpaceRackFaultTolerantBPP.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockInfo.java

## Purpose
`TestBlockInfo` validates contiguous `BlockInfo` behavior used by `BlocksMap` and datanode storage block lists. It focuses on deletion state, storage addition and replacement, provided-storage detection, argument validation, and `DatanodeStorageInfo` block-list reordering.

## Important APIs, Types, and Functions
The tests use `BlockInfoContiguous`, `BlockCollection`, `DatanodeStorageInfo`, `DatanodeStorage`, `StorageType`, `GenerationStamp`, and `DatanodeStorageInfo.AddBlockResult`. Mockito supplies mock storages and datanode descriptors for storage-type scenarios. `testBlockListMoveToHead` exercises `DatanodeStorageInfo.moveBlockToHead`, `getBlockListHeadForTesting`, `findStorageInfo`, and `getNext`.

## Control Flow and State
`testIsDeleted` toggles `blockCollectionId` from a valid id to `INVALID_INODE_ID`. `testAddStorage` and provided-storage tests verify storage slots and `isProvided`. `testReplaceStorage` adds ten blocks to one storage, then adds one block to another storage on the same datanode and expects replacement semantics rather than an `ADDED` result. `testAddStorageWithDifferentBlock` expects `IllegalArgumentException` for mismatched block IDs. The block-list test builds a ten-block linked list, moves every block to the head, validates order, then performs random head moves.

## Dependencies and Integration Points
This is a unit-style test with `DFSTestUtil` factories and direct block/storage APIs. It probes data structures consumed by block reports, storage maps, provided-storage support, and datanode descriptor iteration.

## Risks and Test Signals
Important risks are broken linked-list invariants, incorrect storage replacement, accepting mismatched block reports, and failing to mark provided-backed blocks. The strongest test signal is structural: iterator length, head identity, and next pointers must remain consistent after deterministic and random moves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockInfoStriped.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockInfoStriped.java

## Purpose
`TestBlockInfoStriped` validates erasure-coded `BlockInfoStriped` storage indexing, removal, serialization, block lookup, and input validation across all configured EC policies. It is parameterized over `StripedFileTestUtil.getECPolicies()`.

## Important APIs, Types, and Functions
The class uses `BlockInfoStriped`, `ErasureCodingPolicy`, `Block`, `DatanodeStorageInfo`, `MiniDFSCluster`, `DistributedFileSystem`, `DFSck`, and `Whitebox` inspection of the private `indices` array. `createReportedBlocks` generates internal block IDs by adding offsets to a negative base block-group ID. Tests exercise `addStorage`, `removeStorage`, `findStorageInfo`, `numNodes`, `getCapacity`, `write`, and validation of mismatched block types or block groups.

## Control Flow and State
`testAddStorage` adds even-indexed then odd-indexed storages, checks capacity and indices, re-adds the same reports, then adds duplicate internal blocks from additional storages to force capacity growth. `testRemoveStorage` removes selected storages, checks `-1` index markers, adds duplicate reports into freed and extended slots, then removes those duplicates. `testGetBlockInfo` builds a MiniDFSCluster, writes an EC file, removes one storage from the NameNode's stored block info, and runs `dfsck -blockId` to ensure output does not contain `null`. `testWrite` verifies serialized bytes match raw `Block` fields.

## Dependencies and Integration Points
The file integrates EC policy definitions, NameNode block manager storage lookup, `DFSck`, MiniDFSCluster EC setup, and `DFSTestUtil` block discovery. It touches both pure in-memory `BlockInfoStriped` behavior and an end-to-end NameNode/DFSck reporting path.

## Risks and Test Signals
Risks include stale `indices` entries after removal, duplicate internal block miscounting, null storage output in diagnostics, and accidental acceptance of contiguous or different-group blocks. Test signals are strong because they assert exact index arrays, capacity behavior, serialization bytes, and expected exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockInfoStriped.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockManager.java

## Purpose
`TestBlockManager` is a broad integration and white-box test suite for HDFS block-management behavior. It covers rack-aware reconstruction, decommission and maintenance accounting, EC reconstruction source selection, safe-mode block-report processing, incremental block report queuing and batching, storage capacity and corruption handling, metasave output, placement policy satisfaction, invalidation semantics, datanode restart reports, and excess-redundancy timeout recovery.

## Important APIs, Types, and Functions
Core tested types include `BlockManager`, `DatanodeManager`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `BlockInfoContiguous`, `BlockInfoStriped`, `BlockReconstructionWork`, `NumberReplicas`, `LowRedundancyBlocks`, `InvalidateBlocks`, `BlockPlacementStatus`, and `CorruptReplicasMap`. The setup creates a mocked `FSNamesystem` with BM and global locks reported as held, an HA context that populates reconstruction queues, a real `BlockManager`, mocked `CacheManager`, six synthetic datanodes split across two racks, and helper methods such as `addNodes`, `removeNode`, `addBlockOnNodes`, `scheduleSingleReplication`, `fulfillPipeline`, `addBlockToBM`, `addUcBlockToBM`, and `addEcBlockToBM`.

## Control Flow and State
Early tests repeatedly schedule reconstruction for blocks placed on selected racks and assert source plus target rack selection under normal, partial decommission, full decommission, rack decommission, and single-rack cases. EC tests build striped block groups with duplicate internal blocks, busy datanodes, decommissioning sources, and missing blocks to validate source selection and skip decisions. Safe-mode block-report tests simulate first full reports, incremental-before-full reports, provided storage report counting, and under-construction blocks that should not enter needed reconstruction. MiniDFSCluster tests cover append pipeline updates, stale storage corrupt-replica deletion, remaining-capacity admission failure, queued block operations, async IBR metrics, failed/corrupt storage filtering in located blocks, EC placement satisfaction across changing rack counts, block report after datanode restart, NO_ACK invalidation, and timed-out excess replica deletion after datanode restart.

## State and Persistence Behavior
The class mutates `blocksMap`, `neededReconstruction`, `pendingReconstruction`, corrupt replica maps, excess redundancy maps, invalidate queues, datanode heartbeat state, and temporary NameNode/DataNode storage directories. It also writes temporary metasave files named `test.log` for output assertions and deletes them in finally blocks. Cluster tests persist real replicas in MiniDFSCluster directories, then remove, corrupt, or restart datanodes to verify NameNode state reconciliation.

## Dependencies and Integration Points
Dependencies span HDFS client APIs, MiniDFSCluster, EC policies, block reports, datanode fault injection, metrics, NameNodeAdapter, DataNodeTestUtils, `DFSOutputStream`, `DFSck`-adjacent block location paths, and Mockito spies. It is one of the main integration points between block placement, reconstruction scheduling, report processing, metrics, and administrative diagnostics.

## Risks and Test Signals
Risks are broad: probabilistic target selection, timeout-sensitive concurrency, stale mocks, leaked fault injectors, and filesystem cleanup around real cluster tests. High-value signals include exact pending reconstruction pipeline shape, queue length and metric assertions, located-block exclusion of failed/corrupt storage, metasave string contracts, EC placement status changes after rack expansion, deletion-report suppression for NO_ACK blocks, and excess-block retry after timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockManagerSafeMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockManagerSafeMode.java

## Purpose
`TestBlockManagerSafeMode` is a white-box unit suite for `BlockManagerSafeMode`. It validates the safe-mode state machine, safe-block counters, extension timing, datanode thresholds, future-generation-stamp handling, extension configuration parsing, monitor interval logging, and user-facing safe-mode tips.

## Important APIs, Types, and Functions
The test uses `BlockManagerSafeMode.BMSafeModeStatus` values `OFF`, `PENDING_THRESHOLD`, and `EXTENSION`; mocked `FSNamesystem`; a spied `BlockManager`; a spied `DatanodeManager`; and `Whitebox` access to private `status`, `blockSafe`, `datanodeThreshold`, and `extension`. Helpers include `setSafeModeStatus`, `setBlockSafe`, `setDatanodeThreshold`, `getblockSafe`, `waitForExtensionPeriod`, `injectBlocksWithFugureGS`, and mock setup for decrement paths.

## Control Flow and State
`setupMockCluster` configures safe-mode threshold, extension, and minimum datanodes, initializes NameNode metrics, and stubs locks/running state. Initialization tests assert `activate` moves status to `PENDING_THRESHOLD`. `testCheckSafeMode1` through `testCheckSafeMode10` cover threshold pending, extension entry, zero-extension exit, active-transition blocking, monitor-driven exit, zero total blocks, and valid/invalid monitor interval logging. Counter tests increment and decrement contiguous and striped safe blocks, ensuring counters cap at threshold and become no-ops after leaving safe mode. Datanode threshold tests vary live-node counts and configured minimums. Future-GS tests verify normal exit is blocked, force exit clears bytes-in-future, and safe-mode tips include loss warnings.

## Dependencies and Integration Points
The file integrates with `DFSConfigKeys`, `NameNode.initMetrics`, `GenericTestUtils.waitFor`, `LogCapturer`, `BlockReportReplica`, `NumberReplicas`, and lock-mode-aware FSNamesystem mocks. It intentionally avoids MiniDFSCluster and points readers to broader safe-mode integration suites.

## Risks and Test Signals
Risks include timing flakiness in monitor-thread tests, brittle private-field reflection, and typoed helper names that still compile but obscure intent. Test signals are precise for state transitions, counter boundaries, extension parsing of raw milliseconds and time suffixes, and safe-mode user messages under normal, datanode-threshold, and future-GS conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockManagerSafeMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementPolicyDebugLoggingBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementPolicyDebugLoggingBuilder.java

## Purpose
This test verifies that `BlockPlacementPolicyDefault.chooseRandom` remains stable when block-placement logging level changes dynamically during selection. It targets debug logging builder behavior rather than placement correctness.

## Important APIs, Types, and Functions
The class extends `BaseReplicationPolicyTest` and selects `BlockPlacementPolicyDefault`. `getDatanodeDescriptors` creates three storages across hierarchical rack paths. The test spies the `replicator`, changes `BlockPlacementPolicy.LOG` from INFO to DEBUG inside mocked `chooseDataNode` answers, and calls `chooseRandom` with a disk storage-type requirement.

## Control Flow and State
`testChooseRandomDynamicallyChangeLogger` seeds `results` with all three storages, creates an empty excluded set, and installs two `doAnswer` hooks: one for `chooseDataNode(scope, excluded)` and one for `chooseDataNode(scope, excluded, StorageType.DISK)`. Each hook changes the logger to DEBUG and returns the first datanode. The final `chooseRandom` call exercises logging code that may have built conditional debug state before or during selection.

## Dependencies and Integration Points
The test relies on the base fixture's NameNode, topology, heartbeat, and default policy setup. It uses Mockito spying, `GenericTestUtils.setLogLevel`, `StorageType`, and `EnumMap` storage-type quotas.

## Risks and Test Signals
The main regression risk is logging code assuming a stable log level and throwing when debug becomes enabled mid-operation. There are no explicit assertions; the signal is absence of exception. That makes the test narrow but important for a previously fragile debug/logging path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementPolicyDebugLoggingBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementStatusDefault.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementStatusDefault.java

## Purpose
`TestBlockPlacementStatusDefault` is a compact unit test for `BlockPlacementStatusDefault`, specifically policy satisfaction and `getAdditionalReplicasRequired` calculations based on current rack count, expected rack count, and total cluster racks.

## Important APIs, Types, and Functions
The only production type under test is `BlockPlacementStatusDefault`. The constructor inputs represent current racks, required racks, and cluster racks. Assertions use `isPlacementPolicySatisfied` and `getAdditionalReplicasRequired`.

## Control Flow and State
The single test method evaluates four scenarios: current racks equal expected racks, current racks below expected racks, current racks above expected racks, and current racks below expected racks when the cluster itself has only one rack. The final case is important because placement should be considered satisfied when the cluster cannot supply the nominal rack diversity.

## Dependencies and Integration Points
This is a pure unit test with no HDFS cluster, no storage fixtures, and no external state. It supports the higher-level block placement and reconstruction tests by checking the status object's arithmetic contract.

## Risks and Test Signals
Risks are small but central: incorrect additional-replica counts can cause unnecessary reconstruction or false placement satisfaction failures. The direct assertions are high signal for rack-count arithmetic and the single-rack-cluster exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementStatusDefault.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementStatusWithUpgradeDomain.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementStatusWithUpgradeDomain.java

## Purpose
This class tests `BlockPlacementStatusWithUpgradeDomain`, which layers upgrade-domain diversity requirements on top of a parent `BlockPlacementStatusDefault`. It verifies satisfaction and additional-replica calculations for different domain counts, replication factors, and upgrade-domain factors.

## Important APIs, Types, and Functions
The tests use a mocked `BlockPlacementStatusDefault` parent and a mutable `Set<String>` of upgrade domains. `setup` initializes domains `1`, `2`, and `3` and defaults the parent policy to satisfied. Each scenario constructs `BlockPlacementStatusWithUpgradeDomain` and asserts `isPlacementPolicySatisfied` plus `getAdditionalReplicasRequired`.

## Control Flow and State
`testIsPolicySatisfiedParentFalse` confirms that a failing parent policy dominates even if domain counts are adequate. `testIsPolicySatisfiedAllEqual` covers the ideal case of three domains, three replicas, and factor three. `testIsPolicySatisfiedSmallDomains` differentiates cases where domain count is below replicas but still meets or does not meet the upgrade-domain factor. `testIsPolicySatisfiedSmallReplicas` covers replication factor one and two. `testPolicyIsNotSatisfiedInsufficientDomains` checks additional counts for one or two domains under replication factors two or three.

## Dependencies and Integration Points
This is pure policy-status logic with Mockito for the parent status. It informs reconstruction and block-placement validation layers that combine rack and upgrade-domain constraints.

## Risks and Test Signals
Risks include double-counting parent and domain deficits, over-requiring domains for low replication factors, or ignoring the upgrade-domain factor. The tests give direct arithmetic signal for all those boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockPlacementStatusWithUpgradeDomain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockReportLease.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockReportLease.java

## Purpose
`TestBlockReportLease` validates NameNode full block report lease enforcement and compatibility behavior. It ensures leases are checked once per block-report request, expired leases can throw or be tolerated based on configuration, unregistered datanodes receive registration commands, and incomplete first block reports in safe mode are counted correctly per storage.

## Important APIs, Types, and Functions
The tests use `MiniDFSCluster`, `NamenodeProtocols.sendHeartbeat`, `NamenodeProtocols.blockReport`, `BlockReportContext`, `StorageBlockReport`, `BlockListAsLongs`, `BlockReportLeaseManager`, `InvalidBlockReportLeaseException`, `FinalizeCommand`, and `RegisterCommand`. `createReports` constructs fake block-list payloads for each `DatanodeStorage`. Mockito spies `BlockManager`, and `GenericTestUtils.DelayAnswer` blocks `processReport` to create lease-removal races.

## Control Flow and State
`testCheckBlockReportLease` obtains a lease from heartbeat, starts a block report, waits until `processReport`, removes the lease, then allows processing to complete and expects a `FinalizeCommand`, proving lease validation is request-level rather than per-storage. `testExceptionThrownWhenFBRLeaseExpired` removes the lease before reporting and expects `InvalidBlockReportLeaseException`. `testNoExceptionWhenRejectInvalidLeaseDisabled` sets `DFS_BLOCKREPORT_REJECT_INVALID_LEASE_KEY` false and expects no exception for an invalid lease. `testCheckBlockReportLeaseWhenDnUnregister` removes the datanode from the map and expects `RegisterCommand`. `testFirstIncompleteBlockReport` enters safe mode and sends per-storage reports, simulating a first report failure for the first storage and verifying block report count deltas.

## Dependencies and Integration Points
The file exercises DataNode registration, heartbeat lease issuance, NameNode RPC block-report handling, block manager report processing, safe mode, and rolling-upgrade compatibility configuration.

## Risks and Test Signals
Risks include deadlocks from delayed report processing, executor leaks, and synthetic block-list construction drift. The test signal is strong around lease boundary behavior, especially that mid-request lease removal does not partially reject batched storage reports, while pre-request expiration is handled according to config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockReportLease.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockReportRateLimiting.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockReportRateLimiting.java

## Purpose
`TestBlockReportRateLimiting` verifies full block report lease rate limiting during DataNode startup and lease expiration recovery. It ensures only the configured number of full block report leases is active and that a failed/stopped datanode does not permanently block another datanode after lease expiry.

## Important APIs, Types, and Functions
The test configures `DFS_NAMENODE_MAX_FULL_BLOCK_REPORT_LEASES` and `DFS_NAMENODE_FULL_BLOCK_REPORT_LEASE_LENGTH_MS`. It overrides the static `BlockManagerFaultInjector.instance` to observe `incomingBlockReportRpc`, `requestBlockReportLease`, and `removeBlockReportLease`. Synchronization uses `Semaphore`, `AtomicReference`, `HashSet<DatanodeID>`, and `GenericTestUtils.waitFor`.

## Control Flow and State
`testRateLimitingDuringDataNodeStartup` sets the maximum leases to one, starts five datanodes, and uses the fault injector to block incoming full reports until the test releases a semaphore one datanode at a time. It tracks expected and actual datanode IDs and fails if a lease ID is zero or more than one lease is issued simultaneously. `testLeaseExpiration` starts a two-node cluster with a 100 ms lease, records the first node granted a lease, stops it, injects an IOException for its report, and waits for the other node to successfully send a leased full report after expiration.

## Dependencies and Integration Points
This file integrates the NameNode full block report lease manager, MiniDFSCluster datanode startup, fault injection hooks, and block report RPC contexts. `@AfterEach` restores a normal fault injector to avoid cross-test contamination.

## Risks and Test Signals
The tests are timing and concurrency sensitive. They mitigate this with semaphores, atomics, and bounded waits. Strong signals are the absence of zero-lease bypass reports, exact one-at-a-time lease issuance, and successful progress after the first lessee fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockReportRateLimiting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockStatsMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockStatsMXBean.java

## Purpose
`TestBlockStatsMXBean` validates the NameNode `BlockStatsMXBean` and underlying storage-type statistics. It checks per-storage-type node counts, JMX serialization, failed-storage removal and restoration, per-storage-type xceiver load, and percent fields exposed through JMX.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster` with seven datanodes and mixed storage types: RAM_DISK on all nodes, DISK on three, ARCHIVE on three, and NVDIMM on one. It reads stats through `BlockManager.getStorageTypeStats`, `HeartbeatManager.getStorageTypeStats`, and `/jmx` JSON. It uses `StorageTypeStats`, `DataNodeTestUtils.injectDataDirFailure`, `restoreDataDirFromFailure`, `DistributedFileSystem` storage policies, and `GenericTestUtils.waitFor`.

## Control Flow and State
`setup` builds the mixed-storage cluster with disk-check gap set to zero. `testStorageTypeStats` checks in-service node counts for RAM_DISK, DISK, ARCHIVE, and NVDIMM. `testStorageTypeStatsJMX` fetches `/jmx`, locates `Hadoop:service=NameNode,name=BlockStats`, and verifies serialized storage-type entries. `testStorageTypeStatsWhenStorageFailed` creates a file, injects volume failures into selected storage dirs, expects a write failure when DISK is unavailable, waits for heartbeat-driven stats removal, restores volumes, restarts datanodes, and verifies counts recover. `testStorageTypeLoad` opens HOT and COLD policy files, waits for DISK and ARCHIVE xceiver counts, and verifies total load. `testStorageTypePercentJMX` confirms percent-used fields are present in JMX output.

## Dependencies and Integration Points
The file integrates NameNode block stats, heartbeat aggregation, DataNode volume failure simulation, storage policies, Jetty JMX JSON output, and platform assumptions that skip failure injection on Windows.

## Risks and Test Signals
Risks include sleep-based heartbeat waits, platform-specific volume failure behavior, JSON schema drift, and cleanup after injected failures. Strong signals are exact storage-type counts, JMX bean presence and fields, storage-type removal after disk failure, recovery after restart, and independent load accounting for DISK and ARCHIVE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockStatsMXBean.java -->
