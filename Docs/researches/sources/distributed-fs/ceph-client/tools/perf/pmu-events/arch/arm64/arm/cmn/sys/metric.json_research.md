<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/metric.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/metric.json

## Purpose
This JSON file defines 8 derived perf metrics for Arm cmn. The expressions cover derived CMN uncore perf metrics built from event expressions and are consumed by the `pmu-events` generator as metric rows rather than raw counter encodings. The source was read as a complete 75-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `MetricName` (8), `BriefDescription` (8), `MetricGroup` (8), `MetricExpr` (8), `ScaleUnit` (8), `Unit` (8), `Compat` (8). Metric names include `slc_miss_rate`, `hnf_message_retry_rate`, `sf_hit_rate`, `mc_message_retry_rate`, `rni_actual_read_bandwidth.all`, `rni_actual_write_bandwidth.all`, `rni_retry_rate`, `sbsx_actual_write_bandwidth.all`. Metric groups include `cmn`. `MetricExpr` references raw events such as architectural aliases, `duration_time`, and model-defined event names; `ScaleUnit` controls perf's display scaling.

## Control Flow, State, and Persistence
`jevents.py` parses each `MetricExpr` through `metric.ParsePerfJson()`, simplifies it, and emits generated `pmu-events.c` metric tables. At runtime `perf list` and metricgroup code expose these names and evaluate the expressions from simultaneously counted events. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include stale event names inside expressions, denominator-zero or multiplexing-sensitive ratios, wrong scale units, metrics that depend on events omitted from this CPU directory, and semantic drift when a raw event definition changes. Test signals include `metric_test.py`, `jevents.py` generation, `perf list --metrics`, and sample `perf stat -M` runs on the matching CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/metric.json -->
