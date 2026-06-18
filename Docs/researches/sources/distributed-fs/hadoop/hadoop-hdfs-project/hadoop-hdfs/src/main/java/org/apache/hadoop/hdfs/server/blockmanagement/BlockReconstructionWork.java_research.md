# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockReconstructionWork.java

## Purpose

`BlockReconstructionWork` is the abstract task model used by `BlockManager.computeReconstructionWorkForBlocks` to represent replication or erasure-coding reconstruction. It bundles the block, source datanodes, containing nodes, live storages, target choices, priority, and placement deficiency flags.

## Important APIs and types

- Constructor captures `BlockInfo`, `BlockCollection`, source nodes, containing nodes, live replica storages, required additional replicas, and priority.
- Accessors expose block, source path, block size, storage policy ID, source nodes, live storages, target storages, priority, and required replication count.
- `setNotEnoughRack` and `hasNotEnoughRack` mark reconstruction driven by placement-policy deficiency rather than only replica count.
- Abstract `chooseTargets(BlockPlacementPolicy, BlockStoragePolicySuite, Set<Node>)` delegates target selection to concrete replicated or striped work.
- Abstract `addTaskToDatanode(NumberReplicas)` attaches the computed task to a source datanode.

## Control flow

The base constructor snapshots block collection details needed for later target choice. Concrete subclasses set `targets` after invoking block placement and then enqueue replication or erasure-coding work on a source datanode. The containing-node list is returned as unmodifiable so target selection can exclude existing holders without allowing callers to corrupt the task model.

## State and persistence behavior

The class is an in-memory scheduling object. It stores selected targets and a placement-deficiency flag, but nothing is persisted directly. Durable block state changes happen elsewhere when datanodes execute tasks and report blocks.

## Dependencies and integration points

It connects `BlockManager`, `BlockPlacementPolicy`, `BlockStoragePolicySuite`, `BlockInfo`, `BlockCollection`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `NumberReplicas`, and reconstruction queues.

## Risks and edge cases

The task snapshots `srcPath`, block size, and storage policy at construction; if metadata changes before scheduling, subclasses must tolerate stale context. Source-node arrays differ between replicated and erasure-coded tasks. Resetting targets allows retry paths but requires callers to avoid using stale target arrays.

## Test signals

Tests should verify constructor field capture, unmodifiable containing-node view, not-enough-rack flag behavior, subclass target selection with exclusions, and add-task behavior for both replicated and erasure-coded reconstruction.
