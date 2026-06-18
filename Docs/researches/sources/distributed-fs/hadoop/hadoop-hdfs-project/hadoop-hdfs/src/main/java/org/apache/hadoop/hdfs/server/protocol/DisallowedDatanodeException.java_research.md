<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DisallowedDatanodeException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DisallowedDatanodeException.java

## Purpose

`DisallowedDatanodeException` reports that a DataNode is not allowed to register or communicate with a NameNode because include/exclude host rules rejected it.

## Important APIs and types

The exception extends `IOException` and has constructors accepting a `DatanodeID` plus an optional reason. The default reason states that the host is not in the include list.

## Control flow

NameNode registration or heartbeat validation throws this exception after checking host admission rules. The message includes the reason and DataNode identity for logs and client-side diagnostics.

## State and persistence behavior

There is no state beyond the serialized exception message and `serialVersionUID`. Include/exclude state is maintained elsewhere by NameNode host managers.

## Dependencies and integration points

It depends only on `DatanodeID` and Java `IOException`. It integrates with DataNode registration, decommission/exclusion handling, and administrative host-list configuration.

## Risks and test signals

The main risk is diagnostic clarity: the exception should expose enough identity and reason without leaking unrelated internals. Tests should cover default and custom reasons, registration rejection, and DataNode behavior after receiving the exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/DisallowedDatanodeException.java -->
