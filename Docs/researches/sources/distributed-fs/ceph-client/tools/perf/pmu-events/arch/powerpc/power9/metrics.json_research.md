# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/metrics.json

## Purpose

This file defines 318 POWER9 derived metrics. The metrics cover branch prediction, CPI breakdown, data-cache reload percentages by source, estimated data-cache miss CPI, general IPC/CPI and miss rates, instruction-source percentages, L2 stats, latency estimates, LSU rejects, memory locality, prefetch, PTEG reloads, and translation ratios. Metric groups include `branch_prediction`, `cpi_breakdown`, `general`, `memory`, `latency`, `translation`, and other focused groups.

## APIs, types, and schema

Each object uses the metric schema consumed by `JsonEvent`: `MetricName`, `MetricGroup`, `MetricExpr`, and usually `BriefDescription`. `jevents.py` parses `MetricExpr` with `metric.ParsePerfJson(...).Simplify()`, stores the result as a generated metric expression, and may rewrite metrics in terms of other metrics with `metric.RewriteMetricsInTermsOfOthers`. Unlike event files, there is no `EventCode`; the public API is the metric name and expression available to perf metric groups.

## Control flow and integration

The file is loaded with all other POWER9 JSON files. Metrics are collected into pending metric tables, deduplicated by metric name and PMU, sorted, and emitted into generated `pmu-events.c`. At runtime, perf metric commands resolve raw PMU events and derived metric names from these expressions. Cross-file integration is heavy: this file references 219 distinct `PM_*` raw events, and all direct `PM_*` references observed in the expressions are present in the POWER9 JSON directory.

## State, persistence, and dependencies

The file is static formula metadata persisted in source and generated C. It depends on raw event names from the POWER9 event JSON files, the perf metric expression parser, expression rewrite rules, and correct denominator semantics. Several formulas depend on other derived metrics, so the metric graph must remain acyclic and parseable.

## Risks and test signals

The major risks are formula drift, divide-by-zero behavior in low-count workloads, derived-metric dependency mistakes, and raw event renames. CPI breakdown formulas are particularly sensitive because some entries subtract other derived metrics and can produce misleading negative values if component events are unavailable or not mutually exclusive. Test signals include `jq empty`, `pmu-events/metric_test.py`, full `jevents.py` generation, checking unresolved `PM_*` references, and representative `perf stat -M` runs for branch, CPI, memory, latency, and translation groups.
