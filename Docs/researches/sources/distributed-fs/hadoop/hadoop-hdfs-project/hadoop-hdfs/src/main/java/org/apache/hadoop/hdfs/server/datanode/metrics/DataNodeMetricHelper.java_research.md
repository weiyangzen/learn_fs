# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/DataNodeMetricHelper.java

## Purpose

`DataNodeMetricHelper` adapts an `FSDatasetMBean` into Hadoop metrics2 records. It centralizes the gauge/tag population used when the dataset exposes itself as a `MetricsSource`.

## Important APIs, Control Flow, and State

The sole API is static `getMetrics(MetricsCollector, FSDatasetMBean, String)`. It rejects null beans, uses the bean class name as the record name, sets the metrics context, and adds capacity, DFS-used, remaining, storage info, failed volume counts/times/capacity lost, cache usage/capacity, cached block counts, failed cache/uncache counts, last directory scanner finish time, and pending async deletion count.

There is no retained state or persistence. The control flow is a single builder-style chain against the collector, and bean getter `IOException`s propagate to the caller.

## Dependencies, Integration, Risks, and Tests

Dependencies include `MetricsCollector`, `MetricsTag`, `Interns`, and `FSDatasetMBean`. It integrates with `FsDatasetImpl` metrics publication.

Risks include metric-name compatibility, exceptions from bean getters aborting the whole snapshot, and typos/descriptions becoming externally visible metrics contract. Tests should verify null handling, all expected metric names/tags, and propagation of bean exceptions.
