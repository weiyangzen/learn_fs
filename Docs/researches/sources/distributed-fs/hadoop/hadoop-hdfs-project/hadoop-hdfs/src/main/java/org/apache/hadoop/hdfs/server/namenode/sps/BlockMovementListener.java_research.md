# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockMovementListener.java

## Purpose

`BlockMovementListener` is the callback interface used to notify SPS that block movement attempts have finished or been tried, allowing SPS to recheck storage policy satisfaction and retry as needed.

## Important APIs, Types, And Functions

It declares `notifyMovementTriedBlocks(Block[] moveAttemptFinishedBlks)`. The input array contains blocks whose movement attempt completion was reported.

## Control Flow

DataNode or NameNode integration code calls the listener with finished blocks. SPS then consumes the blocks through attempted-item tracking, removes completed block entries, and requeues associated files for policy re-evaluation.

## State And Persistence Behavior

The interface has no state. Movement completion state is transient and maintained by implementations such as `BlockStorageMovementAttemptedItems` and the owning `SPSService`.

## Dependencies And Integration Points

It depends on HDFS protocol `Block` and integrates with `Context.notifyMovementTriedBlocks`, `SPSService.notifyStorageMovementAttemptFinishedBlk`, and DataNode block movement reports.

## Risks And Edge Cases

Callbacks can contain duplicate or stale block IDs, blocks from unknown attempts, or completions for only one target storage location. Implementations need idempotent handling and should not assume success means the file's policy is already satisfied.

## Test Signals

Tests should notify known, unknown, duplicate, and partial movement blocks and verify attempted-item queues, retry queues, and policy recheck behavior.
