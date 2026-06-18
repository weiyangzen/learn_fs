<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DropSPSWorkCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DropSPSWorkCommand.java

## Purpose

`DropSPSWorkCommand` instructs a DataNode to drop pending Storage Policy Satisfier worker block-movement queues. It is part of the DataNode command channel used when SPS state must be reset or cancelled.

## Important APIs and types

The class extends `DatanodeCommand` and uses action `DatanodeProtocol.DNA_DROP_SPS_WORK_COMMAND`. It exposes a singleton `DNA_DROP_SPS_WORK_COMMAND` and a public no-argument constructor for serialization and construction.

## Control flow

The NameNode returns this command to a DataNode, usually via `HeartbeatResponse`. DataNode command handling dispatches on the action code and clears local SPS work queues.

## State and persistence behavior

The command has no payload beyond its action code. Runtime effects occur only when DataNode SPS worker queues process the command.

## Dependencies and integration points

It depends on `DatanodeCommand` and `DatanodeProtocol`. Integration points are NameNode SPS control logic, DataNode heartbeat command processing, and protobuf command translators.

## Risks and test signals

Risks include losing queued movement work unexpectedly or failing to clear stale work after SPS disablement. Tests should verify singleton/default serialization, action-code mapping, and DataNode queue behavior after receiving the command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DropSPSWorkCommand.java -->
