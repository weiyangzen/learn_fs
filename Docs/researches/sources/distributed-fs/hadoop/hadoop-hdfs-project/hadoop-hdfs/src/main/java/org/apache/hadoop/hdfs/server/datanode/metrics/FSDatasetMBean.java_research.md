# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/metrics/FSDatasetMBean.java

## Purpose

`FSDatasetMBean` defines the stable JMX/metrics view of DataNode dataset storage state. It exposes capacity, usage, failure, cache, scanner, and async deletion metrics and extends `MetricsSource`.

## Important APIs, Control Flow, and State

The interface declares getters for block-pool used, total DFS used, capacity, remaining, storage info, failed volume count and locations, last failure date, estimated lost capacity, cache used/capacity, cached and failed cache/uncache block counts, last directory scanner finish time, and pending async deletions. Implementations provide the actual state; this interface has no control flow.

The persistence behavior is indirect: values reflect live dataset state, volume failure records, cache manager counters, and scanner timestamps. Because this is a published MBean-style interface, method names are part of the observable management contract.

## Dependencies, Integration, Risks, and Tests

Dependencies are minimal: `MetricsSource` and `IOException`. Integration is through `FsDatasetImpl` and `DataNodeMetricHelper`.

Risks include incompatible method changes breaking JMX/metrics consumers and expensive implementations blocking metrics collection. Tests should verify implementing classes publish all gauges/tags and maintain expected values through volume failure, cache, scanner, and async deletion events.
