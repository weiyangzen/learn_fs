# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/package-info.java

## Purpose
This descriptor documents the router security package, including the security manager and token store implementations.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.router.security`.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no state or persistence. Dependencies are Hadoop classification annotations.

## Integration Points
The descriptor covers the security manager package consumed by router RPC and WebHDFS security paths.

## Risks
The package is private/evolving and may change without public compatibility guarantees.

## Test Signals
Compilation and package documentation generation are adequate.
