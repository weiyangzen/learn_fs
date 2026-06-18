<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetricsInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetricsInfo.java

## Purpose
`JvmMetricsInfo` centralizes the `MetricsInfo` names and descriptions emitted by `JvmMetrics`.

## Important APIs and Types
It is an enum implementing `MetricsInfo`. Constants include the record `JvmMetrics`, memory gauges, GC counters, thread gauges, log counters, pause counters, and GC percentage. `description()` returns the configured text and `name()` is inherited from enum constants.

## Control Flow
There is no dynamic flow beyond enum initialization and simple method calls. `JvmMetrics` passes these constants to `MetricsRecordBuilder`.

## State and Persistence
Each enum constant stores one immutable description string for the JVM lifetime.

## Dependencies and Integration Points
The enum is used by metrics source code and potentially tests expecting stable metric names. It depends on metrics2 `MetricsInfo` and Hadoop audience annotations.

## Risks and Test Signals
Renaming enum constants changes metric names and can break dashboards. Descriptions are user-facing in sinks such as Prometheus. Tests should validate emitted `JvmMetrics` records include these names and that `toString` remains diagnostic rather than a metric identity dependency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetricsInfo.java -->
