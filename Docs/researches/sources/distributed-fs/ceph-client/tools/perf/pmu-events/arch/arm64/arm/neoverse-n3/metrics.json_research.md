<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/metrics.json

Purpose: Defines derived perf metrics rather than raw programmable events. The entries combine architected PMU event names into ratios, MPKI values, operation-mix percentages, and cycle/topdown-style accounting formulas for this CPU.

Important data contract: JSON array with 67 entries for the `neoverse-n3` `metrics` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 63 entries carry local descriptions and 65 entries carry `MetricExpr` formulas. Representative names: `backend_bound`, `backend_busy_bound`, `backend_cache_l1d_bound`, `backend_cache_l2d_bound`, `backend_core_bound`, `backend_core_rename_bound`, `backend_mem_bound`, `backend_mem_cache_bound`, plus 59 more.

Control flow: Perf's pmu-events generator preserves each `MetricName`, parses `MetricExpr`, and resolves referenced event tokens against sibling event JSON tables for the same CPU map. Runtime selection evaluates the expression over counters collected in the same stat session. Metric groups represented include Branch_Effectiveness, Cycle_Accounting, FP_Arithmetic_Intensity, FP_Precision_Mix, General, LL_Cache_Effectiveness, plus 20 more.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, BriefDescription, MetricExpr, MetricGroup, MetricName, ScaleUnit`. Metric expressions reference sibling raw events such as ASE_SPEC, BR_IMMED_RETIRED, BR_IND_RETIRED, BR_MIS_PRED_RETIRED, BR_RETIRED, BR_RETURN_RETIRED, CPU_CYCLES, CRYPTO_SPEC, DMB_SPEC, DP_SPEC, plus 55 more tokens.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Metric expressions can silently become misleading if referenced raw events are renamed, unavailable for a CPU revision, or have divide-by-zero behavior on short runs. Expressions using `#slots` or `strcmp_cpuid_str` are tightly coupled to perf's metric parser and CPU identification helpers.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `backend_bound`, `backend_busy_bound`, `backend_cache_l1d_bound`, `backend_cache_l2d_bound`, `backend_core_bound`, and 62 more. Run `perf stat -M` for representative metrics and check expression parsing, event grouping, and zero-denominator handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/metrics.json -->
