# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/ivt-metrics.json

Purpose: Defines 137 derived Ivy Town perf metrics, including package/core C-state residency, SMI indicators, topdown microarchitecture levels, memory/cache diagnostics, frontend/backend breakdowns, FP/HPC summaries, power/system metrics, and helper `tma_info_*` values. This file is the main formula layer above raw PMU events.

Important APIs/types/functions: Entries use `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, `BriefDescription`, `PublicDescription`, `MetricThreshold`, `MetricConstraint`, and `MetricgroupNoGroup`. Expressions reference raw event aliases, other metrics, perf special terms (`duration_time`, `cycles`, `#SMT_on`, `#core_wide`, `#num_cpus_online`, `#num_dies`), MSR and sysfs-style events (`msr@tsc@`, `power@energy-pkg@`, `cstate_*`), and encoded event forms such as `cpu@...\\,cmask\\=1@`.

Control flow: Perf loads these metric definitions for Ivy Town, resolves dependencies recursively, schedules the raw events needed by each formula, evaluates `MetricExpr`, applies `ScaleUnit`, groups metrics through `MetricGroup`, and uses thresholds for UI/reporting hints. Level-1 topdown metrics derive from `tma_frontend_bound`, `tma_bad_speculation`, `tma_retiring`, and `tma_backend_bound`; deeper metrics refine those categories into branch, frontend, memory, core, port, FP, and system explanations.

State and persistence: Static formula metadata only. There is no mutable state in the file. Runtime state is the measured event values and evaluated metric results held by perf.

Dependencies/integration: Depends on raw aliases from Ivy Town cache, frontend, floating-point, memory, pipeline, virtual-memory, and uncore files. High-frequency dependencies include `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, `MEM_LOAD_UOPS_RETIRED.*`, LLC hit/miss retired events, `UOPS_RETIRED.RETIRE_SLOTS`, and `UOPS_EXECUTED.THREAD`. It also depends on `metricgroups.json` for readable group labels.

Risks: Formula breakage is easy when event aliases are renamed, removed, or moved between files. Expressions include divisions with workload-dependent zero denominators; perf's expression evaluator must handle these robustly. Some formulas embed architecture-specific latency constants, SMT adjustments, and heuristic thresholds, so values are diagnostic estimates rather than hardware invariants. Long offcore/memory expressions create large event groups that may multiplex or fail on counter constraints.

Test signals: Run perf metric parser tests, dependency-resolution checks for every `MetricExpr`, and group-label checks against `metricgroups.json`. On Ivy Town hardware, smoke-test topdown, memory, power, and FP metric groups under idle, CPU-bound, memory-bound, branch-mispredict, and FP workloads. Static tests should flag unknown aliases, cyclic metric dependencies, and invalid expression syntax.
