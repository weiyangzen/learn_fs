## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/snb-metrics.json

### Purpose
`snb-metrics.json` defines 69 Sandy Bridge derived metrics. It provides top-down microarchitecture analysis metrics, system summary metrics, power/C-state residency, SMT/core frequency helpers, floating-point throughput, memory bandwidth, SMI accounting, OS/kernel utilization, and metric thresholds.

### Important APIs, Types, And Data Fields
The file is a JSON array of metric objects:

- `MetricName` is the perf metric identifier, for example `tma_frontend_bound`, `tma_bad_speculation`, `tma_backend_bound`, `tma_retiring`, `tma_memory_bound`, `tma_fp_vector`, `tma_info_thread_ipc`, `tma_info_system_dram_bw_use`, `smi_cycles`, and C-state residency metrics.
- `MetricExpr` is the expression language consumed by perf. It references event names, other metrics, constants, runtime variables such as `#SMT_on`, `#core_wide`, `#num_cpus_online`, `#num_dies`, and special events like `duration_time`, `msr@tsc@`, `msr@aperf@`, and `cstate_*`.
- `MetricGroup` is a semicolon-separated taxonomy consumed with `metricgroups.json`.
- `MetricThreshold` encodes alert/display thresholds for many top-down metrics.
- `ScaleUnit` formats output, often `100%`, `1SMI#`, or blank for ratios.
- `MetricConstraint` and `MetricgroupNoGroup` constrain grouping for events that cannot be scheduled together or should not be auto-grouped in some modes.
- `BriefDescription` and `PublicDescription` provide user-facing metric explanations.

No local functions/classes exist, but metric expressions are executable by perf's metric evaluator.

### Control Flow And Data Flow
Perf loads event definitions from sibling files, then evaluates `MetricExpr` formulas by collecting referenced events and recursively resolving metric references. Top-down level 1 is built from `tma_frontend_bound`, `tma_bad_speculation`, `tma_retiring`, and derived `tma_backend_bound`. Lower-level metrics derive branch mispredicts, machine clears, fetch latency/bandwidth, core/memory bound, DRAM bound, L3 bound, store bound, port utilization, FP arithmetic mix, and microcode sequencing. System metrics use uncore events from `uncore-interconnect.json`, C-state pseudo-events, MSR pseudo-events, and duration/time pseudo-events.

### State And Persistence
The file persists formulas, thresholds, group membership, and display units. It stores no runtime measurements. Perf may compile or cache these expressions in generated event tables.

### Dependencies And Integration Points
This file depends on exact event names from `pipeline.json`, `frontend.json`, `cache.json`, `memory.json`, `floating-point.json`, `virtual-memory.json`, and `uncore-interconnect.json`. It depends on group keys in `metricgroups.json` and perf's expression evaluator features: conditional expressions, `min`, escaped raw event syntax such as `cpu@UOPS_DISPATCHED.CORE\\,cmask\\=1@`, MSR pseudo-events, C-state pseudo-events, and runtime topology variables.

### Risks
Metrics can fail or mislead if any referenced event is renamed, removed, or semantically changed. Expressions include scheduling-sensitive constraints and SMT/core-wide conditionals; mistakes can produce plausible but wrong top-down percentages. Escaping in raw event syntax is fragile because commas and backslashes must survive JSON parsing and perf expression parsing. Group and threshold metadata also affect how users discover and interpret bottlenecks.

### Test Signals
Run JSON validation, perf metric expression parser tests, reference checks ensuring every event and metric name resolves, group-key checks against `metricgroups.json`, and `perf stat -M` smoke tests for top-down groups on compatible systems. Important formulas to validate include `tma_info_thread_slots`, `tma_frontend_bound`, `tma_bad_speculation`, `tma_memory_bound`, `tma_dram_bound`, `tma_info_system_dram_bw_use`, and FP FLOP metrics.
