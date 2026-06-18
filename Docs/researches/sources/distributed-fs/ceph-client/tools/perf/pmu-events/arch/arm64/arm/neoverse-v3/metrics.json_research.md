<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/metrics.json

## Purpose
Provides 63 derived perf metrics for the Arm Neoverse V3 core model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as backend_busy_bound, backend_cache_l1d_bound, backend_cache_l2d_bound, backend_core_bound, backend_core_rename_bound, backend_mem_bound, backend_mem_cache_bound, backend_mem_store_bound, backend_mem_tlb_bound, backend_stalled_cycles, and 53 more and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `ArchStdEvent` references, `MetricName`/`MetricExpr` formulas. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `backend_busy_bound`, `backend_cache_l1d_bound`, `backend_cache_l2d_bound`, `backend_core_bound`, `backend_core_rename_bound`. Metric groups are Branch_Effectiveness, Cycle_Accounting, FP_Arithmetic_Intensity, FP_Precision_Mix, General, LL_Cache_Effectiveness, MPKI;Branch_Effectiveness, MPKI;DTLB_Effectiveness, MPKI;ITLB_Effectiveness, MPKI;ITLB_Effectiveness;DTLB_Effectiveness, and 16 more.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The Neoverse V3 formulas combine stall, branch, cache, TLB, FP, SVE, and topdown events into percentages, MPKI values, and ratios; several topdown category rows are also referenced through `ArchStdEvent`.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/metrics.json -->
