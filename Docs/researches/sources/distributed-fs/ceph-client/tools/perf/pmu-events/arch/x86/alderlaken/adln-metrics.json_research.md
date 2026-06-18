<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/adln-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/adln-metrics.json

## Purpose
Defines derived Intel Alder Lake-N metrics for perf, including package/core C-state residency, SMI accounting, topdown TMA levels, frontend/backend bottlenecks, memory execution ratios, load/store miss accounting, and floating-point operation mix.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 94 records: 0 raw event aliases and 94 derived metrics. Schema fields present are `BriefDescription`, `DefaultMetricgroupName`, `MetricExpr`, `MetricGroup`, `MetricName`, `MetricThreshold`, `MetricgroupNoGroup`, `PublicDescription`, `ScaleUnit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `C10_Pkg_Residency`, `C1_Core_Residency`, `C2_Pkg_Residency`, `C3_Pkg_Residency`, `C6_Core_Residency`, `C6_Pkg_Residency`, `C7_Core_Residency`, `C8_Pkg_Residency`, `smi_cycles`, `smi_num`, plus 84 more.

## Control Flow
Build control flow is data-driven: `process_one_file()` assigns a model table for the leaf x86 directory, `read_json_events()` creates one `PmuEvent` per JSON object, and metric expressions are parsed by `metric.ParsePerfJson(...).Simplify()`. The 94 metrics reference tokens such as `BACLEARS.ANY`, `BR_INST_RETIRED.ALL_BRANCHES`, `BR_INST_RETIRED.CALL`, `BR_INST_RETIRED.FAR_BRANCH`, `BR_MISP_RETIRED.ALL_BRANCHES`, `BR_MISP_RETIRED.COND`, `BR_MISP_RETIRED.COND_TAKEN`, `BR_MISP_RETIRED.INDIRECT`, `BR_MISP_RETIRED.RETURN`, `CPU_CLK_UNHALTED.CORE`, `CPU_CLK_UNHALTED.CORE_P`, `CPU_CLK_UNHALTED.REF_TSC`, plus 79 more; at runtime `perf stat -M` resolves those names against generated PMU tables and evaluates the formulas over counter groups selected for the matching CPUID.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model. Metric integration also depends on expression-token resolution, `MetricConstraint` grouping policy, `ScaleUnit`, `MetricThreshold`, and metric groups `Default;TopdownL1;tma_L1_group`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `TopdownL2;tma_L2_group;tma_backend_bound_group`, `TopdownL2;tma_L2_group;tma_bad_speculation_group`, plus 8 more.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. Metric formulas can fail or mislead if referenced aliases are unavailable, event grouping cannot be scheduled, `#slots` or topdown constants are wrong for the CPU, or denominators are zero on short samples. The `MetricThreshold` strings are carried as text rather than parsed like `MetricExpr`, so threshold syntax changes need explicit perf UI validation.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `C10_Pkg_Residency`, `C1_Core_Residency`, `C2_Pkg_Residency`, `C3_Pkg_Residency`, `C6_Core_Residency`, `C6_Pkg_Residency`, plus 88 more. On matching hardware, run `perf stat -M` for metrics such as `C10_Pkg_Residency`, `C1_Core_Residency`, `C2_Pkg_Residency`, `C3_Pkg_Residency`, `C6_Core_Residency`, plus 89 more and verify expression parsing, grouping, scaling, and thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/adln-metrics.json -->
