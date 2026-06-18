# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeLocalInfo.java

## Purpose
`DatanodeLocalInfo` is a small private/evolving value object for information available locally from a DataNode: software version, configuration version, and uptime in seconds.

## APIs and Behavior
The constructor initializes final fields. Getters expose each field, and `getDatanodeLocalReport()` returns a compact human-readable status line.

## State, Dependencies, and Integration
There is no persistence or mutation in this class. It is likely returned by DataNode-side admin/client commands that inspect a single local node rather than cluster-wide NameNode reports.

## Risks and Test Signals
Inputs are not validated, so null versions or negative uptime can be represented. Tests should cover report formatting, uptime units, and serialization/RPC compatibility for admin tooling.
