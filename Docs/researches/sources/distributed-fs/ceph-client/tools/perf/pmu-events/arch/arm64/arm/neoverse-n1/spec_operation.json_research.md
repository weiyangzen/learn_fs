<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spec_operation.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 25 entries for the `neoverse-n1` `spec operation` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 25 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `LDREX_SPEC`, `STREX_PASS_SPEC`, plus 17 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, and 20 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spec_operation.json -->
