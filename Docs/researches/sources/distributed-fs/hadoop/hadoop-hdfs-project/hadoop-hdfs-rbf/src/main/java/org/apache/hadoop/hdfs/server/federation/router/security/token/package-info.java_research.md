# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/package-info.java

## Purpose
This descriptor documents token secret-manager implementations for router security.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.router.security.token` and notes that implementations should extend Hadoop's abstract delegation token secret manager.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no local state or persistence. The Javadoc references Hadoop delegation token secret manager contracts.

## Integration Points
The package contains SQL and ZooKeeper token persistence implementations selected by router security configuration.

## Risks
The package is private/evolving and not intended for stable external use.

## Test Signals
Compilation and generated package docs are sufficient.
