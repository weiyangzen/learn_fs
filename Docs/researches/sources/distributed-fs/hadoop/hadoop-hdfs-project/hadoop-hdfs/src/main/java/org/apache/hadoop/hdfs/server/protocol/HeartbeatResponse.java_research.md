<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/HeartbeatResponse.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/HeartbeatResponse.java

## Purpose

`HeartbeatResponse` is the NameNode's response to `DatanodeProtocol.sendHeartbeat`. It bundles commands for the DataNode, HA status for the NameNode, rolling-upgrade status, a full block-report lease ID, and whether the DataNode is considered slow.

## Important APIs and types

Fields are `DatanodeCommand[] commands`, `NNHAStatusHeartbeat haStatus`, `RollingUpgradeStatus rollingUpdateStatus`, `fullBlockReportLeaseId`, and `isSlownode`. Constructors support old and new forms with default `isSlownode=false`. Getters expose all fields.

## Control flow

The DataNode sends heartbeat metrics and receives this object. It processes commands, updates its view of active/standby NameNode HA state, tracks rolling upgrade, and uses the block-report lease ID before submitting a full block report.

## State and persistence behavior

The response is transient. It represents NameNode in-memory command queues, HA txid state, rolling-upgrade state, and block-report lease state.

## Dependencies and integration points

It integrates `DatanodeProtocol`, command subclasses, `NNHAStatusHeartbeat`, and `RollingUpgradeStatus`. It is central to DataNode liveness and NameNode-to-DataNode control.

## Risks and test signals

Risks include command ordering, null command arrays, stale HA txids, invalid block-report leases, and slow-node flag compatibility with older constructors. Tests should cover mixed command arrays, lease-request heartbeats, rolling upgrade propagation, HA state changes, and slow-node reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/HeartbeatResponse.java -->
