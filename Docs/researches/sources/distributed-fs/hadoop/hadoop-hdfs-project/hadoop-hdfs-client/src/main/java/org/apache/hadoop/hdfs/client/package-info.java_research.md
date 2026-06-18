# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/package-info.java

## Purpose
This package-info documents `org.apache.hadoop.hdfs.client` as the package providing administrative APIs for HDFS.

## Important APIs, types, and functions
It applies `@InterfaceAudience.Public` and `@InterfaceStability.Evolving` to the package, indicating public but evolving HDFS client APIs.

## Control flow
There is no executable control flow.

## State and persistence behavior
There is no runtime state or persistence.

## Dependencies and integration points
It imports Hadoop classification annotations and classifies the surrounding client API package, which includes public client-side administrative types.

## Risks and test signals
Build and javadoc checks should verify annotation resolution. API compatibility review should consider the package-level public/evolving contract.
