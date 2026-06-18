<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/stall.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 7 entries for the `neoverse-n2-v2` `stall` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 7 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/stall.json -->
