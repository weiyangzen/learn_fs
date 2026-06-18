<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricVisitor.java

## Purpose
`GangliaMetricVisitor` maps metrics2 metric values to Ganglia wire types and slopes without relying on concrete metric implementation classes.

## Important APIs and Types
It implements `MetricsVisitor`. `getType()` returns `int32`, `float`, or `double`; `getSlope()` returns `positive` for counters and null for gauges. Overloads handle int, long, float, and double gauges plus int and long counters.

## Control Flow
Each `AbstractMetric` calls back into the visitor through `metric.visit`. The visitor mutates its latest `type` and `slope` fields according to the metric overload. Sinks then read those fields immediately.

## State and Persistence
State is the last visited metric type and slope. It is reused by a sink instance and is not thread-safe, matching the Ganglia sink assumption that metrics sink calls are not concurrent.

## Dependencies and Integration Points
`GangliaSink30` uses the visitor before `emitMetric`; `GangliaSink31` inherits the same mapping. The class depends on metrics2 `MetricsInfo`, `MetricsVisitor`, and Ganglia slope enum.

## Risks and Test Signals
Long counters and long gauges are both emitted as `float`, which can lose precision for large values. Null slope for gauges relies on later fallback logic. Tests should exercise every visitor overload, repeated visits, and the sink slope precedence of explicit config over visitor-derived slope over default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricVisitor.java -->
