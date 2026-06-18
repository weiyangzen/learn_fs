<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicationWork.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicationWork.java

## Purpose

`ReplicationWork` is the concrete `BlockReconstructionWork` for normal replicated-block reconstruction. It chooses target storages and enqueues replication work on a single source DataNode.

## Important APIs and types

The constructor takes a `BlockInfo`, owning `BlockCollection`, selected source node array, containing nodes, live replica storages, additional replica count, and priority. It overrides `chooseTargets` and `addTaskToDatanode`.

## Control flow

Construction asserts exactly one source node and increments that node's pending-replication-without-targets counter. `chooseTargets` calls the configured `BlockPlacementPolicy.chooseTarget` unless the block has been deleted, then stores the chosen targets and always decrements the pending counter in a `finally` block. `addTaskToDatanode` calls `addBlockToBeReplicated` on the source node.

## State and persistence behavior

The object is transient scheduling state. It mutates the source DataNode's pending counters and task queues, but it is not itself persisted.

## Dependencies and integration points

It integrates `BlockReconstructionWork`, `BlockPlacementPolicy`, `BlockStoragePolicySuite`, `DatanodeDescriptor`, `DatanodeStorageInfo`, and `NumberReplicas`. It is used by BlockManager reconstruction scheduling for replicated blocks, distinct from erasure-coding work.

## Risks and edge cases

The single-source assertion is central; callers must not pass multiple source nodes. Deleted blocks skip placement to avoid sending invalid `NO_ACK`-sized work. Placement can return null/empty targets, but the task enqueue method still returns true and delegates to source-node handling.

## Test signals

Tests should verify source counter increment/decrement on success and exception, target choice arguments, deleted-block skip behavior, source task enqueue, and assertion/validation of single-source construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicationWork.java -->
