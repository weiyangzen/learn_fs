<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ServerCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ServerCommand.java

## Purpose

`ServerCommand` is the common base for protocol-specific commands sent from a NameNode to other HDFS server components.

## Important APIs and types

It stores a final integer `action`, exposes `getAction()`, and formats `toString()` as class name plus action code. `DatanodeCommand` and `NamenodeCommand` derive from it.

## Control flow

NameNode implementations construct concrete command subclasses with action constants from the relevant protocol. Receivers dispatch on `getAction()` and command subtype.

## State and persistence behavior

The action code is immutable and transient. Runtime side effects occur only when receivers process commands.

## Dependencies and integration points

It defines the shared shape used by DataNode and subordinate NameNode command channels and is serialized by protocol translators.

## Risks and test signals

Integer action spaces are protocol-specific, so using a command in the wrong channel can be ambiguous. Tests should cover action preservation, toString diagnostics, and translator behavior for unknown actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ServerCommand.java -->
