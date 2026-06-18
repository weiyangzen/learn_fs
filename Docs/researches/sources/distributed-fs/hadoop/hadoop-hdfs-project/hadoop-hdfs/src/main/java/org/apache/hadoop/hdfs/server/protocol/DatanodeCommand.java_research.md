<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeCommand.java

## Purpose

`DatanodeCommand` is the abstract base for commands the NameNode returns to a DataNode, usually in `HeartbeatResponse` or block-report responses. It separates DataNode command classes from generic `ServerCommand` while preserving the protocol-specific integer action code.

## Important APIs and types

The only constructor is package-private and accepts an action code. Subclasses such as `RegisterCommand`, `FinalizeCommand`, `KeyUpdateCommand`, `DropSPSWorkCommand`, block commands, cache commands, and movement commands supply constants from `DatanodeProtocol`.

## Control flow

There is no additional control flow beyond delegating construction to `ServerCommand`. DataNode-side dispatch reads `getAction()` and downcasts/deserializes to the matching command payload.

## State and persistence behavior

The object stores only inherited immutable action state. It is serialized through the HDFS RPC/protobuf layer and has no persistence outside command delivery.

## Dependencies and integration points

It depends on `ServerCommand` and `DatanodeProtocol` action namespaces. The integration point is the NameNode-to-DataNode command path, especially heartbeat responses.

## Risks and test signals

Because the constructor is package-private, new commands must live in the protocol package or use existing constructors. Risks are action-code collisions and protobuf translator mismatch. Tests should verify each concrete command maps to the expected `DNA_*` code and that DataNode command dispatch handles singleton/default commands correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeCommand.java -->
