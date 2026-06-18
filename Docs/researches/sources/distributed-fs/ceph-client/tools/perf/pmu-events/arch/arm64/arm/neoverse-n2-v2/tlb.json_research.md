<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/tlb.json

Purpose: Declares instruction/data TLB access, refill, read/write, and walk PMU aliases.

Important data contract: JSON array with 16 entries for the `neoverse-n2-v2` `tlb` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 16 entries carry local descriptions. Representative names: `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, `L2D_TLB`, `DTLB_WALK`, `ITLB_WALK`, plus 8 more.

Control flow: Perf maps these aliases into generated event tables used for TLB miss ratios, MPKI metrics, and direct page-walk counters.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, and 11 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/tlb.json -->
