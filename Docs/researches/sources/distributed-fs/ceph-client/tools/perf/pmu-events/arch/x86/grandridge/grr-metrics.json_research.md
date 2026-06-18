## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/grr-metrics.json

**Purpose:** Grand Ridge metric table with 124 `pmu_metric` records. It defines user-facing formulas for topdown microarchitecture analysis, power/C-state residency, CPI/IPC/frequency/utilization, memory and IO bandwidth, SMI, load/store miss ratios, FLOPs, and detailed bottleneck breakdowns.

**Schema and important records:** Records use metric fields `MetricName`, `MetricExpr`, optional `MetricGroup`, `MetricThreshold`, `ScaleUnit`, `BriefDescription`, `PublicDescription`, and `MetricgroupNoGroup`. Groups include `TopdownL1`, `TopdownL2`, `TopdownL3`, `Flops`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `load_store_bound`, and `smi`. Expressions reference core events (`CPU_CLK_UNHALTED.*`, `INST_RETIRED.ANY`, `TOPDOWN_*`, `MEM_*`, `BR_*`, `FP_*`), MSR pseudo-events (`msr@tsc@`, `msr@smi@`, `msr@aperf@`), cstate pseudo-events, and uncore events (`UNC_CHA_*`, `UNC_M_*`, `UNC_IIO_*`).

**Control flow and integration:** `jevents.py` emits these as `struct pmu_metric` rows, while `metric.py` and perf's metric parser validate and expand expressions. Runtime `perf stat -M <metric>` schedules the referenced event set, applies thresholds, scales units, and groups metrics according to `MetricGroup`.

**State and persistence:** Metric formulas and thresholds are static compiled metadata. Runtime values are derived from current counter readings, duration, source counts, and system constants such as `#SYSTEM_TSC_FREQ`.

**Dependencies:** Strongly depends on all Grand Ridge event-topic files plus uncore PMU event definitions outside this subset. `metricgroups.json` supplies descriptions for the group names used here.

**Risks:** This file is name-fragile: any event rename or missing uncore event breaks expression parsing or runtime collection. Division by zero, multiplexing, and threshold grouping can produce misleading output. Typographical metric names such as `adressaliasing` may be externally visible and should not be changed casually.

**Test signals:** Run perf metric parser tests and `tools/perf/pmu-events/metric_test.py` if available. `perf list metricgroups`, `perf list metrics`, and sample `perf stat -M TopdownL1,cpi,memory_bandwidth_total` on Grand Ridge are high-value integration checks.
