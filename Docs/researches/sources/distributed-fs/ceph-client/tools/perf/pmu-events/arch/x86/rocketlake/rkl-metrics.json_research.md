# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/rkl-metrics.json

## Purpose
This JSON file defines the Rocket Lake metric catalog for Linux perf. Unlike the event-topic JSON files, it does not program hardware counters directly. It defines named formulas, groups, thresholds, units, and constraints that perf's metric resolver evaluates from PMU event counts, MSR pseudo-events, topdown pseudo-events, constants, runtime helpers, and other metrics.

The file is the high-level analysis layer for Rocket Lake. It covers package/core C-state residency, SMI accounting, TSX transaction metrics, uncore frequency, memory bandwidth and latency estimates, instruction mix, branch behavior, frontend and backend bottlenecks, port utilization, floating-point/vector usage, TLB behavior, and multi-level Topdown Microarchitecture Analysis groups from L1 through L6.

## Data shape and important fields
The file is a JSON array of 243 metric objects. The observed keys are `MetricName`, `MetricGroup`, `MetricExpr`, `BriefDescription`, `PublicDescription`, `MetricThreshold`, `MetricConstraint`, `ScaleUnit`, `MetricgroupNoGroup`, and `DefaultMetricgroupName`.

Important characteristics:

- 219 metrics have no explicit `MetricConstraint`; 24 use `NO_GROUP_EVENTS`, preventing perf from forcing all referenced events into a single group.
- 151 metrics include `MetricThreshold`, which perf and consumers can use to highlight significant bottlenecks.
- 115 metrics use scale unit `100%`; C-state and TMA metrics commonly express fractions as percentages. Other units include SMI counts and cycles per transaction/elision.
- 12 metrics set `MetricgroupNoGroup`, and 4 set `DefaultMetricgroupName`.
- Metric groups are semicolon-separated classification tags, including `TopdownL1` through `TopdownL6`, `TmaL1`/`TmaL2`/`TmaL3mem`, `Backend`, `Frontend`, `MemoryBW`, `MemoryLat`, `Power`, `HPC`, `SMT`, `SoC`, `OS`, `transaction`, and issue-specific tags such as `tma_issueBW`, `tma_issueTLB`, and `tma_issueBM`.

Representative formulas show the range of expression dependencies:

- C-state residency divides `cstate_pkg@...@` or `cstate_core@...@` counters by `msr@tsc@`.
- Topdown L1 metrics use `topdown\-fe\-bound`, `topdown\-bad\-spec`, `topdown\-retiring`, and `topdown\-be\-bound`.
- Pipeline formulas combine event aliases such as `UOPS_RETIRED.SLOTS`, `TOPDOWN.SLOTS`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CYCLE_ACTIVITY.STALLS_MEM_ANY`, and `EXE_ACTIVITY.BOUND_ON_STORES`.
- Memory formulas depend on `MEM_LOAD_RETIRED.*`, `L2_RQSTS.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, `DTLB_*`, `ITLB_*`, and uncore aliases such as `UNC_ARB_*`.
- Power formulas reference `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE` from `other.json`.
- Streaming-store analysis references `OCR.STREAMING_WR.ANY_RESPONSE` from `other.json`.

## Control flow and integration
The effective control flow is the perf metric-generation and metric-evaluation pipeline:

1. `jevents.py` parses metric objects into generated `struct pmu_metric` rows.
2. `MetricExpr` strings are parsed by the perf metric expression parser. The test file `pmu-events/metric_test.py` demonstrates supported arithmetic, comparisons, `min`/`max`, conditional `if ... else`, escaped event names, and event modifier syntax such as `cpu@event\,umask@`.
3. Generated metric tables are exposed through `pmu_metrics_table__for_each_metric()` and `pmu_metrics_table__find_metric()`.
4. Runtime perf resolves metric names, expands formulas into required events and nested metrics, applies constraints, schedules event groups, collects counts, and evaluates expressions.

This file has extensive dependency control flow through nested metric references. Many formulas are defined in terms of other `tma_*` metrics, so perf must resolve a dependency graph rather than a flat list of independent formulas.

## State, persistence, and dependencies
The file is static source data with no local persistence. Its build artifact is generated C metric-table data. Runtime state is external: perf creates event groups, reads PMU/MSR/sysfs counters, computes durations, detects features such as `#SMT_on`, `#num_dies`, or availability via `has_event(...)`, and evaluates expressions.

Dependencies are broad. The file references Rocket Lake event aliases from `pipeline.json`, `virtual-memory.json`, `other.json`, `uncore-interconnect.json`, and `uncore-other.json`, plus sibling event files outside this work item such as cache, memory, frontend, floating-point, offcore, and topdown-related categories. It also depends on perf's expression language, helper variables (`duration_time`, `#SMT_on`, `#num_dies`), pseudo-events (`cycles`, `cycles\-t`, `topdown\-*`), MSR events, cstate PMUs, and event availability guards.

## Risks
The main risk is unresolved or incorrectly grouped metric dependencies. The JSON itself can parse while a formula references a renamed event, a missing sibling event, or a helper unavailable on a particular system. Metrics with `NO_GROUP_EVENTS` constraints can also produce different scheduling behavior from grouped metrics, so constraint changes affect measurement validity.

Formula fragility is high because many expressions divide by other counters or nested metrics. Some formulas use `max(...)`, `min(...)`, and `if has_event(...) else ...` guards, but not every denominator is explicitly protected. Low-count workloads, unsupported events, disabled PMUs, or multiplexing can yield misleading percentages.

Another risk is cross-layer semantic drift. TMA metrics assume particular Rocket Lake slot, pipeline, memory, and uncore semantics. A local edit to one event file can silently change a metric's meaning. Conversely, adding a metric here without adding required event aliases in sibling JSON files breaks perf metric resolution.

## Test signals
Required baseline checks are `jq empty rkl-metrics.json`, a full `jevents.py` generation run, and perf metric parser tests. Stronger checks include running `metric_test.py`, verifying `perf list --json` includes representative `MetricName` rows and their groups, and running `perf stat -M` smoke tests for `tma_backend_bound`, `tma_frontend_bound`, `tma_memory_bound`, `tma_dtlb_load`, `tma_info_system_power`, `C6_Core_Residency`, and TSX metrics on hardware or a test harness with expected event availability.

Cross-file validation should extract all uppercase event references from `MetricExpr` and confirm they resolve somewhere in the Rocket Lake event set or in perf pseudo-event support. It should also check that thresholds and `ScaleUnit` values are preserved in generated `pmu_metric` rows.
