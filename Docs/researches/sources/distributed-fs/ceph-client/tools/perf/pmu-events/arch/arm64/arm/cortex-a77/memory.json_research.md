<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 7 entries for the `cortex-a77` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a77` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/memory.json -->
