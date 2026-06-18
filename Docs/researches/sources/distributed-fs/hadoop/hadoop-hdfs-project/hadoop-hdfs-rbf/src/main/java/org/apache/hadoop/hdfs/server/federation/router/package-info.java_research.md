# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/package-info.java

## Purpose
This package descriptor documents the core HDFS Federation router package, where `Router` acts as a transparent proxy and `RouterRpcServer` exposes NameNode client protocol to DFS clients.

## Important APIs, Types, And Functions
It applies `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` to `org.apache.hadoop.hdfs.server.federation.router`.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no local state or persistence. The file depends only on classification annotations and package-level Javadoc references.

## Integration Points
The descriptor sets compatibility expectations for the router package containing the RPC server, heartbeat services, quota manager, refresh services, and async/sync protocol modules.

## Risks
The package is private/evolving, so implementation details may change between Hadoop versions.

## Test Signals
Compilation and package Javadoc generation are the relevant checks.
