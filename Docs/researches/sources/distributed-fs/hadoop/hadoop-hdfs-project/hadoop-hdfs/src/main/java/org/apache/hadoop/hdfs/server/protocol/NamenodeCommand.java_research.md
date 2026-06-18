<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeCommand.java

## Purpose

`NamenodeCommand` is the concrete base for commands returned by the active NameNode to subordinate NameNodes, such as checkpoint or shutdown commands.

## Important APIs and types

The constructor accepts an action code and delegates to `ServerCommand`. `CheckpointCommand` is the main payload-bearing subclass in this group.

## Control flow

Subordinate NameNode RPC calls such as `startCheckpoint` receive a `NamenodeCommand`, inspect its action, and act accordingly.

## State and persistence behavior

Only the inherited immutable action code is stored. Runtime effects are handled by the receiving subordinate service.

## Dependencies and integration points

It depends on `ServerCommand` and `NamenodeProtocol` action constants. It integrates with secondary/backup NameNode checkpoint control.

## Risks and test signals

Risks are action-code mismatch and insufficient subtype handling in RPC translators. Tests should cover action propagation, checkpoint command downcasting, and unknown/shutdown command handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeCommand.java -->
