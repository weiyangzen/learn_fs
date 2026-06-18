<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Metrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Metrics.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Metrics.java` defines mutable metrics for NFSv3 gateway RPC activity, bytes, and selected latency quantiles. The source was read as a complete 219-line file for this report.

## Important APIs, Types, and Functions

`Nfs3Metrics` is annotated with Metrics2 annotations. It owns `MutableRate` fields for NFSv3 procedures, `MutableCounterLong` fields for bytes, quantile arrays for read/write/commit latencies, a `MetricsRegistry`, gateway name, and `JvmMetrics`. `create` registers the source with `DefaultMetricsSystem`; `add*` methods update rates and quantiles.

## Control Flow

Construction tags the registry with session ID and creates quantiles for configured percentile intervals. RPC handlers call `addGetattr`, `addRead`, `addWrite`, `addCommit`, and related methods with nanosecond latencies; read/write/commit additionally feed quantile trackers.

## State and Persistence Behavior

Metrics are in-memory counters/rates/quantiles exported through Hadoop Metrics2. They reset on process restart and do not persist to HDFS.

## Dependencies and Integration Points

It integrates Metrics2 annotations, `DefaultMetricsSystem`, `JvmMetrics`, DFS metrics session ID, and `NfsConfigKeys.NFS_METRICS_PERCENTILES_INTERVALS_KEY`.

## Risks and Edge Cases

Empty percentile intervals produce empty quantile arrays, which is valid. Incorrect latency units would skew dashboards because comments and APIs assume nanoseconds.

## Test Signals

Metrics registration tests, RPC handler tests that assert counters/rates move, and configured percentile interval tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Metrics.java -->
