# subset-b-007538 research

This grouped report covers Hadoop HDFS blockmanagement test sources assigned to `subset-b-007538`. Each section is delimited for deterministic reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingReconstruction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingReconstruction.java

## Purpose
`TestPendingReconstruction` validates the queue and BlockManager integration behavior for blocks whose reconstruction work has been scheduled but not yet completed. It covers the standalone `PendingReconstructionBlocks` timeout map, BlockManager transitions after timeout, incremental block reports, file deletion cleanup, NameNode metrics, and duplicate scheduling suppression for the same destination DataNode.

## Important APIs, types, and functions
The main production types under test are `PendingReconstructionBlocks`, `BlockManager`, `LowRedundancyBlocks`, `BlocksMap`, `FSNamesystem`, and the NameNode RPC path `blockReceivedAndDeleted`. Test helpers include `genBlockInfo`, `BlockManagerTestUtil.computeAllPendingWork`, `BlockManagerTestUtil.updateState`, `DataNodeTestUtils.pauseIBR`, `DataNodeTestUtils.setHeartbeatsDisabledForTests`, and `GenericTestUtils.waitFor`. The tests directly use `DatanodeStorageInfo`, `DatanodeDescriptor`, `StorageReceivedDeletedBlocks`, `ReceivedDeletedBlockInfo`, and `BlockStatus.RECEIVED_BLOCK` to simulate reconstruction reports.

## Control flow
`testPendingReconstruction` builds an in-memory pending queue, inserts blocks with distinct target sets, decrements targets, checks duplicate increments, waits for timeout monitor cleanup, and verifies timed-out block accounting. `testProcessPendingReconstructions` creates a MiniDFSCluster, manually inserts pending entries, updates the corresponding `BlocksMap` generation stamp, waits for timeout, and asserts only the stored block with the current generation stamp enters `neededReconstruction`. It then stops the redundancy thread and checks that `addBlock` only clears a pending record when the reported block generation stamp matches the pending block.

`testBlockReceived` creates a one-replica file, disables DataNode heartbeats, raises replication to the DataNode count, computes work, then sends two incremental block reports from new DataNodes. After flushing async block operations, the pending target count drops once per reporting DataNode and remains idempotent on duplicate reports. `testPendingAndInvalidate` corrupts two replicas, schedules reconstruction, deletes the file, and polls until pending reconstruction count returns to zero. `testReplicationCounter` constructs three block states to drive successful, timed-out, and unscheduled reconstruction metrics. `testPendingReConstructionBlocksForSameDN` pauses IBR, runs work computation twice, and checks block state logs contain only one reconstruction assignment for the block.

## State and persistence behavior
The file is concerned with volatile NameNode state: pending reconstruction entries, timeout counters, low-redundancy queues, block map membership, incremental block operation queues, corrupt replica state, invalidation cleanup, and metrics counters. It does not test edit-log or fsimage persistence directly, but it does verify that deleting namespace state removes pending records before the normal timeout window. Generation stamp matching is a critical state invariant: stale reports must not clear pending reconstruction for a newer block version.

## Dependencies and integration points
The tests integrate with MiniDFSCluster, DistributedFileSystem, NameNode metrics, DataNode heartbeat/IBR controls, `NameNodeAdapter`, `FSDirectory`, and BlockManager internals guarded by `RwLockMode.BM`. They depend on asynchronous background threads for pending timeout and redundancy monitoring, so multiple tests use sleeps or `GenericTestUtils.waitFor`.

## Risks and test signals
The test suite signals regressions where reconstruction work is double-counted, never times out, times out against stale block metadata, fails to decrement on incremental block reports, survives file deletion incorrectly, or corrupts metrics. Flakiness risks come from real timers, background monitors, and log counting. The strongest behavioral signals are exact queue sizes, generation-stamp equality, NameNode metric counters, and idempotent pending replica counts after duplicate block reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingReconstruction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingRecoveryBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingRecoveryBlocks.java

## Purpose
`TestPendingRecoveryBlocks` is a focused unit test for `PendingRecoveryBlocks`, the NameNode-side structure that suppresses repeated block recovery attempts within a recovery timeout. It verifies add/remove semantics and timeout-based re-admission for the same block.

## Important APIs, types, and functions
The test constructs `PendingRecoveryBlocks` with a `recoveryTimeout` of 1000 ms and uses `BlockInfoContiguous` wrapping `Block` instances as keys. Mockito spies the tracker so `getTime()` can be controlled deterministically. The public methods under test are `add`, `remove`, and `isUnderRecovery`.

## Control flow
`setUp` creates a spy tracker before each test. `testAddDifferentBlocks` adds three distinct blocks and verifies each is tracked as under recovery. `testAddAndRemoveBlocks` adds two blocks, removes the first, and verifies adding that block again succeeds. `testAddBlockWithPreviousRecoveryTimedOut` forces time to 0 for the first add, to half the timeout for a rejected duplicate add, and to twice the timeout for an accepted recovery retry.

## State and persistence behavior
All state is in-memory and scoped to the tracker. The important state transition is from absent to pending recovery, from pending to absent via `remove`, and from pending to expired when the current time passes the timeout. No persistence or cluster-level state is involved.

## Dependencies and integration points
This is a pure unit test except for Hadoop block model classes and Mockito. It intentionally avoids MiniDFSCluster, BlockManager, and background threads by controlling the clock through the spy.

## Risks and test signals
The main regression signal is whether duplicate recovery is blocked only during the active timeout. Missing behavior includes no checks for concurrent access, batch cleanup, or interaction with lease/block recovery in a running NameNode. The deterministic mocked time makes these tests stable and precise for the core timeout contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingRecoveryBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestProvidedStorageMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestProvidedStorageMap.java

## Purpose
`TestProvidedStorageMap` validates how `ProvidedStorageMap` exposes HDFS PROVIDED storage to multiple DataNodes. It checks that all DataNodes presenting the configured provided storage UUID resolve to the same shared `DatanodeStorageInfo`, while regular DISK storage still follows normal DataNode-local registration.

## Important APIs, types, and functions
The test configures `DFS_PROVIDER_STORAGEUUID`, `DFS_NAMENODE_PROVIDED_ENABLED`, and `DFS_PROVIDED_ALIASMAP_CLASS` with `TestProvidedImpl.TestFileRegionBlockAliasMap`. It uses mocked `BlockManager` and `RwLock`, `DatanodeDescriptor`, `DatanodeStorage`, `DatanodeStorageInfo`, `StorageType.PROVIDED`, and `StorageType.DISK`. The central methods are `ProvidedStorageMap.getProvidedStorageInfo()` and `ProvidedStorageMap.getStorage(...)`.

## Control flow
`setup` prepares the provided UUID, alias map class, block pool ID, and mocks. `testProvidedStorageMap` creates the map and captures its singleton provided storage info. It creates a DataNode, then asks for a PROVIDED storage and a DISK storage while the mocked namesystem lock reports a global write lock. The provided lookup returns the map singleton; the disk lookup is null until a disk `DatanodeStorageInfo` is injected into the descriptor. A second DataNode with the same provided storage UUID also receives the same singleton, and its descriptor is updated to contain that provided storage.

## State and persistence behavior
The tested state is the in-memory association between DataNode descriptors and storage infos. PROVIDED storage is intentionally global per configured UUID and block pool, not a separate per-DataNode storage object. DISK storage remains descriptor-local. The test does not validate alias map persistence or block report contents, only mapping identity and registration side effects.

## Dependencies and integration points
This test sits at the BlockManager storage registration boundary. It depends on the provided-storage feature flags, alias map abstraction, NameNode locking contract, and `DFSTestUtil.getDatanodeDescriptor`. It does not start a cluster.

## Risks and test signals
The important signal is Java object identity: `dns1Provided == providedMapStorage`, `dns2Provided == providedMapStorage`, and injected disk storage identity is preserved. Regressions would duplicate provided storage per DataNode, fail to attach it to the descriptor, or treat unregistered disk storage as implicitly valid. The test does not cover disabled provided storage or wrong UUID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestProvidedStorageMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestRBWBlockInvalidation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestRBWBlockInvalidation.java

## Purpose
`TestRBWBlockInvalidation` covers NameNode and DataNode behavior for replicas in RBW/RWR states when local files disappear, generation stamps diverge, or a DataNode restarts with an outdated replica. It protects against corrupt RBW replicas blocking re-replication and against deletion of good replicas when old-genstamp RWR replicas reappear.

## Important APIs, types, and functions
The tests use `MiniDFSCluster`, `FSDataOutputStream`, `DFSTestUtil`, `MaterializedReplica`, `FSNamesystem`, `BlockManager.countNodes`, `NumberReplicas`, `ExtendedBlock`, and HA helper `HATestUtil.waitForDNDeletions`. `RandomDeleterPolicy` is configured as the block placement policy in one regression test to avoid deterministic free-space ordering hiding bad deletion choices. `waitForNumTotalBlocks` repeatedly triggers block reports until the NameNode block total matches an expected value.

## Control flow
`testBlockInvalidationWhenRBWReplicaMissedInDN` skips Windows because file locking prevents deleting replica files. It starts a two-DataNode cluster, writes and hsyncs a replication-2 file, starts a third DataNode, deletes one DataNode's materialized RBW data and metadata files, closes the stream, then waits for live replicas to drop to one, rise back to two after re-replication, and finally for corrupt replica count to reach zero.

`testRWRInvalidation` opens ten replication-2 files, writes and flushes initial data, stops one pipeline DataNode, writes and flushes new data to the remaining node, lowers replication to one, and closes the files. After restarting the NameNode and DataNodes in an order that exposes old-genstamp replicas first, it computes invalidation work, triggers heartbeats and deletion reports, then verifies block totals and reads every file. `testRWRShouldNotAddedOnDNRestart` disables replacement on write failure, restarts a stopped DataNode after additional writes, and asserts the restarted old-generation node is absent from current block locations.

## State and persistence behavior
The file exercises on-disk DataNode replica files, replica states, generation stamps, block reports, corrupt replica tracking, invalidation queues, and replication counts. It indirectly tests persistence across NameNode restart in the RWR invalidation scenario. The crucial invariant is that older generation stamp replicas are invalidated without losing the only current data copy.

## Dependencies and integration points
These are MiniDFSCluster integration tests involving client write pipelines, DataNode replica storage, NameNode block reports, heartbeat-driven invalidation, and block placement policy. The first test depends on filesystem semantics that permit deleting replica files while the cluster is running.

## Risks and test signals
The strongest signals are live replica counts, corrupt replica counts, successful reads after invalidation, and block location membership. Risks include timing sensitivity from sleeps, block-report intervals, and platform-specific file locking. The tests catch regressions in RBW/RWR cleanup, corrupt replica accounting, generation-stamp comparison, and re-replication scheduling after partial replica loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestRBWBlockInvalidation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReconstructStripedBlocksWithRackAwareness.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReconstructStripedBlocksWithRackAwareness.java

## Purpose
`TestReconstructStripedBlocksWithRackAwareness` validates rack-aware reconstruction for erasure-coded striped blocks. It ensures that complete block groups with insufficient rack diversity are fixed by copying an existing internal block to a new rack rather than by normal decode reconstruction, and that excess internal replicas are pruned to preserve rack diversity.

## Important APIs, types, and functions
The test uses the default erasure coding policy from `StripedFileTestUtil`, `MiniDFSCluster` with explicit host and rack arrays, `DistributedFileSystem`, `BlockInfoStriped`, `LocatedStripedBlock`, `BlockManager`, `DatanodeManager`, `DatanodeAdminManager`, `NetworkTopology`, `DataNodeTestUtils`, and `Whitebox`. Helpers `getHosts`, `getRacks`, `stopDataNode`, and `getDataNode` build deterministic topologies and manipulate live DataNodes.

## Control flow
`setup` configures short redundancy and decommission intervals and disables load consideration. `testReconstructForNotEnoughRacks` starts a cluster with `dataBlocks + parityBlocks + 1` hosts spread across `dataBlocks` racks, stops the final host, creates an EC file with all internal blocks on one fewer rack than required, restarts the stopped host, pauses heartbeats, calls `processMisReplicatedBlocks`, and verifies one DataNode gets replication work while no DataNode gets erasure-coding work.

`testChooseExcessReplicasToDelete` creates an EC file with one host stopped, then stops host1 and restarts the spare host so reconstruction completes elsewhere. When host1 returns and reports its old internal block, the test waits for replication policy cleanup and verifies host1 is no longer in the located striped block. `testReconstructionWithDecommission` builds an 11-host topology, creates a file with two hosts down, restarts one host, stops another to force reconstruction, marks a host decommissioning, restarts the missing hosts, starts decommission through the admin manager, and waits until decommission completes with placement policy satisfied.

## State and persistence behavior
The tested state includes EC block group storage membership, rack counts, DataNode liveness, decommission status, reconstruction work queues, and excess replica selection. No long-term persistence is asserted, but block reports and decommission state transitions are central.

## Dependencies and integration points
This is a high-level integration suite across EC policies, BlockManager placement checks, redundancy monitor work selection, DataNode admin/decommission logic, and rack-aware topology. It uses internal locks and Whitebox access for decommission manager control.

## Risks and test signals
Signals include rack set size, topology leaf/rack counts, per-DataNode replication versus erasure-coding work counters, located block membership, live replica counts, decommissioned state, and `isPlacementPolicySatisfied`. Timing and topology assumptions are the main risks. The tests protect against expensive or wrong EC reconstruction when a simple copy can restore rack diversity, and against deleting the wrong excess internal block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReconstructStripedBlocksWithRackAwareness.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestRedundancyMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestRedundancyMonitor.java

## Purpose
`TestRedundancyMonitor` is a focused concurrency regression test for target choice while DataNodes disappear from topology. It verifies that `BlockPlacementPolicyDefault.chooseTarget` does not propagate a runtime failure when the topology becomes empty between rack-count checks and target selection.

## Important APIs, types, and functions
The test uses `MiniDFSCluster`, `BlockManager`, `BlockPlacementPolicyDefault`, `NetworkTopology`, Mockito `spy`, and `GenericTestUtils.DelayAnswer`. It calls `chooseTarget` directly with the default storage policy and `BLOCK_SIZE`, while another thread removes all `DatanodeDescriptor` entries from a spied topology.

## Control flow
The cluster starts with two hosts on the same rack. The test replaces the placement policy's `clusterMap` with a spy and delays `getNumOfNonEmptyRacks`. One executor task enters `chooseTarget`; once the delay confirms the code path is inside topology inspection, another task removes every DataNode from the topology. The delay is released and `chooseTargetFuture.get()` is checked so any exception is rethrown as the test failure.

## State and persistence behavior
Only in-memory topology and heartbeat manager state are involved. No filesystem data is created. The state transition of interest is a concurrent drop from non-empty topology to empty topology during target selection.

## Dependencies and integration points
This test is at the boundary between BlockManager redundancy work and placement policy. It simulates a race that can occur because redundancy monitor invokes choose-target logic outside the global NameNode lock.

## Risks and test signals
The success signal is absence of an exception. There are no assertions on chosen targets because the scenario is intentionally degraded. The risk area is concurrent topology mutation; a regression would often appear as `ArithmeticException` or another runtime exception from rack arithmetic on an empty topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestRedundancyMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicy.java

## Purpose
`TestReplicationPolicy` is the baseline block placement and low-redundancy test suite for replicated blocks. It runs against both `BlockPlacementPolicyDefault` and `BlockPlacementPolicyWithUpgradeDomain`, exercising target selection, rack locality, exclusions, stale-node avoidance, limited availability, low-redundancy priority iteration, replica deletion, storage policy handling, favored nodes, no-local-write flags, load exclusion, and configuration validation.

## Important APIs, types, and functions
The class extends `BaseReplicationPolicyTest`, overriding `getDatanodeDescriptors` to create six DataNodes across three racks and an extra storage on one DataNode. It uses `BlockPlacementPolicy.chooseTarget`, `BlockPlacementPolicyDefault.chooseReplicaToDelete`, `splitNodesWithRack`, `adjustSetsWithChosenReplica`, `chooseReplicasToDelete`, `useDelHint`, `isMovable`, `LowRedundancyBlocks`, `BlockManager`, `BlockInfoContiguous`, `StatefulBlockInfo`, `DFSUtil.getInvalidateWorkPctPerIteration`, and `DFSUtil.getReplWorkMultiplier`. Configuration and state helpers include `updateHeartbeatWithUsage`, `updateHeartbeatForExtraStorage`, `resetHeartbeatForStorages`, and stale-node timestamp manipulation through `DFSTestUtil.resetLastUpdatesWithOffset`.

## Control flow
The early `testChooseTarget*` methods drive the normal write path. They vary writer locality, excluded nodes, unavailable local storage, rack availability, non-cluster writers, and requests for more targets than available nodes. Assertions verify the standard placement pattern: prefer local if suitable, place a second replica on a different rack, place a third on the second replica's rack, and spread additional replicas without collapsing rack diversity. Multi-storage tests check that a DataNode can be rejected if all its storages are short on space, but accepted when at least one storage has enough remaining space.

Stale-node tests manipulate last heartbeat times and the DatanodeManager stale count. They confirm stale nodes are avoided when at most half the cluster is stale, but are allowed again when avoiding them would create hotspots. Re-replication tests pass pre-existing chosen storages and verify target choice complements current placement. Low-redundancy tests insert `BlockInfo` entries into priority queues, choose bounded batches, and verify iterator progress after updates, stored-block additions, under-construction conversions, and replication factor changes.

Replica deletion tests build replica sets across racks and storage types, then verify deletion preference by rack concentration, remaining space, storage type excess, delete hints, and storage policy changes. The striped deletion variant uses the striped placement policy to verify deterministic deletion order for EC-style candidates. Later tests cover favored nodes, `AddBlockFlag.NO_LOCAL_WRITE`, `excludeNodeByLoad`, COLD policy failures due to missing storage type, choose-attempt behavior with no stale nodes, and not-enough-space logging.

## State and persistence behavior
Most tests operate on in-memory descriptors, storage utilization, rack topology, and low-redundancy queues. A few instantiate MiniDFSCluster for priority scheduling. State under test includes per-storage remaining space, per-DataNode xceiver load, stale timestamps, selected/excluded target sets, low-redundancy cursor position, block collection mappings, under-construction state, storage policy excess types, and log/metric side effects. Persistent namespace storage is not the focus.

## Dependencies and integration points
This file is the main integration point for placement policy contracts consumed by BlockManager writes, re-replication, balancer moves, and storage policy transitions. It also depends on NameNode lock mocks, `BlockStoragePolicySuite`, storage type stats, log appenders, and MiniDFSCluster where background redundancy work is needed.

## Risks and test signals
The suite catches regressions in rack-aware placement, local-write preference, stale-node thresholds, warning logs for unsatisfied target counts, queue iteration skips, deletion choices that violate placement, and invalid configuration acceptance. Risks include parameterization across two policies where assertions must remain valid for both, and helper state leakage if storage heartbeats are not reset. Strong signals include exact target lengths, rack membership checks, chosen storage identity, queue bucket sizes, thrown exceptions for invalid config, and log messages such as `NO_REQUIRED_STORAGE_TYPE` and `NOT_ENOUGH_STORAGE_SPACE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyConsiderLoad.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyConsiderLoad.java

## Purpose
`TestReplicationPolicyConsiderLoad` verifies that placement policy load filtering uses the correct in-service average and configured load factor. It runs against both default and upgrade-domain policies to ensure load exclusion composes with topology-aware placement.

## Important APIs, types, and functions
The class extends `BaseReplicationPolicyTest`, parameterized over `BlockPlacementPolicyDefault` and `BlockPlacementPolicyWithUpgradeDomain`. Its topology has six DataNodes across three racks. It sets `DFS_NAMENODE_REDUNDANCY_CONSIDERLOAD_FACTOR` to 1.2 and uses `HeartbeatManager.updateHeartbeat` to set xceiver counts. It reads `FSClusterStats.getInServiceXceiverAverage` and invokes `chooseTarget`.

## Control flow
`testChooseTargetWithDecomNodes` sets xceiver counts on three nodes, verifies average load over all six in-service nodes, then marks the first three DataNodes decommissioned. The in-service average is recalculated over the remaining three nodes, and choosing three targets from a decommissioned writer must return the three non-decommissioned storages. `testConsiderLoadFactor` sets different xceiver counts across all six nodes, calculates the average, chooses three targets, and asserts no chosen node exceeds average times 1.2.

## State and persistence behavior
The tested state is volatile heartbeat load, decommission flags, and derived in-service load statistics. Decommissioning is started and force-marked in memory, then stopped in the finally block. No persistent decommission state or fsimage behavior is tested.

## Dependencies and integration points
The tests exercise the placement policy's `isGoodTarget` load checks through DatanodeManager heartbeat stats. They also check that decommissioned DataNodes are excluded from average-load calculations and target eligibility.

## Risks and test signals
Regression signals are incorrect in-service average values, choosing decommissioned nodes, or selecting overloaded nodes above the configured factor. The tests rely on manual heartbeat updates under the BlockManager write lock and reset decommission state after execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyConsiderLoad.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyExcludeSlowNodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyExcludeSlowNodes.java

## Purpose
`TestReplicationPolicyExcludeSlowNodes` verifies that slow-peer telemetry can be converted into a slow-node exclusion set and honored by multiple block placement policies. It also verifies that disabling peer statistics through reconfiguration clears the global slow-node set.

## Important APIs, types, and functions
The parameterized class runs with `BlockPlacementPolicyDefault`, `BlockPlacementPolicyWithUpgradeDomain`, `AvailableSpaceBlockPlacementPolicy`, `BlockPlacementPolicyRackFaultTolerant`, and `AvailableSpaceRackFaultTolerantBlockPlacementPolicy`. It enables `DFS_DATANODE_PEER_STATS_ENABLED_KEY`, sets a one-second slow-peer collection interval, and enables `DFS_NAMENODE_BLOCKPLACEMENTPOLICY_EXCLUDE_SLOW_NODES_ENABLED_KEY`. It uses `SlowPeerTracker.addReport`, `OutlierMetrics`, `DatanodeManager.getSlowPeersUuidSet`, `DatanodeManager.getSlowNodesUuidSet`, and NameNode `reconfigureProperty`.

## Control flow
`testChooseTargetExcludeSlowNodes` registers all test DataNodes, adds peer reports so the first three DataNodes are reported slow by the last three, sleeps for the collector, then obtains the slow-peer UUID set. Choosing three targets from a slow writer must return only DataNodes not in the slow set. `testSlowPeerTrackerEnabledClearSlowNodes` adds reports, waits until the static slow-node set is populated, reconfigures peer statistics off, and asserts the set is cleared.

## State and persistence behavior
The state under test is the in-memory `SlowPeerTracker`, DatanodeManager collector initialization, static slow-node UUID set, and placement-time exclusion behavior. Reconfiguration changes runtime NameNode configuration but no persistence is checked.

## Dependencies and integration points
This file integrates slow peer telemetry with block placement. It covers both direct tracker ingestion and the collector path that translates reports into DataNode UUID exclusions. The test intentionally runs across several policies to protect the shared exclusion hook.

## Risks and test signals
Signals include exact slow set size, membership by DataNode UUID, target count, and absence of slow UUIDs in chosen targets. The tests are timing-sensitive because collector execution is observed with sleep or `GenericTestUtils.waitFor`. Regressions include ignoring slow-node exclusions, not clearing slow state on disable, or policy-specific bypass of the shared slow-node filter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyExcludeSlowNodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyRatioConsiderLoadWithStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyRatioConsiderLoadWithStorage.java

## Purpose
`TestReplicationPolicyRatioConsiderLoadWithStorage` validates the load-by-volume placement option. It ensures the default placement policy excludes nodes whose total xceiver load is high and also excludes nodes whose load is too high relative to their number of available volumes.

## Important APIs, types, and functions
The class extends `BaseReplicationPolicyTest` with `BlockPlacementPolicyDefault`. It enables `DFS_NAMENODE_REDUNDANCY_CONSIDERLOAD_KEY`, sets the load factor to 2, and enables `DFS_NAMENODE_REDUNDANCY_CONSIDERLOADBYVOLUME_KEY`. `getDatanodeDescriptors` creates five racks, adds five extra storages to each DataNode, and marks a different number of storages available per node using `DatanodeStorageInfo.setUtilizationForTesting`. `HeartbeatManager.updateHeartbeat` supplies xceiver counts.

## Control flow
The single test updates heartbeats so total cluster load is 200 and average node load is 40. Based on available volume counts, DataNode 1 exceeds node load and DataNode 0 exceeds per-storage load. Choosing three targets from DataNode 2 returns DataNodes 2, 3, and 4. Choosing four targets still returns only those three because the two overloaded nodes remain ineligible.

## State and persistence behavior
State is in-memory storage utilization, available volume count, DataNode xceiver count, and derived average load. The test does not interact with real files or persistence.

## Dependencies and integration points
This test targets placement policy load filtering with the volume-aware extension. It depends on `BlockManagerTestUtil.getStorageReportsForDatanode` reflecting the per-storage utilization injected into descriptors.

## Risks and test signals
The main signals are target length and membership set. It catches regressions where load is considered only per DataNode and not per available volume, or where overloaded nodes are returned to satisfy requested replica count. The comments encode the expected arithmetic and are important for maintaining the thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyRatioConsiderLoadWithStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyWithNodeGroup.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyWithNodeGroup.java

## Purpose
`TestReplicationPolicyWithNodeGroup` validates `BlockPlacementPolicyWithNodeGroup`, where placement must account for node-group fault domains below racks. It checks placement verification, write target selection, re-replication, deletion, boundary topologies, dependency exclusions, and favored-node behavior under node-group constraints.

## Important APIs, types, and functions
The class extends `BaseReplicationPolicyTest`, configures `NetworkTopologyWithNodeGroup`, and disables DFS network topology so tests run against node-group-aware topology. Helpers include `checkTargetsOnDifferentNodeGroup`, `isOnSameRack`, `isOnSameNodeGroup`, `chooseTarget`, `verifyNoTwoTargetsOnSameNodeGroup`, and `calculateRemaining`. It uses `BlockPlacementPolicyWithNodeGroup`, `BlockManager.newLocatedBlock`, `BlockPlacementStatus`, `NetworkTopology.getLastHalf`, `Host2NodesMap`, dependent host names, and storage policy deletion helpers inherited from the default policy.

## Control flow
`testVerifyBlockPlacement` creates located blocks with selected storages and checks placement status plus error descriptions for rack and node-group violations. `testChooseTarget1` through `testChooseTarget5` vary local writer health, exclusions, unavailable local rack, external writer, and no-space local storage. They assert that the first replica follows local preference when possible, later replicas spread across racks and node groups, and no two selected targets share a node group when avoidable. `testChooseTargetForLocalStorage` verifies fallback to another node on the writer's local rack when the writer has no space.

Re-replication tests pass existing chosen nodes and verify new targets complement rack and node-group placement. `testChooseReplicaToDelete` splits candidate replicas into rack/node-group priority sets and chooses deletions by node-group concentration and remaining space. Boundary topology tests replace the cluster topology with cases where one rack has a single node group or the requested replica count exceeds the number of node groups. Dependency testing adds dependent host relationships and verifies exclusions expand to all dependent nodes, reducing target count. Favored-node tests ensure usable favored nodes are selected, unusable favored nodes fall back within their node group, and remaining replicas still obey policy.

## State and persistence behavior
State includes the in-memory network topology, storage remaining space, excluded node sets, favored node lists, host dependency map, and replica candidate partitions. No persistent filesystem writes are required.

## Dependencies and integration points
The file tests the node-group specialization of the generic placement policy and its interaction with topology implementation, Host2NodesMap dependency awareness, storage policy deletion, and favored-node APIs. It depends heavily on the shared `BaseReplicationPolicyTest` harness.

## Risks and test signals
Signals are target lengths, exact storage identities in important cases, rack comparisons, node-group uniqueness, placement error text, deletion identity, and expanded exclusion-set size. The main risks are topology mutations shared across tests and assumptions about deterministic target choice where multiple nodes satisfy the same constraint. It protects against placing multiple replicas in the same node group, deleting replicas that reduce node-group diversity, and ignoring host dependency constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyWithNodeGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyWithUpgradeDomain.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyWithUpgradeDomain.java

## Purpose
`TestReplicationPolicyWithUpgradeDomain` validates `BlockPlacementPolicyWithUpgradeDomain`, which layers upgrade-domain diversity on top of rack-aware block placement. It covers target choice, exclusions, insufficient-domain fallback, placement verification, replica deletion, and move eligibility.

## Important APIs, types, and functions
The test extends `BaseReplicationPolicyTest` and sets `blockPlacementPolicy` to `BlockPlacementPolicyWithUpgradeDomain`. It builds nine DataNodes across three racks, assigning upgrade domains 1, 2, and 3 repeatedly within each rack. It uses `chooseTarget`, `verifyBlockPlacement`, `chooseReplicasToDelete`, `BlockStoragePolicySuite`, `StorageType`, and `isMovable`. Local helpers collect selected upgrade domains and racks from `DatanodeStorageInfo[]`.

## Control flow
`testChooseTarget1` checks target selection for replica counts 0 through 4. It verifies local preference, remote rack placement, same-rack grouping for later replicas, and that selected targets cover the expected number of upgrade domains. `testChooseTargetWithExcludeNodes` adds excluded DataNodes in combinations that constrain available upgrade domains and racks, then verifies the policy still prefers local and preserves diversity where possible. `testChooseTargetWithoutEnoughReplica` excludes enough nodes that only two targets can satisfy a request for three.

`testVerifyBlockPlacement` constructs located blocks with specific rack and upgrade-domain distributions and checks whether placement is satisfied, including whether error descriptions mention upgrade-domain deficiencies only when that is the limiting factor. `testChooseReplicasToDelete` checks delete hints, rejection of hints that would reduce upgrade-domain diversity, storage type excess deletion, and SSD-policy transition scenarios. `testIsMovable` simulates balancer moves and checks whether replacing a source with a target preserves or improves rack and upgrade-domain counts.

## State and persistence behavior
The state under test is in-memory DataNode topology, upgrade-domain labels, selected target lists, candidate replica collections, storage types, and move candidate sets. There is no cluster persistence; the source builds synthetic descriptors through the base harness.

## Dependencies and integration points
This file tests the upgrade-domain placement policy used by writes, re-replication, deletion, and balancer move validation. It integrates with storage policy excess calculations and the generic placement status/error mechanism.

## Risks and test signals
Signals include exact target counts, object identity for expected storages, rack set size, upgrade-domain set size, placement status, error description content, chosen deletion candidates, and `isMovable` booleans. It catches regressions where rack policy is satisfied but upgrade-domain diversity is lost, delete hints are accepted too aggressively, or balancer moves reduce fault-domain diversity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyWithUpgradeDomain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSequentialBlockGroupId.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSequentialBlockGroupId.java

## Purpose
`TestSequentialBlockGroupId` validates allocation and collision handling for erasure-coded block group IDs. It ensures group IDs advance through the striped block group ID space, avoid collisions with existing groups, avoid collisions with legacy contiguous blocks using negative IDs, and reset on BlockManager clear.

## Important APIs, types, and functions
The test uses `SequentialBlockGroupIdGenerator`, `SequentialBlockIdGenerator`, `BlockIdManager`, `BLOCK_GROUP_INDEX_MASK`, `MAX_BLOCKS_IN_GROUP`, `MiniDFSCluster`, `DistributedFileSystem`, `StripedFileTestUtil`, `ErasureCodingPolicy`, and `DFSTestUtil.getAllBlocks`. Mockito `spy`, `doAnswer`, and `Whitebox.setInternalState` replace the regular block ID generator in one collision test.

## Control flow
`setup` starts a MiniDFSCluster sized for the default EC policy plus spare DataNodes, enables the EC policy, creates `/ecDir`, and sets the EC policy on that directory. `testBlockGroupIdGeneration` records the initial generator value, creates an EC file with four block groups, resets the generator to the initial value, repeatedly skips to the next group-aligned value, and asserts each located block group ID matches. It then clears the BlockManager and checks the generator current value is `Long.MIN_VALUE`.

`testTriggerBlockGroupIdCollision` creates one EC file, rewinds the block group generator to its initial value, creates a second EC file, and verifies no block group ID is shared. `testTriggerBlockGroupIdCollisionWithLegacyBlockId` first forces the contiguous `SequentialBlockIdGenerator.nextValue()` to return a value in the block group space, creates a contiguous file with that ID, resets the group generator, creates an EC file, and verifies the EC block group IDs do not collide with the legacy block ID.

## State and persistence behavior
State includes the in-memory generator counters, BlockManager block map, EC directory policy, and allocated block IDs visible through located blocks. The tests do not restart the NameNode, so persistence of generator counters is not exercised.

## Dependencies and integration points
The file integrates ID generators with real file creation for EC and contiguous blocks. It relies on the block group ID layout constants and Whitebox replacement of BlockIdManager internals to force rare collision scenarios.

## Risks and test signals
Signals are exact block group count, expected aligned ID values, uniqueness across files, uniqueness against forced legacy IDs, and reset value after clear. It catches regressions in ID spacing, collision retry loops, and separation between contiguous and striped ID spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSequentialBlockGroupId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSequentialBlockId.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSequentialBlockId.java

## Purpose
`TestSequentialBlockId` validates sequential contiguous block ID allocation, collision recovery when the generator is rewound, legacy versus new block detection by generation stamp, and generation stamp selection for legacy and new blocks.

## Important APIs, types, and functions
The test uses `MiniDFSCluster`, `FileSystem`, `DFSTestUtil.createFile`, `DFSTestUtil.getAllBlocks`, `SequentialBlockIdGenerator`, `BlockIdManager`, and `Block`. Mockito mocks and spies allow direct testing of `BlockIdManager.isLegacyBlock` and `nextGenerationStamp`.

## Control flow
`testBlockIdGeneration` creates a ten-block file in a one-DataNode cluster and asserts each block ID increments by one from the first block. `testTriggerBlockIdCollision` creates one ten-block file, rewinds the sequential block ID generator by five, creates a second ten-block file, and asserts the first block of the second file starts immediately after the last block of the first file rather than colliding. `testBlockTypeDetection` stubs the legacy generation-stamp limit and verifies blocks below or above it are classified correctly. `testGenerationStampUpdate` stubs next legacy and new generation stamp values and verifies `nextGenerationStamp(true/false)` delegates to the right counter.

## State and persistence behavior
The cluster tests use in-memory NameNode block ID generator state and block map collision checks. The mocked tests isolate generation-stamp logic from cluster state. No restart or fsimage persistence is validated.

## Dependencies and integration points
This file tests the ID generation service used during HDFS block allocation and the generation-stamp split used to distinguish legacy blocks. It depends on real file creation for collision detection rather than only testing the generator in isolation.

## Risks and test signals
Signals include exact sequential ID equality, non-colliding start ID after rewind, and boolean/classification outcomes from mocked generation stamps. The tests catch regressions that might allocate duplicate block IDs or misclassify blocks after generation-stamp layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSequentialBlockId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSlowDiskTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSlowDiskTracker.java

## Purpose
`TestSlowDiskTracker` validates NameNode aggregation, expiration, ranking, and JSON serialization of DataNode slow disk reports. It also verifies the DataNode heartbeat path from disk metrics to the NameNode tracker.

## Important APIs, types, and functions
The primary type is `SlowDiskTracker`, especially `addSlowDiskReport`, `updateSlowDiskReportAsync`, `getSlowDisksReport`, `getSlowDiskReportAsJsonString`, `setReportValidityMs`, and nested `DiskLatency`. It uses `SlowDiskReports`, `SlowDiskReports.DiskOp`, `FakeTimer`, Jackson `ObjectReader`, `MiniDFSCluster`, `DataNode.getDiskMetrics().addSlowDiskForTesting`, `DatanodeManager.getSlowDiskTracker`, and `GenericTestUtils.waitFor`.

## Control flow
`testDataNodeHeartbeatSlowDiskReport` starts two DataNodes, injects slow disk metrics into each, waits for heartbeat/report propagation, validates four aggregated disk IDs and operation latencies, then deserializes JSON and checks the same contents. Unit-style tests add synthetic reports directly to the tracker, call `updateSlowDiskReportAsync`, and verify empty reports, retrieval, total expiration, partial expiration, and replacement of expired reports. `testGetJson` checks JSON includes all active reports. `testGetJsonSizeIsLimited` adds eight reports and verifies only the top five latencies are serialized. `testEmptyReport` verifies expired-only state yields null JSON. `testRemoveInvalidReport` uses a MiniDFSCluster tracker with short validity and waits until invalid reports are removed.

## State and persistence behavior
State is in-memory per-DataNode/per-disk latency reports with timestamps, async generated report snapshots, JSON cache, and validity windows. `FakeTimer` controls unit tests, while MiniDFSCluster tests use wall-clock sleeps. No persistent storage is involved.

## Dependencies and integration points
This file bridges DataNode disk metrics, heartbeat reporting, DatanodeManager aggregation, and NameNode JSON reporting. It depends on configuration keys for heartbeat interval, DataNode file IO profiling sampling percentage, and outlier report interval.

## Risks and test signals
Signals include exact report map size, disk ID keys in the `dn:disk` form, per-operation floating-point latencies, JSON deserialization size, top-five ranking, and null JSON for empty active state. Risks are async update timing and wall-clock sleeps. The tests catch regressions in report expiry, stale replacement, JSON limits, and heartbeat integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSlowDiskTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSlowPeerTracker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSlowPeerTracker.java

## Purpose
`TestSlowPeerTracker` validates aggregation, expiration, replacement, ranking, and JSON serialization for slow peer reports. These reports identify DataNodes considered slow by other DataNodes and feed the slow-node exclusion machinery used by placement tests.

## Important APIs, types, and functions
The test uses `SlowPeerTracker`, `SlowPeerJsonReport`, `OutlierMetrics`, `FakeTimer`, and Jackson deserialization to `Set<SlowPeerJsonReport>`. Tracker methods under test include `addReport`, `getReportsForAllDataNodes`, `getReportsForNode`, `getReportValidityMs`, and `getJson`. Helper `isNodeInReports` checks serialized slow-node membership.

## Control flow
`testEmptyReports` verifies empty all-node and per-node queries. `testReportsAreRetrieved` adds reports for two slow nodes from different reporters and checks all-node and per-node counts. Expiration tests advance `FakeTimer` to verify all reports disappear after validity, only newer reports survive partial expiration, and an expired report can be replaced by a valid report for the same slow/reporter pair. `testGetJson` verifies JSON contains slow nodes with reports and excludes nodes that only appear as reporters. `testGetJsonSizeIsLimited` adds more candidate slow nodes than the output limit and verifies high-ranked nodes with multiple reports are retained while a lower-ranked node is excluded. `testLowRankedElementsIgnored` confirms five nodes with two reports outrank ten nodes with one report each.

## State and persistence behavior
State is in-memory slow-node-to-reporting-node telemetry with timestamped `OutlierMetrics`. Expiry is purely based on `FakeTimer`; there is no persistence.

## Dependencies and integration points
This tracker supplies slow peer data to `DatanodeManager` and placement policy slow-node exclusion. The JSON ranking behavior is also consumed by NameNode diagnostics and web/API reporting.

## Risks and test signals
Signals include exact counts, absence after expiry, slow-node membership in JSON, reporter latency ordering in serialized reports, and exclusion of low-ranked elements when the report is capped. The deterministic fake clock makes timing stable. Regressions would lose reports too early, retain stale reports, serialize reporters as slow nodes, or rank one-report nodes above stronger multi-report evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSlowPeerTracker.java -->
