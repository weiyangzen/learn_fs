# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ErasureCodingWork.java

## Purpose

`ErasureCodingWork` is a `BlockReconstructionWork` specialization that chooses targets and enqueues datanode work for striped erasure-coded blocks. It handles full decode/reconstruction and optimized simple replication of an internal block when all internal blocks exist but rack placement or leaving-service requirements require another copy.

## Important APIs, Types, and State

Constructor state includes `blockPoolId`, `liveBlockIndices`, `liveBusyBlockIndices`, and `excludeReconstructedIndices`, in addition to base reconstruction work state such as block, source nodes, containing nodes, live replica storages, priority, and required additional replicas. Methods include `chooseTargets()`, `addTaskToDatanode()`, `hasAllInternalBlocks()`, `chooseSource4SimpleReplication()`, `createReplicationWork()`, and `findLeavingServiceSources()`.

## Control Flow

`chooseTargets()` delegates to `BlockPlacementPolicy.chooseTarget()` unless the block is marked deleted (`NO_ACK`-style deletion), in which case no targets are chosen. `addTaskToDatanode()` decides which command to enqueue after targets are set. If the block lacks rack diversity but all internal blocks are present, it chooses a source from the rack with the most source nodes and enqueues EC internal-block replication to the source datanode. If decommissioning or live entering-maintenance replicas exist and all internal blocks are present, it finds leaving-service sources whose internal block index is not already present on an in-service source and replicates those internal blocks to targets. Otherwise it sends a full `BlockECReconstructionInfo` task to the first target datanode.

`createReplicationWork()` computes the internal block length with `StripedBlockUtil`, creates a block ID offset by the internal block index, and enqueues it through `DatanodeDescriptor.addECBlockToBeReplicated()`.

## State and Persistence Behavior

This is transient scheduling state created by the reconstruction monitor. It does not persist work itself; it enqueues commands into `DatanodeDescriptor` queues, which are later drained on heartbeat.

## Dependencies and Integration Points

It depends on `BlockPlacementPolicy`, `BlockStoragePolicySuite`, `BlockInfoStriped`, `NumberReplicas`, `StripedBlockUtil`, `DatanodeDescriptor`, and datanode EC reconstruction protocol types. It is part of the block reconstruction pipeline in `BlockManager` and related redundancy monitors.

## Risks and Edge Cases

The critical correctness issue is mapping source node indexes to `liveBlockIndices`. Incorrect index alignment can replicate the wrong internal block. The optimized paths assume all internal blocks are present, including busy blocks for the coverage check. Target count may exceed leaving-service sources, so the code limits to the smaller count and can return false if no source is available.

## Test Signals

Signals include `TestReconstructStripedBlocks`, `TestReconstructStripedBlocksWithRackAwareness`, `TestDecommissionWithStriped`, `TestMaintenanceWithStriped`, `TestErasureCodingCorruption`, and `TestBlockInfoStriped`. Tests should assert rack-only simple replication, decommission/maintenance source selection, deleted-block target suppression, and internal block length/ID calculation.
