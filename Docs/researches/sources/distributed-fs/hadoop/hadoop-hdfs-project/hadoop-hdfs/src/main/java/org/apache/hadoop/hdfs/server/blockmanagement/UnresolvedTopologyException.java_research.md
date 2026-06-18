<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/UnresolvedTopologyException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/UnresolvedTopologyException.java

## Purpose

`UnresolvedTopologyException` signals failure to resolve a node's topology path, such as rack or network location, during block placement or topology-aware operations.

## Important APIs and types

The class extends `IOException`, defines `serialVersionUID`, and exposes a message constructor.

## Control flow

There is no internal algorithm. Callers throw it when topology resolution cannot produce a usable location.

## State and persistence behavior

The class has no mutable state beyond inherited exception fields. It is not persisted.

## Dependencies and integration points

It integrates with block placement policies, network topology mapping, and DataNode registration/placement paths that require resolved rack paths.

## Risks and edge cases

The exception preserves only caller-provided text, so diagnostics depend on including node and mapping context at throw sites.

## Test signals

Tests should cover topology mapper failures, invalid rack strings, and caller behavior that surfaces the exception without falling back to unsafe placement assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/UnresolvedTopologyException.java -->
