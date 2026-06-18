# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/DatanodeLifelineProtocol.proto

## Purpose

`DatanodeLifelineProtocol.proto` defines the private stable RPC used by DataNodes to send a lightweight lifeline to the NameNode. The source was read as a complete 43-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.datanodelifeline`, Java outer class `DatanodeLifelineProtocolProtos`, and imports `DatanodeProtocol.proto`. It defines an empty `LifelineResponseProto` and service `DatanodeLifelineProtocolService` with `sendLifeline(hadoop.hdfs.datanode.HeartbeatRequestProto)`.

## Control Flow

The service deliberately reuses `HeartbeatRequestProto` as its request payload but returns an empty response. Unlike a full heartbeat, lifeline responses do not dispatch NameNode commands. The flow lets a DataNode signal liveness and storage/report context without invoking normal command handling.

## State and Persistence Behavior

The proto has no persisted state. Implementations update in-memory NameNode liveness/health tracking based on heartbeat-like data. It indirectly affects failure detection timing but does not journal namespace changes.

## Dependencies and Integration Points

It depends on `DatanodeProtocol.proto` for heartbeat schema. Integration points include DataNode-to-NameNode RPC translators, NameNode heartbeat/lifeline managers, and HA/slow-node monitoring that consumes heartbeat-style metrics.

## Risks and Edge Cases

Compatibility risk is concentrated in the reused heartbeat message: new heartbeat fields may appear in lifeline requests even though no commands are returned. Implementations must not accidentally treat lifeline as a full heartbeat or issue commands on its empty response path.

## Test Signals

Tests should verify that lifelines update liveness, return no commands, tolerate older heartbeat messages without newer optional fields, and do not interfere with normal heartbeat command delivery.
