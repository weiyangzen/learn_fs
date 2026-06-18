# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/SPSService.java

## Purpose

`SPSService` is the lifecycle and queue-management interface for the Storage Policy Satisfier service. It lets the NameNode initialize, start, stop, query, feed, and notify SPS implementations.

## Important APIs, Types, And Functions

The interface declares `init`, `start`, `stopGracefully`, `stop`, `isRunning`, `addFileToProcess`, `addAllFilesToProcess`, `processingQueueSize`, `getConf`, `markScanCompletedForPath`, and `notifyStorageMovementAttemptFinishedBlk`.

## Control Flow

NameNode code initializes the service with a `Context`, starts it in a configured `StoragePolicySatisfierMode`, and submits file or directory scan results as `ItemInfo` queues. Implementations expose queue size for monitoring, mark directory scans complete, handle DataNode block movement completion reports, and stop either gracefully or forcefully with optional hint cleanup.

## State And Persistence Behavior

The interface itself has no state. Implementations maintain in-memory queues, daemon threads, attempted-item tracking, DataNode caches, and configuration. Persistent SPS requests live in NameNode hints/xAttrs that implementations remove through `Context`.

## Dependencies And Integration Points

It depends on `Context`, `Configuration`, `ItemInfo`, `StoragePolicySatisfierMode`, `DatanodeInfo`, `StorageType`, and `Block`. It is the top-level contract implemented by `StoragePolicySatisfier` and used by NameNode SPS plumbing.

## Risks And Edge Cases

Implementations must define clear semantics for force stop versus graceful stop, avoid accepting work before `init`, handle duplicate `start` or `stop` calls, and safely process movement completion notifications for blocks no longer tracked. Queue-size reporting can be transient under concurrent worker activity.

## Test Signals

Tests should cover lifecycle ordering, graceful and forced stop behavior, queue additions for single files and directory batches, scan-complete handling, configuration access, running-state transitions, and block movement completion notification paths.
