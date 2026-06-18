<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/ll_cache.json

## Purpose
NVIDIA T410 last-level/L3 cache topic table. It exposes L3 allocation, refill, access, read, local miss, read-write, prefetch, hardware prefetch, L1/L2 prefetch-induced traffic, instruction fetch and memory-management refills, and standard `LL_CACHE_RD`/`LL_CACHE_MISS_RD` aliases.

## APIs, Types, and Functions
The file combines `ArchStdEvent` entries with direct event names such as `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_REFILL_RD`, `L3D_CACHE_LMISS_RD`, `L3D_CACHE_RW`, `L3D_CACHE_PRFM`, `L3D_CACHE_REFILL_RWL1PRFL2PRF`, `L3D_CACHE_REFILL_IF`, `L3D_CACHE_REFILL_MM`, `L3D_CACHE_L1PRF`, and `L3D_CACHE_L2PRF`.

## Control Flow, State, and Persistence
Perf generation resolves the standard LL aliases and emits T410 L3 direct encodings. Runtime state is limited to active PMU counters selected by perf.

## Dependencies and Integration
Depends on ARM64 LLC aliases and NVIDIA T410 L3 event definitions. It integrates with L2D cache, bus, memory, and metrics for LLC read hit/miss ratios, MPKI, demand access/miss counts, and prefetch accuracy/coverage.

## Risks and Test Signals
Risks include aggregate L3 events overlapping with L1/L2 prefetch-origin subevents, instruction and memory-management refills requiring careful attribution, and LLC metrics using read-only denominators. Test signals are generated alias success, LLC working-set sweeps, prefetch-heavy tests, instruction-fetch refill tests, and consistency between LLC misses and bus/memory traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/ll_cache.json -->
