<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/branch.json

Purpose: Declares branch prediction and branch-speculation PMU aliases for perf on this Arm core.

Important data contract: JSON array with 2 entries for the `cortex-a76` `branch` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`.

Control flow: The table is consumed as named raw PMU events; branch metrics and `perf stat -e` aliases depend on these names resolving to the CPU's PMU encoding.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a76` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/branch.json -->
