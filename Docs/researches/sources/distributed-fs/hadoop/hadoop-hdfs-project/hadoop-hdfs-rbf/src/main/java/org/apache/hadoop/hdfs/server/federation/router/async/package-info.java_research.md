# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/package-info.java

## Purpose
This package descriptor marks the router async package as private and evolving and documents its role as the non-blocking operation layer for HDFS Federation router RPCs.

## Important APIs, Types, And Functions
The file declares package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Evolving` for `org.apache.hadoop.hdfs.server.federation.router.async`.

## Control Flow
There is no runtime control flow.

## State, Persistence, And Dependencies
There is no state or persistence. The only dependencies are Hadoop classification annotations.

## Integration Points
The annotations communicate compatibility expectations to downstream Hadoop developers and generated docs.

## Risks
The package is explicitly not a stable public API, so external users should not depend on these implementation classes.

## Test Signals
No direct tests are required beyond compilation and annotation checks.
