<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/metrics.json

Purpose: Defines derived perf metrics rather than raw programmable events. The entries combine architected PMU event names into ratios, MPKI values, operation-mix percentages, and cycle/topdown-style accounting formulas for this CPU.

Important data contract: JSON array with 46 entries for the `neoverse-n2-v2` `metrics` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 42 entries carry local descriptions and 46 entries carry `MetricExpr` formulas. Representative names: `backend_bound`, `backend_stalled_cycles`, `bad_speculation`, `branch_misprediction_ratio`, `branch_mpki`, `branch_percentage`, `crypto_percentage`, `dtlb_mpki`, plus 38 more.

Control flow: Perf's pmu-events generator preserves each `MetricName`, parses `MetricExpr`, and resolves referenced event tokens against sibling event JSON tables for the same CPU map. Runtime selection evaluates the expression over counters collected in the same stat session. Metric groups represented include Cycle_Accounting, General, LL_Cache_Effectiveness, MPKI;Branch_Effectiveness, MPKI;DTLB_Effectiveness, MPKI;ITLB_Effectiveness, plus 16 more.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, BriefDescription, MetricExpr, MetricGroup, MetricName, ScaleUnit`. Metric expressions reference sibling raw events such as #slots, ASE_SPEC, BR_IMMED_SPEC, BR_INDIRECT_SPEC, BR_MIS_PRED, BR_MIS_PRED_RETIRED, BR_RETIRED, BR_RETURN_SPEC, CPU_CYCLES, CRYPTO_SPEC, plus 32 more tokens.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Metric expressions can silently become misleading if referenced raw events are renamed, unavailable for a CPU revision, or have divide-by-zero behavior on short runs. Expressions using `#slots` or `strcmp_cpuid_str` are tightly coupled to perf's metric parser and CPU identification helpers.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `backend_bound`, `backend_stalled_cycles`, `bad_speculation`, `branch_misprediction_ratio`, `branch_mpki`, and 41 more. Run `perf stat -M` for representative metrics and check expression parsing, event grouping, and zero-denominator handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/metrics.json -->
