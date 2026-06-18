<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/tgl-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/tgl-metrics.json

## Purpose

`tgl-metrics.json` is the Tiger Lake perf metric catalog. It contains 243 metric records that turn raw core, uncore, MSR, cstate, and derived topdown events into user-facing `perf stat -M` metrics. The file covers package/core C-state residency, uncore frequency, SMI accounting, Top-Down Microarchitecture Analysis levels 1 through 6, bottleneck-view rollups, branch and fetch analysis, memory/cache/TLB pressure, port utilization, instruction mix, floating-point mix, system utilization, DRAM bandwidth, power-license utilization, SMT utilization, and TSX transaction behavior.

## Important APIs, Types, and Data Fields

The file is a JSON array of perf metric objects rather than executable code. Records use the metric schema fields `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, and optional `PublicDescription`, `MetricThreshold`, `MetricConstraint`, `DefaultMetricgroupName`, `MetricgroupNoGroup`, and `ScaleUnit`. `MetricExpr` is the primary API surface: expressions reference raw events such as `UOPS_DISPATCHED.PORT_*`, `BR_MISP_RETIRED.ALL_BRANCHES`, `MEM_LOAD_RETIRED.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, pseudo-events such as `msr@tsc@`, `msr@aperf@`, `msr@smi@`, cstate aliases, duration constants, and other metrics such as `tma_backend_bound`.

Important metric families include the top-level categories `tma_backend_bound`, `tma_bad_speculation`, `tma_frontend_bound`, and `tma_retiring`; bottleneck-view formulas such as `tma_bottleneck_data_cache_memory_bandwidth`, `tma_bottleneck_data_cache_memory_latency`, `tma_bottleneck_memory_data_tlbs`, `tma_bottleneck_mispredictions`, and `tma_bottleneck_compute_bound_est`; system/info metrics under `tma_info_*`; memory hierarchy metrics such as `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_dram_bound`, `tma_mem_bandwidth`, and `tma_mem_latency`; and summary/power metrics such as `C*_Pkg_Residency`, `C*_Core_Residency`, `UNCORE_FREQ`, `smi_cycles`, and `smi_num`. There are 24 metrics with `MetricConstraint`, 22 with `MetricThreshold`, 19 with `PublicDescription`, and 7 with `ScaleUnit`.

## Control Flow and Data Flow

There is no local control flow in the JSON. The data flow starts when perf's PMU event build pipeline parses this file and emits generated metric descriptors. At runtime, perf's metric parser expands each `MetricExpr`, schedules the referenced events, applies arithmetic and conditional expressions, normalizes with constants such as `tma_info_thread_slots` or `duration_time`, evaluates thresholds, and groups metrics according to `MetricGroup`.

The formulas form a dependency graph. Base information metrics compute clock, slot, instruction, cache, memory, and system denominators; level-1 and deeper `tma_*` metrics reuse those bases; bottleneck-view metrics combine multiple topdown branches into higher-level cost estimates. This means a user request for one high-level metric can require many raw events and intermediate metrics.

## State and Persistence Behavior

The only persistent state is static metric metadata in the source tree and the generated perf event-table output produced from it. Runtime measurements are interval-local and are not written back to this file. Several metrics depend on package-wide or system-wide state, such as C-state residency, SMI counters, DRAM bandwidth, and uncore frequency, while most TMA metrics depend on per-thread or per-core counting. `MetricThreshold` values persist as advisory expressions that perf can use to flag likely bottlenecks.

## Dependencies and Integration Points

The file depends on Tiger Lake core PMU event definitions, uncore memory/event catalogs, cstate and MSR pseudo-event support, topdown hardware events, and the perf metric expression evaluator. It integrates with `perf list metrics`, `perf list metricgroups`, `perf stat -M`, generated `pmu-events.c`, metric tests, and topdown performance-analysis workflows. It also depends indirectly on sibling Tiger Lake event files for raw event names referenced by formulas, including cache, memory, frontend, pipeline, virtual-memory, uncore-memory, and uncore-interconnect topics.

## Risks and Edge Cases

The main risk is expression fragility. Any rename or removal of a referenced event or intermediate metric can break metric parsing or produce unavailable metrics. Large formulas can divide by zero or by near-zero denominators when a workload does not exercise the relevant hardware path; some expressions use `max(...)` or conditionals, but not every ratio is guarded. Package-wide and system-wide metrics can be misleading when interpreted as task-local. Multiplexing can distort formulas that combine many events if the PMU cannot schedule them together. `MetricConstraint: NO_GROUP_EVENTS` is important because losing it can force invalid grouped scheduling. Thresholds are heuristics, not correctness rules.

## Test Signals

Useful checks include JSON parsing with `jq`, generated perf PMU table builds, `tools/perf/pmu-events/metric_test.py` or equivalent metric-expression tests, and `perf list metrics` on a Tiger Lake-capable build. Runtime smoke tests should include `perf stat -M TopdownL1`, memory bandwidth/latency metrics under a streaming workload, branch-misprediction metrics under a branch-heavy workload, and power/SMI metrics on an idle versus busy system. Regression tests should specifically catch missing raw-event aliases, unguarded expression failures, and accidental group/threshold changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/tgl-metrics.json -->
