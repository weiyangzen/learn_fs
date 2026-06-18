<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1d_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 12 entries for the `neoverse-n3` `l1d cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 12 entries carry local descriptions. Representative names: `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_INNER`, `L1D_CACHE_REFILL_OUTER`, plus 4 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, and 7 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1d_cache.json -->
