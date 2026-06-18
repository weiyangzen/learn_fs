<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/sve.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 7 entries for the `neoverse-v1` `sve` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 7 entries carry local descriptions. Representative names: `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, `SVE_LDFF_SPEC`, `SVE_LDFF_FAULT_SPEC`.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/sve.json -->
