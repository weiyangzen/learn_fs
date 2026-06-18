<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingReconstructionBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingReconstructionBlocks.java

## Purpose

`PendingReconstructionBlocks` tracks block reconstruction commands that have been issued but not yet satisfied. It lets BlockManager avoid overscheduling the same block and detect reconstruction attempts that timed out.

## Important APIs and types

The class owns `pendingReconstructions`, `timedOutItems`, a monitor `Daemon`, timeout configuration, and `timedOutCount`. APIs include `start`, `stop`, `increment`, `decrement`, `remove`, `clear`, `size`, `getNumReplicas`, `getTimedOutBlocks`, `getNumTimedOuts`, `metaSave`, and `getTargets`. `PendingBlockInfo` stores timestamp and target storages.

## Control flow

`increment` inserts or refreshes a block entry and adds unique target storages. `decrement` removes target entries matching a DataNode descriptor and deletes the block when no targets remain. The monitor sleeps for the smaller of the timeout and five minutes, scans pending entries under lock, moves expired blocks to `timedOutItems`, increments NameNode timeout metrics, and removes them from pending. `getTimedOutBlocks` drains the timeout list and advances the cumulative count.

## State and persistence behavior

All state is in-memory and protected by explicit synchronization on the maps/lists. It is rebuilt from runtime scheduling, not persisted. The monitor lifecycle is controlled by `start` and `stop`.

## Dependencies and integration points

It integrates with `BlockManager`, `DatanodeStorageInfo`, NameNode metrics, metasave diagnostics, and the redundancy monitor.

## Risks and edge cases

Timeouts are coarse-grained, so retry timing can lag. `decrementReplicas` compares DataNode descriptor identity rather than storage identity. `metaSave` formats monotonic timestamps with `java.sql.Time`, which is diagnostic only. Interrupted monitor shutdown ignores interruption after join.

## Test signals

Tests should cover unique target accumulation, decrement-to-zero removal, timeout scanning, `getTimedOutBlocks` drain semantics, `getNumTimedOuts`, monitor start/stop, and metasave output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingReconstructionBlocks.java -->
