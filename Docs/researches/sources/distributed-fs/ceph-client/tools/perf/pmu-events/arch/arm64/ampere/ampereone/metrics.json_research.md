<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/metrics.json

## Purpose
This JSON file defines 56 derived perf metrics for Ampere ampereone. The expressions cover derived perf metrics built from event expressions and are consumed by the `pmu-events` generator as metric rows rather than raw counter encodings. The source was read as a complete 387-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `MetricExpr` (55), `MetricName` (54), `BriefDescription` (54), `MetricGroup` (54), `ScaleUnit` (51), `ArchStdEvent` (2), `DefaultMetricgroupName` (2). Metric names include `branch_miss_pred_rate`, `bus_utilization`, `l1d_cache_miss_ratio`, `l1i_cache_miss_ratio`, `Miss_Ratio;l1d_cache_read_miss`, `l2_cache_miss_ratio`, `l1i_cache_read_miss_rate`, `l2d_cache_read_miss_rate`, `l1d_cache_miss_mpki`, `l1i_cache_miss_mpki`, `simd_percentage`, `crypto_percentage`, and 44 more. Metric groups include `branch`, `Bus`, `Miss_Ratio;L1D_Cache_Effectiveness`, `Miss_Ratio;L1I_Cache_Effectiveness`, `Cache`, `Miss_Ratio;L2_Cache_Effectiveness`, `Operation_Mix`, `InstructionMix`, `General`, `PEutilization`, and 7 more. `MetricExpr` references raw events such as architectural aliases, `duration_time`, and model-defined event names; `ScaleUnit` controls perf's display scaling.

## Control Flow, State, and Persistence
`jevents.py` parses each `MetricExpr` through `metric.ParsePerfJson()`, simplifies it, and emits generated `pmu-events.c` metric tables. At runtime `perf list` and metricgroup code expose these names and evaluate the expressions from simultaneously counted events. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include stale event names inside expressions, denominator-zero or multiplexing-sensitive ratios, wrong scale units, metrics that depend on events omitted from this CPU directory, and semantic drift when a raw event definition changes. Test signals include `metric_test.py`, `jevents.py` generation, `perf list --metrics`, and sample `perf stat -M` runs on the matching CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/metrics.json -->
