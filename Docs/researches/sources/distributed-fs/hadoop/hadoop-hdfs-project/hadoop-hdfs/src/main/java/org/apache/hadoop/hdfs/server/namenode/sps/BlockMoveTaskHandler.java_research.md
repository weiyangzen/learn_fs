# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockMoveTaskHandler.java

## Purpose

`BlockMoveTaskHandler` is the SPS abstraction for submitting concrete block movement tasks. It decouples the Storage Policy Satisfier from whether a move is sent directly to a DataNode or scheduled through NameNode/DataNode heartbeat mechanisms.

## Important APIs, Types, And Functions

The interface declares `submitMoveTask(BlockMovingInfo blkMovingInfo) throws IOException`. `BlockMovingInfo` carries block, source, target, and storage-type movement details.

## Control Flow

Implementations receive a planned block move from SPS scheduling code and submit it to the chosen transport. This interface itself has no control flow beyond the checked exception contract.

## State And Persistence Behavior

The interface has no state and no persistence. Implementations are expected to interact with live DataNode/NameNode channels and rely on later block reports or movement completion notifications for progress.

## Dependencies And Integration Points

It depends on `BlockStorageMovementCommand.BlockMovingInfo` and is mirrored by `Context.submitMoveTask`. It integrates with `StoragePolicySatisfier` block-move scheduling and movement-attempt tracking.

## Risks And Edge Cases

Implementations must handle duplicate submissions, unavailable DataNodes, stale storage reports, and partial failures without losing retry visibility. Throwing `IOException` should leave higher layers able to retry or requeue the file.

## Test Signals

Tests should mock implementations and verify SPS submits the expected `BlockMovingInfo`, propagates or handles `IOException`, and records attempted items only when submission semantics warrant it.
