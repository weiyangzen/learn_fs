# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/hsw-metrics.json

## Purpose

This file defines 122 Haswell metric records for Linux perf. It is the Haswell top-down and system-metric catalog: package/core C-state residency, uncore frequency, SMI accounting, top-down microarchitecture levels, memory bandwidth and latency formulas, branch and instruction-mix ratios, SMT/core utilization helpers, pipeline throughput helpers, port-utilization breakdowns, and derived memory/cache/TLB indicators.

The x86 mapfile selects the `haswell` directory for `GenuineIntel-6-(3C|45|46)` models. Once compiled into perf, these metrics let users run `perf stat -M` or list metric groups without knowing the underlying raw events.

## Important APIs, Types, And Data

The file is declarative data. Its effective API is the perf metric JSON schema handled by `tools/perf/pmu-events/jevents.py`: `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, and optional `ScaleUnit`. `MetricExpr` is parsed through perf's metric expression parser, simplified, then emitted into generated metric tables.

Important metric families include `tma_frontend_bound`, `tma_bad_speculation`, `tma_backend_bound`, `tma_retiring`, `tma_memory_bound`, `tma_core_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dram_bound`, `tma_ports_utilization`, `tma_ports_utilized_*`, `tma_port_0` through `tma_port_7`, `tma_info_memory_*`, `tma_info_system_*`, `tma_info_thread_*`, `C*_Residency`, `UNCORE_FREQ`, `smi_cycles`, and `smi_num`.

The expressions depend on aliases defined in sibling Haswell event files, including `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `UOPS_*`, `IDQ_*`, `BR_*`, `MACHINE_CLEARS.*`, `CYCLE_ACTIVITY.*`, `MEM_LOAD_UOPS_*`, `MEM_UOPS_RETIRED.*`, `OFFCORE_*`, `DTLB_*`, `ITLB_*`, and uncore `UNC_*` aliases. They also use perf expression variables such as `#SMT_on`, `#core_wide`, `#num_cpus_online`, `#num_dies`, and built-in events like `duration_time`, `msr@tsc@`, `msr@aperf@`, `msr@smi@`, and power/cstate PMUs.

## Control Flow

At build time, `jevents.py` scans the Haswell directory, skips only `metricgroups.json` for event loading, and creates `JsonEvent` objects for metric entries. `MetricExpr` is parsed by `metric.ParsePerfJson(...).Simplify()`, metric-group strings are preserved, descriptions are compacted into the generated string table, and metric records are emitted into generated `pmu-events.c`.

At runtime, perf metric expansion resolves metric names into event aliases, raw event specs, special PMUs, constants, and conditional expression branches. Metrics do not program counters directly; they expand into the event set needed by `perf stat`, then calculate ratios or percentages from measured counter values.

## State And Persistence Behavior

The JSON stores persistent metric formulas and display metadata only. It does not persist counter samples, derived values, or runtime state. Runtime state lives in perf evsels, kernel PMU file descriptors, and the measured workload. Formula conditionals such as `if #SMT_on else` adapt to detected topology at evaluation time.

## Dependencies And Integration Points

This file integrates with `arch/x86/mapfile.csv`, Haswell core and uncore event JSON files, `tools/perf/pmu-events/jevents.py`, `metric.py`, generated `pmu-events.c`, perf metric lookup and expression evaluation code, `perf list`, and `perf stat -M`. It depends on sibling event aliases staying stable because formulas reference event names textually. It also depends on kernel exposure of MSR, power, cstate, and uncore PMUs for system-level metrics.

## Risks And Edge Cases

Textual event references are the main risk: renaming or deleting an event alias in another JSON file can break metric expansion even when this file remains valid JSON. Several formulas divide by event counts such as branch counts, store counts, walk counts, or elapsed time; zero or multiplexed counts can produce undefined, capped, or misleading results. SMT-aware conditionals and hard-coded constants such as slot width, assist costs, and latency weights are Haswell-specific and should not be reused for HaswellX or later models without validation. Metrics that mix core, package, MSR, power, and uncore events can fail partially on kernels or systems that do not expose every required PMU.

## Test Signals

Useful checks include `jq empty`, running `jevents.py` generation for x86, building `tools/perf`, `perf test pmu-events`, `perf test expr`, and `perf list --details` for Haswell metric names. Runtime validation should include `perf stat -M tma_frontend_bound,tma_backend_bound,tma_retiring,tma_bad_speculation`, a memory-stress run for `tma_info_memory_*`, and a system-level run for `Power`, `SoC`, and `smi` groups on hardware or fixtures with the required MSR and uncore PMUs.
