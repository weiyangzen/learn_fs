# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/FSClusterStats.java

## Purpose

`FSClusterStats` is a small placement-facing interface that exposes cluster load, stale-write avoidance, in-service datanode count, average xceiver load, average volume load, and per-storage-type stats. `DatanodeManager.newFSClusterStats()` creates the concrete anonymous implementation backed by `HeartbeatManager`.

## Important APIs and Types

Methods are `getTotalLoad()`, `isAvoidingStaleDataNodesForWrite()`, `getNumDatanodesInService()`, `getInServiceXceiverAverage()`, `getInServiceXceiverAverageForVolume()`, and `getStorageTypeStats()`. It uses `StorageType` and `StorageTypeStats`.

## Control Flow

Block placement policies ask this interface for load and storage-type context when choosing write targets. The implementation computes averages defensively, returning zero when no in-service nodes or volumes are available.

## State and Persistence Behavior

The interface is stateless. Values are runtime views over heartbeat-maintained statistics and stale-node policy.

## Dependencies and Integration Points

Primary consumers are block placement policies such as default, available-space, upgrade-domain, and rack-fault-tolerant policies. `DatanodeManager` mediates stale-write policy and `HeartbeatManager` supplies load and storage stats.

## Risks and Edge Cases

Average load semantics depend on the denominator: node average uses in-service datanode count, while volume average uses writable volume count. If administrative state accounting is wrong, placement may overuse decommissioning, maintenance, stale, or overloaded nodes.

## Test Signals

Signals include `TestReplicationPolicy`, `TestReplicationPolicyConsiderLoad`, `TestReplicationPolicyRatioConsiderLoadWithStorage`, available-space placement tests, and stale-node tests. Coverage should validate zero-denominator behavior and stale-write avoidance toggling.
