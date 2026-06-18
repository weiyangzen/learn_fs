<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink30.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink30.java

## Purpose
`GangliaSink30` emits metrics2 records using the Ganglia 3.0 protocol. It can publish either dense metrics through a cache or sparse metrics directly from each update.

## Important APIs and Types
The class extends `AbstractGangliaSink`. Key methods are `init`, `appendPrefix`, `putMetrics`, `calculateSlope`, and protected `emitMetric`. It owns a `MetricsCache` for dense mode and `useTagsMap` for context-specific tag inclusion configured by `tagsForPrefix.*`.

## Control Flow
`init` delegates shared setup, enables comma list parsing, and loads tag inclusion rules. `putMetrics` constructs `context.record[.tag=value]` group/name prefixes. In dense mode it updates `MetricsCache` and emits every cached metric for the record; in sparse mode it emits only metrics in the current record. For each metric it visits the metric to determine Ganglia type/slope, merges configured `GangliaConf`, and writes a Ganglia 3.0 XDR packet.

## State and Persistence
Runtime state is the dense metrics cache, tag inclusion map, and inherited socket/buffer configuration. No durable state is written by the class itself.

## Dependencies and Integration Points
It integrates metrics2 with Ganglia 3.0 gmond endpoints. It consumes `MsInfo.Context` and `MsInfo.Hostname` to avoid duplicating those tags in metric names.

## Risks and Test Signals
Dense mode retains prior metric values and is sensitive to high-cardinality tags. `appendPrefix` includes raw tag values in names. Tests should cover tag rule parsing, all-tags wildcard, dense versus sparse behavior, slope precedence, null value/type guard paths, XDR packet fields, and IOException wrapping in `MetricsException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink30.java -->
