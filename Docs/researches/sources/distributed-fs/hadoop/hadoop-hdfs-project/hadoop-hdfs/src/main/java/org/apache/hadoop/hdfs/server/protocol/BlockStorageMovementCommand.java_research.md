<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockStorageMovementCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockStorageMovementCommand.java

## Purpose

`BlockStorageMovementCommand` instructs a DataNode to move blocks from source storage media to target DataNodes/storage media to satisfy HDFS storage policies.

## Important APIs and types

- Extends `DatanodeCommand`.
- Holds `blockPoolId` and `Collection<BlockMovingInfo>`.
- `BlockMovingInfo` carries `Block`, source DataNode, target DataNode, source storage type, and target storage type.
- Getters expose all movement fields; `addBlock` can replace the block in a `BlockMovingInfo`.

## Control flow

SPS constructs `BlockMovingInfo` tasks and submits them through its context. DataNodes receiving the command pass tasks to `ExternalSPSBlockMoveTaskHandler`, which schedules physical movement and later reports attempt completion.

## State and persistence behavior

The command is an in-memory/RPC DTO. Persistent effects occur after DataNode block movement and subsequent NameNode reports. The task collection and nested fields are mutable by reference.

## Dependencies and integration points

Directly integrates `StoragePolicySatisfier`, external SPS task handling, DataNode command processing, and `BlocksStorageMoveAttemptFinished` reports.

## Risks and edge cases

Source and target storage type correctness is essential; wrong pairings can move blocks to policy-incompatible media. `addBlock` mutability is unusual for a command DTO. There is no local validation for null nodes or same source/target combinations.

## Test signals

SPS tests should inspect generated `BlockMovingInfo` tasks, DataNode task handler behavior, success/failure reports, retries, and EC internal block movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockStorageMovementCommand.java -->
