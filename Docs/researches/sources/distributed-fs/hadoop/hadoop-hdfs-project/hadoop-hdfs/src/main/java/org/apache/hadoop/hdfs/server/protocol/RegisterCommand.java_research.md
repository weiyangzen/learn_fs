<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RegisterCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RegisterCommand.java

## Purpose

`RegisterCommand` tells a DataNode to register or re-register with the NameNode.

## Important APIs and types

It extends `DatanodeCommand` with action `DatanodeProtocol.DNA_REGISTER` and exposes a singleton `REGISTER`.

## Control flow

The NameNode returns this command in a heartbeat response when it needs a DataNode to refresh registration. The class comment notes it cannot be combined with other commands because DataNode processing skips the rest of the response after handling registration.

## State and persistence behavior

There is no payload. Processing triggers a DataNode registration handshake that refreshes NameNode in-memory DataNode state.

## Dependencies and integration points

It depends on `DatanodeProtocol` action codes and DataNode heartbeat command dispatch.

## Risks and test signals

Risks include combining it with other commands, causing skipped work, or sending it repeatedly during registration failures. Tests should cover singleton serialization, command ordering, and DataNode behavior when registration is required mid-heartbeat cycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/RegisterCommand.java -->
