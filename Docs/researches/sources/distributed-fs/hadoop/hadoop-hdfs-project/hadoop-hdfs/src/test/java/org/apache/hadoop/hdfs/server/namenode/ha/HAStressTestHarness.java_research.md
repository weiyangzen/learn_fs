# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/HAStressTestHarness.java

## Purpose

`HAStressTestHarness` is a reusable HA test utility that starts a MiniDFS HA cluster and attaches background threads for repeated failover and replication/deletion progress stimulation.

## Important APIs, Types, and Functions

The class owns a `Configuration`, `MiniDFSCluster`, `TestContext`, and configurable NameNode count. It exposes `setNumberOfNameNodes`, `startCluster`, `getFailoverFs`, `addReplicationTriggerThread`, `addFailoverThread`, `startThreads`, `stopThreads`, and `shutdown`. It uses `MiniDFSNNTopology.simpleHATopology`, `RepeatingTestThread`, `DataNodeTestUtils`, and `BlockManagerTestUtil.computeAllPendingWork`.

## Control Flow

The constructor sets small block size, short heartbeat/tail-edits periods, and high replication stream limits. `startCluster` builds an HA cluster with three DataNodes. Replication trigger threads periodically force deletion reports, heartbeats, and pending block work computation. Failover threads transition each NameNode to standby and the next to active in a ring, sleeping between cycles.

## State and Persistence Behavior

The harness mutates cluster HA role state and DataNode/BlockManager transient work queues. It does not create files itself, but tests using it typically persist namespace and block state while background activity runs.

## Dependencies and Integration Points

It integrates MiniDFSCluster HA topology, failover client configuration through `HATestUtil`, DataNode test hooks, block manager scheduling, and multithreaded test utilities.

## Risks and Edge Cases

The failover loop assumes node indices are valid and transitions are legal in sequence. Background threads can mask or expose races depending on interval choices. `shutdown` must stop threads before cluster teardown to avoid touching closed services.

## Test Signals

Consumers should observe no exceptions from `TestContext`, successful failover cycles, accelerated deletion/replication progress, and clean shutdown with all test threads stopped.
