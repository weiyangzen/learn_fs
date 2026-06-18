<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressMetrics.java

## Purpose

`StartupProgressMetrics` adapts `StartupProgress` to Hadoop Metrics2/JMX. It emits overall elapsed time and percent complete plus per-phase count, elapsed time, total, and percent metrics.

## Important APIs and types

- Implements `MetricsSource`.
- `register(StartupProgress)` constructs and registers a source.
- Constructor registers with `DefaultMetricsSystem` under `StartupProgress`.
- `getMetrics(MetricsCollector, boolean)` builds a snapshot view and populates a metrics record.

## Control flow

On each metrics poll, the class calls `startupProgress.createView()`, adds overall counters/gauges, then iterates every `Phase` from the view and emits named metrics using the phase's stable name/description.

## State and persistence behavior

The only held state is a reference to `StartupProgress`. Metrics are emitted on demand; no durable persistence is performed. Registration in the default metrics system is process-global.

## Dependencies and integration points

Integrates startup progress with Metrics2, JMX, and NameNode monitoring. It depends on metric intern helpers, `MetricsRecordBuilder`, and phase names from `Phase`.

## Risks and edge cases

Repeated construction/register calls with the same source name can collide in the metrics system. Metric names are tied to enum names and should remain stable. Snapshot creation prevents mid-poll inconsistencies but may allocate during metrics collection.

## Test signals

`TestStartupProgressMetrics` should verify source registration and emitted metric values/names for representative phase and counter states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressMetrics.java -->
