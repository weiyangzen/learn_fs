<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/trace.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/trace.json

Purpose: Declares trace buffer, trace external output, and CTI trigger PMU aliases.

Important data contract: JSON array with 9 entries for the `cortex-x2` `trace` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `TRB_WRAP`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, `CTI_TRIGOUT4`, `CTI_TRIGOUT5`, `CTI_TRIGOUT6`, plus 1 more.

Control flow: Perf exposes the trace/CTI event names when the CPU PMU advertises them, allowing low-level trace integration counters to be selected by name. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `TRB_WRAP`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, and 4 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/trace.json -->
