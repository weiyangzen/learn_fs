<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksStorageMoveAttemptFinished.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksStorageMoveAttemptFinished.java

## Purpose

`BlocksStorageMoveAttemptFinished` is the DataNode-to-NameNode report payload listing blocks whose storage movement attempts have finished, whether successful or failed.

## Important APIs and types

- Constructor accepts `Block[] moveAttemptFinishedBlocks`.
- `getBlocks()` returns the array.
- `toString()` formats all blocks for diagnostics.

## Control flow

After a DataNode storage movement attempt finishes, the DataNode reports the affected blocks. SPS attempt monitoring uses these reports to mark blocks complete, update timestamps, retry, or clean tracking.

## State and persistence behavior

This is a simple transport DTO with immutable array reference but mutable contents. It does not persist state itself.

## Dependencies and integration points

Works with SPS, DataNode block movement task handling, and `StoragePolicySatisfier.notifyStorageMovementAttemptFinishedBlk`.

## Risks and edge cases

The payload does not include explicit success/failure status per block, so higher layers infer completion from block reports and storage state. Array mutation after construction can change reported contents.

## Test signals

SPS attempted-items monitor tests and external SPS tests should cover report handling, timeout/retry behavior, and mixed successful/failed movement attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksStorageMoveAttemptFinished.java -->
