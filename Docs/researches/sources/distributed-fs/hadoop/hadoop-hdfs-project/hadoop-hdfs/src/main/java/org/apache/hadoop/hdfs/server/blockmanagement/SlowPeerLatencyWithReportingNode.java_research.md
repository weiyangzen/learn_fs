<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerLatencyWithReportingNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerLatencyWithReportingNode.java

## Purpose

`SlowPeerLatencyWithReportingNode` records one reporting DataNode's latency evidence against a slow peer.

## Important APIs and types

The immutable Jackson fields are `ReportingNode`, `ReportedLatency`, `MedianLatency`, `MadLatency`, and `UpperLimitLatency`. The class implements `Comparable` by reporting-node string and overrides equality/hash over all fields.

## Control flow

`SlowPeerTracker` creates one instance for each valid non-stale report. Sorted sets use `compareTo` to order reports by reporting node.

## State and persistence behavior

Instances are immutable diagnostic snapshots. They are serialized as part of `SlowPeerJsonReport` and are not otherwise persisted.

## Dependencies and integration points

It depends on Jackson and Apache Commons equality builders. It bridges `OutlierMetrics` values from DataNode reports into the slow-peer JSON schema.

## Risks and edge cases

`compareTo` compares only reporting node while `equals` also compares latency values. In `TreeSet`, two reports from the same reporting node compare equal even if latency fields differ; this matches the one-report-per-reporter model but is important if data is constructed manually.

## Test signals

Tests should cover JSON field names, ordering by reporting node, equality/hash with changed latency fields, and TreeSet replacement/deduplication semantics for same reporting node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SlowPeerLatencyWithReportingNode.java -->
