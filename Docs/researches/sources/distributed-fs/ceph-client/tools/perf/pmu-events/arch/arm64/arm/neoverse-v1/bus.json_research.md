<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 4 entries for the `neoverse-v1` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/bus.json -->
