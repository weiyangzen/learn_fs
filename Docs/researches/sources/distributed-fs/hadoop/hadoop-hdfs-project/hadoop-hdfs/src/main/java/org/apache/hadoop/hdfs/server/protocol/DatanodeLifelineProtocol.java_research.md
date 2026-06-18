<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeLifelineProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeLifelineProtocol.java

## Purpose

`DatanodeLifelineProtocol` defines the lightweight DataNode-to-NameNode RPC used to send lifeline messages separate from full heartbeats. Lifelines keep a DataNode from being considered dead while avoiding the full command-return path.

## Important APIs and types

The interface is annotated with `@KerberosInfo`, using NameNode and DataNode principal keys. `sendLifeline(...)` is marked `@Idempotent` and carries the DataNode registration, storage reports, cache capacity/usage, transfer and xceiver counts, failed volume count, and `VolumeFailureSummary`.

## Control flow

The DataNode periodically calls `sendLifeline` with status data. The NameNode updates liveness/health information but the method returns `void`, so this channel does not deliver `DatanodeCommand` arrays.

## State and persistence behavior

The protocol mutates NameNode in-memory DataNode liveness and storage-health state through the server implementation. No persistent state is written by the interface itself.

## Dependencies and integration points

It shares most heartbeat payload types with `DatanodeProtocol.sendHeartbeat` and is included in `NamenodeProtocols`, the full NameNode RPC surface. Security depends on configured Kerberos principals.

## Risks and test signals

Risks include skew between lifeline and heartbeat payload semantics, null volume summaries, and over-trusting stale storage reports. Tests should cover lifeline-only liveness extension, authentication principal selection, and behavior when lifelines report failed volumes without returning commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeLifelineProtocol.java -->
