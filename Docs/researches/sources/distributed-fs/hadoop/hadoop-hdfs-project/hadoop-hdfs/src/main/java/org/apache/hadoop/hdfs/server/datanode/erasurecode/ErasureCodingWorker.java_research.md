<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/ErasureCodingWorker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/ErasureCodingWorker.java

## Purpose

`ErasureCodingWorker` receives NameNode erasure-coding reconstruction commands from DataNode heartbeat handling and runs striped reconstruction tasks. It owns the reconstruction and striped-read thread pools.

## Important APIs, Types, And Functions

- Constructor reads EC reconstruction xmit weight and thread-count configuration, validates nonnegative weight, and initializes pools.
- `processErasureCodingTasks(Collection<BlockECReconstructionInfo>)` converts each protocol command to `StripedReconstructionInfo`, creates a `StripedBlockReconstructor`, submits valid tasks, and increments DataNode xmits-in-progress.
- `createReadService()` returns an `ExecutorCompletionService` backed by the striped read pool.
- `shutDown()` stops both pools.

## Control Flow

For each NameNode task, the worker builds source/target reconstruction metadata, constructs a reconstructor, checks whether missing internal blocks have valid targets, then queues work. Xmits are incremented when enqueued rather than when executing so the NameNode can throttle scheduling against queued work.

## State And Persistence

State includes the `DataNode`, `Configuration`, xmit weight, a bounded reconstruction pool, and a cached-style striped read pool. No reconstructed data is persisted here; task classes read and write block data.

## Dependencies And Integration Points

It integrates `BPOfferService`/heartbeat commands, `DataNode` xmit accounting, DFS EC configuration, `StripedReconstructionInfo`, `StripedBlockReconstructor`, and thread-pool utilities.

## Risks And Edge Cases

The reconstruction queue is unbounded, intentionally avoiding dropped tasks but risking memory growth under sustained overload. Invalid task construction is caught per task. Xmit accounting must be decremented by the task's `finally` path.

## Test Signals

Tests should cover config validation, pool construction, valid and invalid targets, xmit increments for queued work, exception isolation per task, read service creation, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/ErasureCodingWorker.java -->
