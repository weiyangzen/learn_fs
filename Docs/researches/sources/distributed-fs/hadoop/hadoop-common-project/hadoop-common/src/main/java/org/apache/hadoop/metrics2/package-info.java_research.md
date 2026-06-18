<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/package-info.java

## Purpose
This package descriptor is the user-facing overview for Hadoop Metrics 2.0. It explains the model of sources, sinks, records, tags, filters, mutable source libraries, JMX publication, configuration keys, and migration from the previous metrics system.

## Important APIs and Types
The file references the core contracts `MetricsSource`, `MetricsSink`, `MetricsCollector`, `MetricsRecordBuilder`, annotations such as `@Metrics` and `@Metric`, `DefaultMetricsSystem`, built-in filters, source helpers, and sink implementations. Its package annotations mark `org.apache.hadoop.metrics2` as public and evolving.

## Control Flow
There is no executable control flow. The Javadoc examples describe expected runtime flow: sources register with the default metrics system, sinks are configured under `[prefix].sink.[instance]`, and update cycles call `putMetrics` followed by `flush`.

## State and Persistence
The document describes persisted configuration in `hadoop-metrics2-[prefix].properties` or `hadoop-metrics2.properties`. It also describes runtime JMX exposure and filtering state managed by the metrics system.

## Dependencies and Integration Points
This documentation is the integration guide for Hadoop subsystems such as HDFS, YARN, RPC, and MapReduce that publish metrics. It also anchors compatibility expectations for third-party metrics sources and sinks.

## Risks and Test Signals
The largest risk is stale documentation, especially sink examples, filter precedence, migration names, and links. Tests cannot directly validate this file, so review should happen when metrics configuration parsing, annotations, or built-in sink names change. Javadoc generation should remain clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/package-info.java -->
