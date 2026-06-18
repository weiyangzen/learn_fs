<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NNHAStatusHeartbeat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NNHAStatusHeartbeat.java

## Purpose

`NNHAStatusHeartbeat` carries the NameNode's HA service state and most recent transaction ID in heartbeat responses to DataNodes.

## Important APIs and types

The class stores an `HAServiceState` and a txid initialized from constructor input. The default invalid txid constant is `HdfsServerConstants.INVALID_TXID`. Getters are `getState()` and `getTxId()`.

## Control flow

The NameNode attaches this object to `HeartbeatResponse`. DataNodes use it to decide whether they are talking to an active or standby NameNode and what edit-log point the NameNode has reached.

## State and persistence behavior

The object is immutable from callers' perspective and transient. It reflects NameNode HA state and edit transaction progress maintained elsewhere.

## Dependencies and integration points

It integrates `HAServiceProtocol.HAServiceState`, `HeartbeatResponse`, and DataNode failover/actor logic.

## Risks and test signals

Risks include stale txids during failover, null state, and DataNodes misclassifying standby responses. Tests should cover active-to-standby transitions, invalid txid defaults, and heartbeat behavior during HA failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NNHAStatusHeartbeat.java -->
