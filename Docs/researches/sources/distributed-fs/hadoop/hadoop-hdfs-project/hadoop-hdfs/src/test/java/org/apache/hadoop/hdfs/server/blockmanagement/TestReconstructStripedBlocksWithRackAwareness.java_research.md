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
