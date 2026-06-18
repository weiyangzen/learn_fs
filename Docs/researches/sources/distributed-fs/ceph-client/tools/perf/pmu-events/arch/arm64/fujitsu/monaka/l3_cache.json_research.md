<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l3_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l3_cache.json

## Purpose
Monaka L3 cache topic table. It represents L3 activity mostly as L2D refill traffic reaching L3, with demand/prefetch, read/write, hit/miss, PFTGT buffer, local memory, remote memory, local/remote L2, and local/remote L3 classifications.

## APIs, Types, and Functions
The file combines `ArchStdEvent` aliases (`L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_LMISS_RD`) with direct event names such as `L2D_CACHE_REFILL_L3D_CACHE*`, `L2D_CACHE_REFILL_L3D_MISS*`, `L2D_CACHE_REFILL_L3D_HIT*`, and topology-specific `*_L_MEM`, `*_FR_MEM`, `*_L_L2`, `*_NR_L2`, `*_NR_L3`, `*_FR_L2`, and `*_FR_L3`.

## Control Flow, State, and Persistence
The JSON is compiled into perf's generated event table for Monaka. At runtime, aliases program PMU counters for the selected core; persistence is limited to the checked-in JSON and generated perf build artifacts.

## Dependencies and Integration
Depends on Monaka L3 fabric encodings and common ARM64 last-level cache aliases. It integrates with NUMA/locality analysis, L2 refill events, memory traffic analysis, and `ll_cache.json` aliases that summarize last-level read and miss behavior.

## Risks and Test Signals
Risks include notes in the descriptions that several L3 hit/miss events may count inaccurately, topology labels being misunderstood, and aggregate L3 access definitions relying on L2 refill plus clean victim write-back behavior. Test signals are generation success, local versus remote NUMA memory tests, L3-resident and DRAM-resident working-set sweeps, and sanity checks that inaccurate-note events are treated as advisory rather than exact accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l3_cache.json -->
