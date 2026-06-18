<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/emr-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/emr-metrics.json

## Purpose
Defines the Emerald Rapids derived metric catalog for Linux perf's x86 PMU events system. The file is a JSON array of 307 metric objects that convert raw core, offcore, uncore, MSR, cstate, and topdown events into higher-level user-facing metrics for `perf list`, `perf stat -M`, and related perf tooling. It is data, not executable code, but it is a contract consumed by perf's pmu-events generator and metric expression evaluator.

## Important APIs, Types, And Functions
- Top-level type: JSON array of metric records.
- Required record fields seen throughout the file: `MetricName`, `MetricExpr`, and `BriefDescription`.
- Classification and display fields: `MetricGroup`, `DefaultMetricgroupName`, `MetricgroupNoGroup`, `ScaleUnit`, `PublicDescription`, and `MetricThreshold`.
- Scheduling/constraint field: `MetricConstraint`, used by perf metric scheduling when an expression has grouping or counter constraints.
- Expression language dependencies: raw PMU event names such as `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, offcore/uncore names such as `UNC_M_CAS_COUNT.RD`, synthetic topdown slots such as `topdown-fe-bound`, helper variables such as `duration_time`, `source_count(...)`, `#num_packages`, `#num_dies`, and `#SYSTEM_TSC_FREQ`.
- Metric families include power and cstate residency, CPI/IPC/utilization, TLB and cache miss ratios, memory and IO bandwidth, NUMA locality, frontend delivery, topdown hierarchy levels, floating-point vector/scalar mix, branch and bad speculation diagnostics, memory latency/bandwidth bottlenecks, and system uncore signals.

## Control Flow
At build or install time, perf's pmu-events tooling reads this JSON with the other Emerald Rapids event files and emits architecture-specific metric tables. At runtime, perf matches the Emerald Rapids model, exposes these `MetricName` values, parses each `MetricExpr`, schedules the referenced hardware/software events, reads counters for the workload interval, and evaluates the expression into the declared `ScaleUnit`. Metrics reference each other heavily: first-level topdown metrics derive from topdown slots, lower-level TMA metrics derive from those parent metrics plus event counts, and informational metrics expose derived rates or ratios used by other metrics.

## State And Persistence
The file itself is static source-controlled metadata. Runtime state is limited to perf's selected metric list, scheduled counter groups, raw counter values, and derived printed results. It does not persist data or modify kernel state beyond normal perf event programming. Several metrics depend on system topology and run duration variables, so the same record can evaluate differently by socket count, die count, uncore availability, multiplexing, and workload duration.

## Dependencies And Integration Points
- Integrated with `tools/perf/pmu-events` JSON loading and generated event-table code in the Ceph-client copy of Linux perf.
- Depends on matching raw event definitions from sibling files in the Emerald Rapids directory and generic x86 event files.
- Depends on Intel Emerald Rapids PMU semantics, including topdown slot events, offcore response events, uncore CHA/IMC/PCU events, cstate PMUs, and model-specific counter availability.
- Integrates with perf metric grouping, threshold display, and metric group browsing through group names such as `Default`, `TopdownL1`, `TopdownL2`, `TopdownL3`, `TopdownL4`, `Mem`, `MemoryBW`, `MemoryLat`, `Flops`, `Frontend`, `Backend`, `Power`, `SoC`, and TMA internal groups.
- The metrics file is also coupled to documentation and user workflows because `MetricName` strings are command-line API surface for `perf stat -M <metric>`.

## Risks And Edge Cases
- Expression drift is the main risk: a metric can parse successfully but produce wrong results if an event name, topdown term, topology variable, or scale factor no longer matches perf's evaluator or the kernel PMU driver.
- Counter scheduling can fail or multiplex if metric expressions require too many constrained events, especially for uncore metrics spanning CHA, IMC, PCU, and offcore resources.
- Null or absent group fields are valid in this file; consumers must not assume every metric has a non-empty `MetricGroup` or `ScaleUnit`.
- Some metrics are ratios over `INST_RETIRED.ANY`, `duration_time`, or uncore clocks; very short runs, idle systems, zero denominators, or disabled uncore PMUs can lead to missing, zero, NaN, or misleading output.
- Metrics with thresholds are advisory. A stale threshold can cause false bottleneck highlighting even if the raw expression remains valid.
- This file is architecture-specific. Reusing it for a nearby x86 model without checking event encodings and uncore topology would risk silent mismeasurement.

## Test Signals
- `jq empty` or an equivalent JSON parser should accept the file.
- The pmu-events build should regenerate successfully and report no unknown fields or malformed expressions.
- `perf list metric` on Emerald Rapids should include representative entries such as `tma_frontend_bound`, `tma_backend_bound`, `tma_memory_bound`, `memory_bandwidth_total`, and `llc_demand_data_read_miss_latency`.
- `perf stat -M` smoke tests for topdown, memory bandwidth, cstate, and FP metrics should schedule without parser errors on supported hardware.
- Regression checks should look for stable metric counts, valid units, no duplicate `MetricName` values, and no unresolved event references after changes to sibling JSON event files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/emr-metrics.json -->
