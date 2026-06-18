# Group Research: subset-b-007537

This grouped report covers Hadoop HDFS block-management tests under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithDFS.java

## Purpose
`TestBlockTokenWithDFS` is an integration test for HDFS block access tokens across read, write, append, direct datanode access, namenode restarts, datanode restarts, and balancer integration. It verifies that expired or malformed block tokens fail at the datanode, while DFS clients can transparently refetch valid tokens when the namenode is available.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DFSClient`, `NamenodeProtocols`, `BlockManager`, `BlockTokenSecretManager`, `LocatedBlock`, `ExtendedBlock`, and `BlockReaderFactory`. Helpers include `generateBytes`, `createFile`, `checkFile1`, `checkFile2`, `writeFile`, `tryRead`, `getConf`, `doTestRead`, and `isBlockTokenExpired`. `tryRead` builds a low-level `BlockReader` with a custom `RemotePeerFactory`, making it a direct test of datanode token validation rather than only the high-level `FileSystem` API.

## Control Flow
`testAppend` and `testWrite` set a one-second token lifetime, write part of a block, wait for the stream token to expire, stop a datanode to force pipeline recovery, then finish the operation and validate bytes. `testRead` builds a two-datanode cluster and delegates to `doTestRead`. `doTestRead` creates a file, opens several streams to cache tokens, exercises direct block reads, waits for token expiry, checks failure for expired/wrong-block/wrong-access tokens, lengthens future token lifetime, verifies transparent token refresh, then tests cached-token behavior across datanode and namenode restarts. `testEnd2End` runs the balancer integration with block tokens enabled.

## State and Persistence Behavior
State under test lives in block tokens cached in `FSDataInputStream` instances, token secret-manager lifetime settings, restarted datanode ports, restarted namenode secret state, and block-location metadata returned by the namenode. The test intentionally takes the namenode down to prove whether cached tokens alone are sufficient.

## Dependencies and Integration Points
This file integrates HDFS client streams, `BlockReaderFactory`, datanode transfer sockets, namenode RPC block locations, token secret management, cluster restart paths, and `TestBalancer`. It relies on `DFSTestUtil`, `SecurityTestUtil`, `GenericTestUtils`, and `ServerSocketUtil`.

## Risks and Edge Cases
The test is sensitive to timing around token expiry and cluster restarts. It covers important risks: stale cached tokens after DN/NN restarts, wrong block IDs, wrong access modes, and pipeline recovery using expired tokens. Port choices are pinned for namenode restart stability.

## Test Signals
Assertions verify exact byte equality, token expiry/non-expiry, `InvalidBlockTokenException` on invalid direct reads, successful transparent rereads after refetch, failed reads when the namenode is unavailable and cached tokens no longer work, and successful balancer integration with block tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithDFSStriped.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithDFSStriped.java

## Purpose
`TestBlockTokenWithDFSStriped` adapts the base block-token test suite to erasure-coded striped files. It verifies that read-token expiry, direct datanode token validation, cached-token reuse, token refetch, and balancer behavior remain correct when a client-visible `LocatedStripedBlock` expands into multiple internal blocks.

## Important APIs, Types, and Functions
The class extends `TestBlockTokenWithDFS`. It uses `StripedFileTestUtil.getDefaultECPolicy`, `ErasureCodingPolicy`, `LocatedStripedBlock`, `StripedBlockUtil.parseStripedBlockGroup`, and `MiniDFSCluster`. It overrides `testRead`, `testWrite`, `testAppend`, `testEnd2End`, `tryRead`, and `isBlockTokenExpired`.

## Control Flow
Instance initialization changes inherited `BLOCK_SIZE` and `FILE_SIZE` to match the EC cell size, four stripes per block, and three full data-block groups. `testRead` starts enough datanodes for data plus parity plus spare nodes, enables the default EC policy, sets the root EC policy, and calls the inherited `doTestRead` with `isStriped=true`. `tryRead` decomposes the striped block group and applies the parent direct read check to each internal block. `isBlockTokenExpired` returns true if any non-null internal block token has expired.

## State and Persistence Behavior
The file depends on EC policy state stored in the filesystem namespace and block-token state attached to each internal block of a striped group. It reuses the base test's restart scenarios but adjusts seek behavior because striped input streams do not support `seekToNewSource`.

## Dependencies and Integration Points
Integration points include HDFS erasure-coding policy management, striped block parsing, MiniDFSCluster port assignment, and the balancer striped-file integration test. It also indirectly tests the base class's token, DFS client, and cluster restart logic.

## Risks and Edge Cases
The main risk is treating a striped block group as a single token-bearing block. The overrides guard against this by validating all internal blocks. Write and append are intentionally not covered here: write token expiry is tested in striped output-stream tests, and append for striped files is not supported.

## Test Signals
Success is signaled by inherited read assertions over EC files, internal-block direct reads succeeding or failing as expected, token-expiry checks across all internal blocks, and `TestBalancer.integrationTestWithStripedFile` completing with block tokens enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithDFSStriped.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithShortCircuitRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithShortCircuitRead.java

## Purpose
`TestBlockTokenWithShortCircuitRead` verifies that short-circuit reads continue to behave correctly after a block token expires and that client shared-memory slot accounting does not leak or duplicate slots across repeated reads.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DistributedFileSystem`, `ShortCircuitCache`, `DfsClientShmManager`, `DfsClientShm`, `ShortCircuitShm.Slot`, `TemporarySocketDirectory`, `DomainSocket`, `SecurityTestUtil`, and namenode block-location RPC. Helpers are `readFile`, `checkSlotsAfterSSRWithTokenExpiration`, and `checkShmAndSlots`.

## Control Flow
The test enables block tokens, domain sockets, and short-circuit reads with short-circuit stream caching disabled. It starts a one-datanode cluster, confirms the shared-memory manager starts empty, creates a file, opens it once, and reads it to acquire a token. It then obtains the first block token from the namenode, waits for expiry, rereads through the same stream after seeking to zero, and checks the shared-memory slot count. The expiry and reread check is repeated to ensure stable slot state.

## State and Persistence Behavior
Relevant state is the client short-circuit shared-memory segment and slots keyed by datanode, plus the token attached to the located block. The test does not persist cluster state across restarts; it focuses on in-process client cache and shared-memory bookkeeping.

## Dependencies and Integration Points
It integrates Unix domain socket configuration, HDFS client context, datanode short-circuit read path, namenode token issuance, and block token lifetime manipulation. It depends on local domain socket support but disables bind-path validation for test stability.

## Risks and Edge Cases
The regression risk is that an expired token during short-circuit reads could force creation of duplicate slots or disable the datanode shared-memory entry. Stream cache size is set to zero to reduce unrelated caching effects.

## Test Signals
Assertions verify full-file byte count, non-expired initial token, exactly one datanode entry in the shared-memory manager, a non-disabled datanode entry, one non-full shared-memory segment, zero full segments, and exactly one slot after repeated token-expiry rereads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithShortCircuitRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockUnderConstructionFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockUnderConstructionFeature.java

## Purpose
`TestBlockUnderConstructionFeature` checks the selection of lease-recovery targets for an under-construction block. It verifies that block recovery rotates or selects datanodes according to recovery attempt and recent heartbeat state.

## Important APIs, Types, and Functions
The test uses `BlockUnderConstructionFeature.initializeBlockRecovery`, `BlockInfoContiguous`, `BlockUCState.UNDER_CONSTRUCTION`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `GenerationStamp`, and `DFSTestUtil.resetLastUpdatesWithOffset`.

## Control Flow
The single test creates three datanode storage infos, marks the datanodes alive, creates a contiguous block, and converts it to under-construction state with all three storages. It runs four recovery attempts. Before each attempt it adjusts the datanodes' last-update times, calls `initializeBlockRecovery`, then pulls the lease recovery command from the expected datanode and checks that the target block is the under-construction block.

## State and Persistence Behavior
State is entirely in memory: datanode liveness, monotonic update timestamps, block under-construction feature state, and queued lease-recovery commands. There is no MiniDFSCluster or persisted namespace state.

## Dependencies and Integration Points
The test directly covers block-management internals rather than client APIs. It integrates `BlockInfoContiguous` under-construction conversion with datanode descriptor recovery queues.

## Risks and Edge Cases
The key risk is repeatedly selecting an unhealthy or stale replica for recovery, which can slow or block lease recovery. The final attempt resets heartbeat timestamps and confirms the most recent heartbeat can be selected again.

## Test Signals
Each recovery attempt asserts that the expected datanode's `getLeaseRecoveryCommand(1)` returns the same `BlockInfo` instance, providing a direct signal that the recovery command was queued on the intended datanode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockUnderConstructionFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlocksWithNotEnoughRacks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlocksWithNotEnoughRacks.java

## Purpose
`TestBlocksWithNotEnoughRacks` is a slow integration suite for rack-aware replica placement and reconstruction. It verifies that HDFS repairs or preserves rack diversity when blocks are under-replicated, mis-replicated, corrupt, over-replicated, affected by node failure, or affected by decommissioning. It also covers upgrade-domain-aware placement.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DFSTestUtil.waitForReplication`, `NameNodeAdapter.setReplication`, `DatanodeManager.removeDatanode`, `HostsFileWriter`, `BlockPlacementPolicyWithUpgradeDomain`, `BlockManager.neededReconstruction`, and `BlockManager.scheduleReconstruction`. Helpers include `getConf`, `scheduleReconstruction`, and `getDnDescriptors`.

## Control Flow
Cluster configurations use short heartbeat, redundancy, pending-reconstruction, and block-report intervals plus a topology script key to enable rack awareness. Individual tests create files with controlled replication and rack layouts, add or remove datanodes, change replication factors, corrupt replicas, decommission nodes, run `fsck -replicate`, and then wait for expected rack counts and replica counts. Upgrade-domain tests assign `upgradeDomain` values to `DatanodeDescriptor`s and verify additional reconstruction requirements and final placement.

## State and Persistence Behavior
State under test includes namenode block placement metadata, low-redundancy queues, excess/invalidation decisions, datanode admin state, host exclude files, corrupt replica state, and upgrade-domain labels. The tests persist blocks in MiniDFSCluster data directories during each test but clean clusters afterward.

## Dependencies and Integration Points
This file integrates the namenode block manager, rack topology mapping, decommission manager, fsck replication command, datanode liveness removal, corrupt replica processing, and upgrade-domain placement policy.

## Risks and Edge Cases
Covered risks include blocks that are numerically replicated but all on one rack, corruption repair choosing same-rack targets, over-replication deleting the only cross-rack copy, decommissioning reducing rack diversity, and upgrade-domain scheduling needing multiple additional replicas.

## Test Signals
The main signals are `DFSTestUtil.waitForReplication` with expected rack counts, fsck output containing placement-policy violation and queued replication text, byte comparisons for non-corrupt replicas, `BlockReconstructionWork.getAdditionalReplRequired`, and successful waits for both rack and upgrade-domain diversity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlocksWithNotEnoughRacks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCachedBlocksList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCachedBlocksList.java

## Purpose
`TestCachedBlocksList` validates the intrusive cached-block lists held by `DatanodeDescriptor`: pending cached, cached, and pending uncached. It ensures list ordering, insertion, removal, iterator removal, random removal, and independent membership across multiple datanode/list combinations.

## Important APIs, Types, and Functions
The test uses `DatanodeDescriptor.CachedBlocksList`, `CachedBlock`, and `DatanodeID`. Helpers are `testAddElementsToList` and `testRemoveElementsFromList`.

## Control Flow
`testSingleList` creates one descriptor and three cached blocks. It checks empty initial lists, appends blocks, prepends one block, removes a middle block, and clears the list while verifying iterator order after each operation. `testMultipleLists` creates two descriptors and five lists, inserts 8000 `CachedBlock` instances into each list, then removes all blocks either through iterator removal or pseudo-random explicit removal.

## State and Persistence Behavior
All state is in memory. The tested lists attach `CachedBlock` entries to datanode-specific linked-list state, so the same block objects must be able to appear in multiple descriptor lists without corrupting list pointers.

## Dependencies and Integration Points
The test is internal to HDFS caching metadata. It does not use cluster services, but it protects the data structures used by centralized cache management and datanode cache directives.

## Risks and Edge Cases
The high-risk area is pointer corruption in intrusive lists when blocks are inserted into several lists or removed through different paths. The 8000-block randomized removal pass is a stress signal for iterator consistency and per-list independence.

## Test Signals
Assertions verify empty-list state, exact iteration order, successful add/remove return values, no remaining iterator entries after clear/removal, and stability across multiple datanode cached-block lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCachedBlocksList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestComputeInvalidateWork.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestComputeInvalidateWork.java

## Purpose
`TestComputeInvalidateWork` verifies how `BlockManager.computeInvalidateWork` schedules deletion work for contiguous replicas and erasure-coded striped blocks. It also checks that invalidation work is skipped or removed when datanodes reformat or re-register with new identities.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `FSNamesystem`, `BlockManager`, `DatanodeManager`, `InvalidateBlocks`, `LocatedStripedBlock`, `SystemErasureCodingPolicies.XOR_2_1_POLICY_ID`, `BlockManagerTestUtil.stopRedundancyThread`, and `Whitebox`. Helpers include `setup`, `teardown`, and `verifyInvalidationWorkCounts`.

## Control Flow
Setup starts a three-datanode cluster, stops the redundancy thread for deterministic behavior, enables an XOR EC policy, creates a striped file, and records the first `LocatedStripedBlock`. The replica, striped, and mixed invalidation tests add more than three times the per-datanode invalidate limit to each datanode under the block-manager write lock, then call `computeInvalidateWork` with varying node limits. Reformat and re-registration tests mutate datanode UUIDs and registrations to ensure stale invalidation work is skipped or removed.

## State and Persistence Behavior
State includes the block-manager invalidation queues, counts split between replica and EC invalidations, datanode UUID registration mappings, and deleted-block queues populated when files are deleted while datanodes are shut down.

## Dependencies and Integration Points
The file integrates EC file creation, namenode block-manager invalidation queues, datanode registration, datanode shutdown, block deletion marking, and white-box access to internal `InvalidateBlocks`.

## Risks and Edge Cases
Important edge cases are fairness and limits across datanodes, mixed replica/EC queues, old datanode UUIDs after reformat, and dead datanodes re-registering with different IDs while invalidations are pending.

## Test Signals
Assertions compare computed work counts against the invalidate limit, verify zero pending deletion after UUID replacement, and check that `InvalidateBlocks` replica and EC counts decrease predictably as datanodes re-register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestComputeInvalidateWork.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCorruptReplicaInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCorruptReplicaInfo.java

## Purpose
`TestCorruptReplicaInfo` validates `CorruptReplicasMap` accounting and pagination for corrupt contiguous replicas and corrupt erasure-coded block groups. It ensures total, replicated, and striped corrupt counts are maintained independently and that test block-id listing APIs return the expected ranges.

## Important APIs, Types, and Functions
The test uses `CorruptReplicasMap`, `BlockIdManager`, `BlockType`, `BlockInfoContiguous`, `BlockInfoStriped`, `StripedFileTestUtil`, `DatanodeDescriptor`, and `CorruptReplicasMap.Reason`. Helpers are `getReplica`, `getStripedBlock`, `verifyCorruptBlocksCount`, and `addToCorruptReplicasMap`.

## Control Flow
The test starts with an empty map and checks invalid and zero-length listing requests. It creates arrays of 140 contiguous block IDs and 140 striped block IDs. It adds corrupt entries for two datanodes, verifying that multiple corrupt replicas of the same block do not increase the corrupt-block count. It removes entries and checks counts return to zero, then bulk-adds all contiguous and striped blocks and validates first-page and offset-page results.

## State and Persistence Behavior
All state is in memory. The file uses local maps to preserve stable `BlockInfo` instances by ID, mirroring how the production corrupt map keys by block identity.

## Dependencies and Integration Points
This is a focused unit test of corrupt replica metadata. It mocks `BlockIdManager` for legacy/striped classification and uses real block-info implementations for contiguous and striped blocks.

## Risks and Edge Cases
Risks include double-counting a block with corrupt reports from multiple datanodes, mixing contiguous and striped counters, bad pagination with the `startingBlockId` argument, and accepting invalid `n` values.

## Test Signals
Signals include exact size/counter assertions after each add/remove, null returns for invalid limits, empty arrays for zero limit, and array equality for contiguous and striped block ID slices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCorruptReplicaInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCorruptionWithFailover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCorruptionWithFailover.java

## Purpose
`TestCorruptionWithFailover` verifies that corrupt replica accounting survives HA failover for a replicated file when a datanode reports an older-generation replica after pipeline recovery.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster` with `MiniDFSNNTopology.simpleHATopology`, `DistributedFileSystem`, `FSDataOutputStream`, `BlockManager`, `GenericTestUtils.waitFor`, and `DFS_NAMENODE_CORRUPT_BLOCK_DELETE_IMMEDIATELY_ENABLED`.

## Control Flow
The test disables immediate corrupt-block deletion and lowers the write replacement minimum replication. It starts a three-datanode HA cluster, activates NN0, writes and syncs 1 MiB, stops one datanode to trigger pipeline update, writes another 1 MiB, and closes. Both namenodes mark all datanodes stale. The stopped datanode is restarted and eventually reports a lower-generation replica, causing NN0 to count one corrupt block. The test then fails over to NN1 and waits for NN1 to report the same corrupt count.

## State and Persistence Behavior
State under test is HA block-manager corrupt-replica metadata, datanode stale state, and generation-stamp differences created by pipeline recovery. The corrupt replica is not deleted immediately, so its metadata remains visible across failover.

## Dependencies and Integration Points
The test integrates DFS output stream pipeline recovery, datanode restart/reporting, namenode HA transitions, and block-manager corrupt counters.

## Risks and Edge Cases
The scenario guards against active and standby block managers diverging on corrupt counts when stale datanode handling postpones deletion during failover.

## Test Signals
`GenericTestUtils.waitFor` checks `bm0.getCorruptBlocks() == 1`, then after failover checks `bm1.getCorruptBlocks() == 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestCorruptionWithFailover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeAdminMonitorBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeAdminMonitorBase.java

## Purpose
`TestDatanodeAdminMonitorBase` verifies ordering behavior for the pending-nodes priority queue used by datanode admin monitoring, especially decommission handling for unhealthy or stale nodes.

## Important APIs, Types, and Functions
The test uses `DatanodeAdminMonitorBase.PENDING_NODES_QUEUE_COMPARATOR`, `DatanodeDescriptor`, `DatanodeID.EMPTY_DATANODE_ID`, `PriorityQueue`, and Java stream sorting.

## Control Flow
A static array of ten datanode descriptors is built with deliberately unordered `lastUpdate` and `lastUpdateMonotonic` values. `testPendingNodesQueueOrdering` inserts all nodes into a priority queue using the comparator and polls them, expecting descending last-update order. `testPendingNodesQueueReverseOrdering` sorts the same nodes with the reversed comparator and expects ascending order.

## State and Persistence Behavior
All state is in memory. The significant state is timestamp metadata on descriptors; no cluster or persistent filesystem state is involved.

## Dependencies and Integration Points
This is a focused unit test for admin-monitor queue ordering. It indirectly protects decommission and maintenance workflows that depend on processing healthier or more recently updated nodes before stale nodes.

## Risks and Edge Cases
The test covers duplicate timestamp values, zero timestamps, and large timestamp values. Incorrect ordering could prioritize unhealthy nodes and slow decommission progress.

## Test Signals
Assertions check that every polled or sorted datanode has the exact expected `lastUpdate` value in descending or ascending order and that queue polling never returns null before all ten nodes are consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeAdminMonitorBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeDescriptor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeDescriptor.java

## Purpose
`TestDatanodeDescriptor` tests two core descriptor behaviors: limiting invalidation commands returned to a datanode and maintaining accurate block counts as blocks are added or removed from datanode storages.

## Important APIs, Types, and Functions
The test uses `DatanodeDescriptor`, `DatanodeStorageInfo`, `DatanodeStorageInfo.AddBlockResult`, `BlocksMap.removeBlock`, `BlockInfoContiguous`, `Block`, `GenerationStamp`, `DFSTestUtil`, and `BlockManagerTestUtil`.

## Control Flow
`testGetInvalidateBlocks` creates ten blocks, queues them for invalidation on one descriptor, then calls `getInvalidateBlocks` with a limit of eight. The first call returns eight blocks and the second returns the remaining two. `testBlocksCounter` creates a descriptor with storage info, adds one block, tries to remove a missing block, tries to add an existing block again, adds a second block, and removes both blocks while checking `numBlocks`.

## State and Persistence Behavior
State is in-memory descriptor metadata: invalidation queues, storage-to-block membership, and the descriptor block counter. There is no MiniDFSCluster.

## Dependencies and Integration Points
The block counter checks protect `BlocksMap` and `DatanodeStorageInfo` interactions. The invalidation limit behavior is consumed by heartbeat command generation.

## Risks and Edge Cases
Risks include returning too many invalidation blocks in one heartbeat, failing to drain remaining invalidations, double-counting duplicate block additions, or decrementing counts for non-existent removals.

## Test Signals
Assertions verify the exact invalidation batch lengths, `ADDED` return values only for first additions, non-`ADDED` for duplicate add, false removal of a missing block, true removals of present blocks, and exact `numBlocks` after every transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeDescriptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeManager.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestDatanodeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestErasureCodingCorruption.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestErasureCodingCorruption.java

## Purpose
`TestErasureCodingCorruption` verifies that a striped block group is not left in the corrupt replica map when a failed-write internal replica should be deleted but deletion is postponed due to stale datanode handling around failover.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster` with HA topology, `DistributedFileSystem`, `FSDataOutputStream`, `BlockManager.getCorruptECBlockGroups`, `GenericTestUtils.waitFor`, and `DFS_NAMENODE_CORRUPT_BLOCK_DELETE_IMMEDIATELY_ENABLED`.

## Control Flow
The test disables immediate corrupt-replica deletion, starts an eight-datanode HA cluster, activates NN0, creates `/dir`, sets the `RS-6-3-1024k` EC policy, and writes more than one stripe. It stops one datanode to trigger pipeline update, writes more data, and closes the file. NN0 transitions standby then active, the stopped datanode restarts and reports the failed-write replica, and the test waits for the EC corrupt-block-group count to be zero.

## State and Persistence Behavior
State under test includes EC block-group corruption metadata, datanode report processing, generation-stamp mismatch handling, and stale-storage deletion postponement. The file data exists only within the test cluster lifetime.

## Dependencies and Integration Points
The test integrates HDFS EC write pipelines, HA transitions, datanode restart/report logic, corrupt-replica map maintenance, and block-manager EC corrupt counters.

## Risks and Edge Cases
The main edge case is specific to striped blocks: a single bad internal replica can cause the whole block group to be marked corrupt, but if that replica is scheduled for deletion the block group should not remain counted as corrupt indefinitely.

## Test Signals
The final wait condition asserts `bm.getCorruptECBlockGroups() == 0`, proving that the block group was explicitly removed from corrupt EC accounting after the failed-write replica report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestErasureCodingCorruption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHeartbeatHandling.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHeartbeatHandling.java

## Purpose
`TestHeartbeatHandling` verifies namenode heartbeat handling for replication commands, invalidation commands, block recovery commands, stale-node filtering, and heartbeat-check stopwatch abort behavior.

## Important APIs, Types, and Functions
The test uses `FSNamesystem`, `HeartbeatManager`, `NameNodeAdapter.sendHeartBeat`, `DatanodeDescriptor`, `DatanodeRegistration`, `BlockCommand`, `BlockRecoveryCommand`, `DatanodeProtocol` actions, `BlockInfoContiguous`, and `HeartbeatManager.shouldAbortHeartbeatCheck`.

## Control Flow
`testHeartbeat` starts a cluster, queues more replication and invalidation work than heartbeat limits allow, sends repeated synthetic heartbeats, and verifies command counts and action order as queues drain. `testHeartbeatBlockRecovery` starts three datanodes, creates under-recovery blocks across their storages, manipulates last-update timestamps, and checks which nodes appear in the recovery command. `testHeartbeatStopWatch` creates a mocked heartbeat manager, restarts its stopwatch, sleeps across the configured recheck interval, and checks abort decisions.

## State and Persistence Behavior
State includes per-datanode replication queues, invalidation queues, storage metadata, under-recovery block state, heartbeat timestamps, and the heartbeat manager stopwatch. Cluster state is temporary and scoped to each test.

## Dependencies and Integration Points
The file integrates namenode heartbeat RPC handling through test adapters, block-manager queue limits, datanode storage updates, stale interval logic, and block recovery command construction.

## Risks and Edge Cases
Covered risks include over-large heartbeat command batches, incorrect command ordering, failing to drain remainder queues, including stale nodes unnecessarily in recovery, excluding all nodes when every node appears stale, and heartbeat checks running too long without aborting.

## Test Signals
Assertions verify exact command array lengths, `DNA_TRANSFER`, `DNA_INVALIDATE`, and `DNA_RECOVERBLOCK` actions, exact block counts per command, exact recovery-node arrays for all-alive, one-stale, and all-stale cases, and stopwatch abort decisions before and after the recheck interval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHeartbeatHandling.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHost2NodesMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHost2NodesMap.java

## Purpose
`TestHost2NodesMap` verifies host-to-datanode mapping behavior when multiple datanodes share a host address, nodes are removed, and null or absent nodes are queried.

## Important APIs, Types, and Functions
The test uses `Host2NodesMap`, `DatanodeDescriptor`, and `DFSTestUtil.getDatanodeDescriptor`. The methods under test are `add`, `contains`, `getDatanodeByHost`, and `remove`.

## Control Flow
Setup creates four descriptors across three IPs, with two descriptors sharing `3.3.3.3` but different transfer ports, adds them to the map, and also calls `add(null)`. `testContains` checks that all inserted nodes are present while null and a non-inserted descriptor are absent. `testGetDatanodeByHost` checks single-host lookups and allows either descriptor for the shared host. `testRemove` removes absent, present, shared-host, null, and already-removed nodes while checking remaining lookup behavior.

## State and Persistence Behavior
State is an in-memory host-to-node map, including a multi-entry bucket for shared hosts. There is no persistent or cluster state.

## Dependencies and Integration Points
This unit test protects `DatanodeManager` host lookup behavior used during registration, report generation, and locality sorting.

## Risks and Edge Cases
Edge cases include null additions/removals, repeated host addresses, removing one node while another remains on the same host, and removing the last node for a host.

## Test Signals
Assertions verify boolean contains/remove results, exact descriptor returns for unique hosts, nullable returns for absent hosts, and either shared descriptor when both are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHost2NodesMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHostFileManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHostFileManager.java

## Purpose
`TestHostFileManager` verifies include/exclude host-set behavior, address deduplication, wildcard port matching semantics, and datanode report generation for included but missing nodes.

## Important APIs, Types, and Functions
The test uses `HostFileManager.parseEntry`, `HostSet`, `DatanodeManager`, `DatanodeDescriptor`, `DatanodeID`, `HdfsConstants.DatanodeReportType`, and `Whitebox` to inject the host manager into a datanode manager.

## Control Flow
`testDeduplication` adds localhost and loopback entries with matching and differing ports and checks final set size. `testRelation` checks `match` and `matchedBy` for exact host:port entries, host-only entries, and unrelated hosts. `testIncludeExcludeLists` builds included and excluded host sets, refreshes the host manager, injects it into a datanode manager, and mutates the datanode map to verify ALL and DEAD reports as live or dead descriptors appear and disappear.

## State and Persistence Behavior
State is in-memory include/exclude sets and the datanode manager's `datanodeMap`. No host files are read from disk in this test.

## Dependencies and Integration Points
This test connects host-file parsing semantics to `DatanodeManager.getDatanodeListForReport`, which powers administrative reports and dead-node visibility.

## Risks and Edge Cases
Covered risks include duplicate include entries due to DNS aliases, host-only entries matching all ports, port-specific entries not overmatching, excluded nodes affecting dead reports, and included dead nodes remaining visible even when not present in the datanode map.

## Test Signals
Assertions verify host-set sizes, `match` and `matchedBy` truth tables, and datanode report list sizes as included nodes are registered, marked dead, removed, or excluded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHostFileManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHostSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHostSet.java

## Purpose
`TestHostSet` is a regression test for unresolved address handling in `HostSet.add`. It ensures unresolved datanode addresses are skipped without throwing and without preventing subsequent resolved addresses from being added.

## Important APIs, Types, and Functions
The test uses `HostSet`, `InetSocketAddress.createUnresolved`, and ordinary resolved `InetSocketAddress` construction. The primary method under test is `HostSet.add`.

## Control Flow
`testAddUnresolvedAddressDoesNotThrow` creates an unresolved hostname and adds it to a new `HostSet`, expecting no exception and no entry. `testAddResolvedAddressSucceeds` adds `127.0.0.1:50010` and expects one entry. `testAddMixedAddressesSkipsUnresolved` adds two resolved loopback addresses with a skipped unresolved entry between them and expects only the resolved addresses in the set.

## State and Persistence Behavior
State is an in-memory host set. The unresolved address is constructed without network access, making the regression deterministic.

## Dependencies and Integration Points
This protects callers such as `dfsadmin -report` and the NameNode web UI from failing when one datanode hostname is no longer resolvable.

## Risks and Edge Cases
The covered regression is an uncaught `IllegalArgumentException` or full batch abort when an unresolved address appears in host data. It also guards against the fix accidentally rejecting resolved addresses.

## Test Signals
Assertions verify unresolved state, resolved state, no thrown exception, and final set sizes of zero, one, and two for the three scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestHostSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestLowRedundancyBlockQueues.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestLowRedundancyBlockQueues.java

## Purpose
`TestLowRedundancyBlockQueues` validates priority queues and counters in `LowRedundancyBlocks` for contiguous replicated blocks and erasure-coded striped block groups. It is parameterized across EC policies.

## Important APIs, Types, and Functions
The test uses `LowRedundancyBlocks`, `BlockInfoContiguous`, `BlockInfoStriped`, `ErasureCodingPolicy`, `StripedFileTestUtil.getECPolicies`, queue constants such as `QUEUE_HIGHEST_PRIORITY`, and helper methods `verifyBlockStats`, `assertAdded`, and `assertInLevel`.

## Control Flow
The parameterized class receives an EC policy. `testDeletedBlocks` checks that deleted/corrupt block infos are skipped when choosing low-redundancy blocks and that queue positions advance and reset. `testQueuePositionCanBeReset` checks iterator cursor reset. `testBlockPriorities` adds blocks with different current and expected replica counts, updates expected counts, and checks queue levels and counters. `testRemoveWithWrongPriority` ensures removal decrements corrupt counts even with an incorrect priority. `testStripedBlockPriorities` checks EC group priority thresholds. `testRemoveBlockInManyQueues` verifies a block present in multiple queue levels is fully removed.

## State and Persistence Behavior
State is in-memory queue membership, queue cursors, per-category counters, corrupt block counters, badly-distributed counters, and block collection IDs used to distinguish deleted blocks.

## Dependencies and Integration Points
This test directly protects the block manager's reconstruction candidate queues. It covers both replicated and EC queues used by redundancy scheduling.

## Risks and Edge Cases
Risks include returning deleted blocks, cursor reset bugs, duplicate additions, incorrect priority classification, corrupt replication-one count drift, EC corrupt count drift, badly-distributed accounting, and incomplete removal from multiple queue levels.

## Test Signals
Signals include exact queue-level membership, exact counter assertions from `verifyBlockStats`, selected block IDs from `chooseLowRedundancyBlocks`, false duplicate additions, and final `contains` false after broad removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestLowRedundancyBlockQueues.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestNameNodePrunesMissingStorages.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestNameNodePrunesMissingStorages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestNodeCount.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestNodeCount.java

## Purpose
`TestNodeCount` verifies that `BlockManager.countNodes` reports live and excess replica counts correctly as datanodes fail, rejoin, and cause over-replication. The namenode uses these counts to decide under- and over-replication actions.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `FSNamesystem`, `BlockManager`, `HeartbeatManager`, `NumberReplicas`, `BlockManagerTestUtil.noticeDeadDatanode`, and helper methods `initializeTimeout`, `checkTimeout`, and `countNodes`.

## Control Flow
The test starts two datanodes, creates a one-block replicated file, records descriptors, starts two additional datanodes, stops one original datanode, forces the namenode to notice the dead node, and waits for replication to return to the target factor. It restarts the failed node, waits for at least one excess replica, chooses a non-excess datanode holding the block, stops that node, waits for live replicas to equal the factor, restarts it, and waits for excess replicas to reach two.

## State and Persistence Behavior
State includes live datanode membership, block replica locations, excess replica tracking, and block-manager counts under the block-manager read lock. The test delays startup block deletion to avoid invalidation races.

## Dependencies and Integration Points
This is a MiniDFSCluster integration test for the block manager, heartbeat manager, dead-node detection, replication monitor, and excess-replica bookkeeping.

## Risks and Edge Cases
It covers races between dead-node detection, replication, datanode rejoin, and excess marking. The timeout helpers include last observed count data to diagnose stuck count transitions.

## Test Signals
Signals are successful replication waits, non-null selection of a non-excess datanode, live replica count equaling the replication factor after a stop, and excess replica count becoming one and then two after datanode restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestNodeCount.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestOverReplicatedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestOverReplicatedBlocks.java

## Purpose
`TestOverReplicatedBlocks` validates over-replication handling: corrupt replicas must not be treated as valid deletion candidates, stale-heartbeat datanodes should be preferred for deletion scheduling, and partial blocks should be invalidated when replication is lowered.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DFSTestUtil`, `BlockManager`, `HeartbeatManager`, `NameNodeAdapter.setReplication`, `InternalDataNodeTestUtils`, `BlockManager.countNodes`, `getExcessSize4Testing`, and datanode storage utilization test hooks.

## Control Flow
`testProcesOverReplicateBlock` creates a three-replica file, corrupts one replica, restarts the datanode to detect corruption, lowers replication to one, and checks a live valid replica remains. `testChooseReplicaToDelete` creates a four-replica file, adds a datanode with rare heartbeats, waits beyond the tolerable heartbeat interval, lowers replication, and verifies all excess deletions are scheduled on the stale datanode without actual deletion. `testInvalidateOverReplicatedBlock` writes and syncs a partial block at replication two, lowers replication to one before close, and verifies one live replica remains.

## State and Persistence Behavior
State includes corrupt replica metadata, storage utilization values, stale heartbeat timestamps, excess replica queues, and live replica counts. Cluster block data is temporary.

## Dependencies and Integration Points
The file integrates block scanning/corrupt detection, over-replication deletion choice, heartbeat freshness, replication-factor changes, partial-block finalization, and excess replica tracking.

## Risks and Edge Cases
Risks include deleting valid replicas while keeping corrupt ones, deleting from healthy datanodes instead of stale ones, or failing to invalidate excess replicas for a block still open or partially written.

## Test Signals
Assertions check live replica counts after corrupt over-replication processing, excess queue size for the stale datanode, unchanged block-location replica counts before stale heartbeat deletion can occur, and one live replica after partial-block replication reduction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestOverReplicatedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingDataNodeMessages.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingDataNodeMessages.java

## Purpose
`TestPendingDataNodeMessages` verifies queueing and draining of pending datanode block reports, including generation-stamp matching, removal of queued reports, and HA standby processing for erasure-coded incremental block reports.

## Important APIs, Types, and Functions
The test uses `PendingDataNodeMessages`, `ReportedBlockInfo`, `DatanodeStorageInfo`, `DatanodeStorage`, `ReplicaState`, `Block`, `MiniDFSCluster` HA topology, `HATestUtil`, `ErasureCodingPolicy`, and `SystemErasureCodingPolicies`.

## Control Flow
`testQueues` enqueues four reports for two storages and two generation stamps of the same block ID, confirms unrelated block lookup does not drain them, then takes the queue using a different `Block` instance with the same ID and generation stamp. `testPendingDataNodeMessagesWithEC` creates an HA EC file, rolls edits on NN0, tails edits on NN1, and checks the standby pending message count is zero. `testRemoveQueuedBlock` removes queued reports for one storage and verifies only the other storage's reports remain.

## State and Persistence Behavior
The unit tests use in-memory pending queues keyed by block identity. The EC HA test uses edit-log tailing and standby block-manager pending message state.

## Dependencies and Integration Points
This file protects delayed IBR processing during namespace/edit-log synchronization and block report handling, especially for erasure-coded blocks in HA.

## Risks and Edge Cases
Risks include queue keying by object identity instead of block identity, generation-stamp conflation, failing to decrement global counts, failing to remove only targeted storage reports, or leaving standby pending IBR messages after tailing EC edits.

## Test Signals
Assertions check queue counts before and after take/remove operations, null returns for unrelated or already-drained queues, string-joined report ordering, and zero pending datanode messages after HA standby tail edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingDataNodeMessages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingInvalidateBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingInvalidateBlock.java

## Purpose
`TestPendingInvalidateBlock` verifies delayed block deletion accounting after namenode startup and for unknown blocks reported by datanodes shortly after restart. It also checks client protocol compatibility for the pending-deletion stats index.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DistributedFileSystem`, `InvalidateBlocks`, `Whitebox`, Mockito spies, `DataNodeTestUtils.triggerBlockReport`, `DFSClient.getStateByIndex` via reflection, and `ClientProtocol.GET_STATS_PENDING_DELETION_BLOCKS_IDX`. Helpers are `setUp`, `tearDown`, `waitForReplication`, and `waitForNumPendingDeletionBlocks`.

## Control Flow
Setup configures small block size, five-second startup block-deletion delay, short block-report and heartbeat intervals, and a two-datanode cluster. `testPendingDeletion` creates a replicated file, restarts the namenode, spies `InvalidateBlocks` to force a deletion delay, deletes the file, waits for two pending deletion blocks, then removes the delay and waits for zero. It also invokes `DFSClient.getStateByIndex` for valid and invalid stats indices. `testPendingDeleteUnknownBlocks` creates five files, stops all datanodes, deletes two files, restarts the namenode with delayed invalidation, restarts datanodes, triggers block reports, observes four pending deletions, then restarts the namenode and waits for pending deletion to clear.

## State and Persistence Behavior
State includes persisted file/block metadata across namenode restart, invalidation delay timestamps, pending deletion counters in the namesystem and client stats, and unknown block reports from datanodes.

## Dependencies and Integration Points
The test integrates filesystem delete, namenode restart, block reports, datanode restart, invalidation queue delay logic, client stats compatibility, and white-box block-manager state replacement.

## Risks and Edge Cases
Covered risks include deleting blocks too early during startup, under-reporting pending deletions to clients, mishandling unknown blocks in early block reports, and invalid stats index behavior.

## Test Signals
Assertions verify blocks total is zero or three as expected, pending deletion counts on namesystem and DFS client, block deletion start time after NN start time, valid stats index returning zero after drain, invalid stats index returning -1, and pending unknown deletions clearing after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingInvalidateBlock.java -->
