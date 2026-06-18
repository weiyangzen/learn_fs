<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaConf.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaConf.java

## Purpose
`GangliaConf` is a package-private value holder for per-metric Ganglia metadata: units, slope, `dmax`, and `tmax`.

## Important APIs and Types
The class exposes package-private getters and setters for `units`, `slope`, `dmax`, and `tmax`, plus `toString`. Defaults come from `AbstractGangliaSink` constants. `slope` may remain null to mean no explicit override.

## Control Flow
There is no complex flow. Instances are created by `AbstractGangliaSink.loadGangliaConf` and then mutated as each config type is parsed. Ganglia sinks read the object while emitting metrics.

## State and Persistence
State is in-memory only and scoped to a configured sink. It persists for the sink lifetime and is not synchronized.

## Dependencies and Integration Points
It is consumed by `GangliaSink30` and `GangliaSink31` during packet encoding. It depends on `AbstractGangliaSink.GangliaSlope`.

## Risks and Test Signals
The lack of validation means bad values are rejected only by the parser that sets them. The default null slope is intentional and must be interpreted by sink logic. Tests should cover default values, setter/getter behavior, null slope fallback, and `toString` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaConf.java -->
