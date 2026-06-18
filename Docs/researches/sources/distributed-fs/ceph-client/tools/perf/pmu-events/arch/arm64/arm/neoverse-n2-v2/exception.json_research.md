<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `neoverse-n2-v2` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 15 entries carry local descriptions. Representative names: `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/exception.json -->
