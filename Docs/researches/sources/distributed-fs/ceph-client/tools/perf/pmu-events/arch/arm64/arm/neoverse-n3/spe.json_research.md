<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spe.json

Purpose: Declares Statistical Profiling Extension sampling pipeline PMU aliases.

Important data contract: JSON array with 10 entries for the `neoverse-n3` `spe` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 10 entries carry local descriptions. Representative names: `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`, `SAMPLE_FEED_BR`, `SAMPLE_FEED_LD`, `SAMPLE_FEED_ST`, `SAMPLE_FEED_OP`, plus 2 more.

Control flow: Perf exposes these names for SPE feed/pop/filter/collision accounting; they complement, but do not configure, SPE sampling itself.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`, `SAMPLE_FEED_BR`, and 5 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spe.json -->
