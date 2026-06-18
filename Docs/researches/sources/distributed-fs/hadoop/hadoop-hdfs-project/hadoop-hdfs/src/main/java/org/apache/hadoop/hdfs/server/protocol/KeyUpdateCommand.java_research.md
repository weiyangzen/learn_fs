<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/KeyUpdateCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/KeyUpdateCommand.java

## Purpose

`KeyUpdateCommand` tells a DataNode to update its exported block-token keys.

## Important APIs and types

The class extends `DatanodeCommand` with action `DatanodeProtocol.DNA_ACCESSKEYUPDATE`. It stores an `ExportedBlockKeys` object and exposes `getExportedKeys()`. The package-private default constructor creates an empty `ExportedBlockKeys` for serialization.

## Control flow

The NameNode includes this command in heartbeat responses when block-token keys change. The DataNode applies the provided keys to token validation/issuance paths.

## State and persistence behavior

The command is transient. Applying it mutates in-memory DataNode block-token key state; persistence and key rotation are handled by security/token managers.

## Dependencies and integration points

It depends on HDFS block-token security (`ExportedBlockKeys`), `DatanodeProtocol`, heartbeat command dispatch, and protobuf translators.

## Risks and test signals

Risks include missing key updates causing token failures, accepting empty/default keys, or command loss during heartbeat retry. Tests should cover key rotation propagation, serialization of current and all keys, and DataNode behavior with stale tokens before and after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/KeyUpdateCommand.java -->
