<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerJsonReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerJsonReport.java

## Purpose

`SlowPeerJsonReport` is a Jackson DTO that groups all valid reports against one slow DataNode for JSON exposure.

## Important APIs and types

The immutable fields are `SlowNode` and `SlowPeerLatencyWithReportingNodes`, both annotated with `@JsonProperty`. Getters expose the slow node ID and sorted reporting-node latency set. Equality and hashing use Apache Commons builders over both fields.

## Control flow

There is no algorithm beyond construction and object comparison. `SlowPeerTracker` creates instances after filtering stale reports and top-N selecting nodes.

## State and persistence behavior

Instances are immutable and transient. Their only persistence-like behavior is JSON serialization for diagnostics or JMX/HTTP consumers.

## Dependencies and integration points

It depends on Jackson annotations, `SortedSet`, `SlowPeerLatencyWithReportingNode`, and `SlowPeerTracker`.

## Risks and edge cases

Equality depends on the sorted set contents. If the set comparator is inconsistent with equality, set membership and object equality can diverge. The class is package-private and final, so schema changes must be coordinated with tracker JSON consumers.

## Test signals

Tests should cover JSON field names, equality/hash behavior, empty reporting sets, and stable ordering inherited from `SlowPeerLatencyWithReportingNode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerJsonReport.java -->
