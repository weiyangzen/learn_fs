<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NodeRegistration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NodeRegistration.java

## Purpose

`NodeRegistration` is the shared interface for registration records sent to a NameNode by server-side HDFS participants.

## Important APIs and types

It declares `getAddress()`, `getRegistrationID()`, `getVersion()`, and `toString()`. `DatanodeRegistration` and `NamenodeRegistration` implement it.

## Control flow

Registration code consumes this interface to validate identity, layout version, and address regardless of whether the registering node is a DataNode or subordinate NameNode.

## State and persistence behavior

The interface owns no state. Implementations usually derive registration ID from persistent `StorageInfo`.

## Dependencies and integration points

It is part of the `server.protocol` registration contract and integrates with NameNode admission/compatibility checks.

## Risks and test signals

Risks are too-small abstraction boundaries: implementations may differ in equality, address source, or storage identity. Tests should cover both known implementations and any generic registration validation logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NodeRegistration.java -->
