<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FinalizeCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FinalizeCommand.java

## Purpose

`FinalizeCommand` tells a DataNode to finalize a previous HDFS upgrade for a specific block pool.

## Important APIs and types

The class extends `DatanodeCommand` with action `DatanodeProtocol.DNA_FINALIZE`. It stores `blockPoolId`, has a private no-argument constructor for serialization, a public constructor taking the block pool ID, and `getBlockPoolId()`.

## Control flow

The NameNode returns this command through the DataNode command channel after upgrade finalization is appropriate. The DataNode reads the block pool ID and finalizes local storage for that pool.

## State and persistence behavior

The command is transient, but processing it changes persistent DataNode storage by removing rollback state for the targeted block pool.

## Dependencies and integration points

It depends on `DatanodeProtocol` action constants and DataNode storage-upgrade code. It is serialized through DataNode command RPC translators.

## Risks and test signals

Risks include a null/wrong block pool ID, finalizing storage too early, and command loss during heartbeat retry. Tests should cover command serialization, correct pool targeting in federated clusters, and DataNode storage state after finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/FinalizeCommand.java -->
