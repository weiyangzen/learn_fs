# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/bdx-metrics.json

## Purpose

`bdx-metrics.json` defines 186 BroadwellX core and system metrics for perf. It is the architectural metric layer above the raw event files in the same directory: formulas combine core events, uncore events, MSR pseudo-events, duration/time aliases, and perf expression conditionals to expose Top-down Microarchitecture Analysis categories, cache/memory ratios, power residency, bandwidth, IPC/CPI, SMT, kernel utilization, and instruction-mix diagnostics.

## Important APIs, types, and schema

Each array element is a metric dictionary consumed by `jevents.py` as a `JsonEvent` with `MetricName` set rather than `EventName`. Important fields are `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, `PublicDescription`, `ScaleUnit`, `MetricThreshold`, `MetricConstraint`, and `MetricgroupNoGroup`. `jevents.py` maps these into `struct pmu_metric` fields: `metric_name`, `metric_expr`, `metric_group`, `metric_threshold`, `unit`, `desc`, `long_desc`, `metricgroup_no_group`, and `event_grouping`.

The metric expressions are parsed by `metric.ParsePerfJson(...).Simplify()` and may be rewritten by `metric.RewriteMetricsInTermsOfOthers()`. Expressions use perf JSON syntax such as `cpu@EVENT\\,cmask\\=1@`, `msr@tsc@`, arithmetic, `min`/`max`, and conditional expressions keyed by runtime variables like `#SMT_on`, `#core_wide`, and `#num_cpus_online`. Metric constraints such as `NO_GROUP_EVENTS` and `NO_GROUP_EVENTS_SMT` are converted to the `enum metric_event_groups` values in `pmu-events.h`; thresholds are stored as strings because `jevents.py` explicitly avoids parsing them.

## Control flow and integration

During the perf build, `Build` includes all x86 JSON files in `SRC_JSON`, optionally copies them to `$(OUTPUT)pmu-events/arch`, and runs `jevents.py`. `preprocess_one_file()` reads this file, adds compact metric strings to the global string table, and `process_one_file()` later appends unique metrics to the BroadwellX metric table. At runtime, `find_core_metrics_table("x86", cpuid)` resolves the BroadwellX table through `arch/x86/mapfile.csv`; `perf list` can print these metrics and `perf stat -M ...` can expand their event dependencies.

This file is tightly coupled to the adjacent raw event files. For example, Top-down and memory metrics reference cache events such as `MEM_LOAD_UOPS_RETIRED.*`, frontend events such as `IDQ_UOPS_NOT_DELIVERED.*`, floating-point events such as `FP_ARITH_INST_RETIRED.*`, memory transaction events such as `MEM_TRANS_RETIRED.*`, and offcore response events encoded in `cache.json` and `memory.json`. It also references other BroadwellX JSON files outside this work item, including pipeline, virtual-memory, uncore-memory, uncore-cache, uncore-interconnect, uncore-io, and power events.

## State and persistence behavior

There is no mutable runtime state in the JSON. Its persistent effect is the generated `pmu-events.c` metric table embedded into the perf binary. Runtime state is limited to perf's event scheduling and metric evaluation: constraints can change how event groups are scheduled, thresholds affect reporting, and formulas using `#SMT_on`, `duration_time`, or uncore counters vary by machine and workload.

## Dependencies

The file depends on the perf PMU JSON schema, `jevents.py`, `metric.py`, `pmu-events.h`, the x86 mapfile entry for BroadwellX, and the raw event names it references. It also depends on kernel/perf support for pseudo-events like `msr@tsc@`, `power@energy-pkg@`, `duration_time`, and named PMU instances such as `cbox_0`.

## Risks

The largest risk is stale or missing event references: because formulas span many files, a renamed event in cache, memory, frontend, floating-point, pipeline, virtual-memory, or uncore JSON will break metric expansion. Several metrics use `MetricConstraint` or `MetricgroupNoGroup` to avoid unsafe grouping; dropping those fields can lead to invalid multiplexing or misleading values under SMT/NMI constraints. Thresholds are not parsed by `jevents.py`, so syntax errors may survive generation and only surface in perf display behavior. Many formulas include division by event counts; zero-count workloads rely on perf metric handling to avoid noisy or undefined output. Some formulas mix core and uncore/system scope, so aggregation mode and PMU availability can materially affect interpretation.

## Test signals

Useful validation is `jq empty bdx-metrics.json`, a `tools/perf` build that regenerates `pmu-events.c`, `pmu-events/metric_test.py`, and a runtime smoke test on BroadwellX or compatible test fixtures with `perf list --json` and `perf stat -M TopdownL1,tma_backend_bound`. Targeted checks should verify that `MetricConstraint` strings map to `enum metric_event_groups`, that TopdownL1/TopdownL2 formulas expand without missing aliases, and that metric group descriptions from `metricgroups.json` cover the groups emitted here.
