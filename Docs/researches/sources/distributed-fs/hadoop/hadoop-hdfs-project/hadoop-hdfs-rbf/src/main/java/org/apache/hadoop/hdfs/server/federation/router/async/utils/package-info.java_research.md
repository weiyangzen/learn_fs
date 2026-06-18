# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/package-info.java

## Purpose
This package descriptor documents the async utility package and marks it private/evolving.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.router.async.utils`.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no state or persistence. Dependencies are Hadoop classification annotations.

## Integration Points
The descriptor applies compatibility metadata to the DSL classes used by async router modules.

## Risks
The package is not a public stable API, so external consumers should avoid binding to it.

## Test Signals
Compilation and generated API documentation are sufficient signals.
