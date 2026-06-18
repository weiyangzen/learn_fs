<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l2d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l2d_cache.json

## Purpose
NVIDIA T410 L2 data-cache topic table. It covers L2D accesses/refills/write-backs, read/write splits, invalidations, local misses, read-write/prefetch classes, hardware prefetch and generic prefetch refills, instruction fetch/TBW/PF refill classes, L1-prefetch-induced traffic, virtual alias backsnoop, and filtered hit/LFB behavior.

## APIs, Types, and Functions
The JSON uses `ArchStdEvent` plus direct event records. Names include `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_LMISS_RD`, `L2D_CACHE_RW`, `L2D_CACHE_PRFM`, `L2D_CACHE_IF_REFILL`, `L2D_CACHE_TBW_REFILL`, `L2D_CACHE_PF_REFILL`, `L2D_CACHE_L1PRF`, `L2D_CACHE_REFILL_L1PRF`, and `L2D_CACHE_BACKSNOOP_L1D_VIRT_ALIASING`.

## Control Flow, State, and Persistence
Build-time generation resolves standard aliases and stores T410 direct encodings. Runtime perf aliases program counters on the selected T410 PMU; the JSON has no mutable state.

## Dependencies and Integration
Depends on ARM64 L2D aliases and T410-specific L2 events. It integrates with L1D, LLC, bus, memory, and T410 metrics for L2 miss ratios, MPKI, prefetch accuracy, and backend cache-bound analysis.

## Risks and Test Signals
Risks include overlap among L1 prefetch, hardware prefetch, and demand refills; virtual alias backsnoop events being rare and platform-sensitive; and TBW/PF refill meanings requiring vendor context. Test signals are cache-size sweep benchmarks, instruction/data refill separation tests, prefetch accuracy metrics, and consistency between L2 refills and LLC/bus traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l2d_cache.json -->
