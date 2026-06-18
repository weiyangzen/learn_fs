<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l2_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l2_cache.json

## Purpose
Monaka L2 cache and L2 TLB topic table. It describes L2D access, refill, write-back, demand read/write splits, exclusive/atomic write refills, coherence events, victim/clean/non-temporal/DC ZVA write-backs, flush-back, hit/miss, prefetch, and refill pressure counters.

## APIs, Types, and Functions
The file combines `ArchStdEvent` aliases with direct Monaka events including `L2D_CACHE_DM*`, `L2D_CACHE_HWPRF_ADJACENT`, `L2D_CACHE_REFILL_DM_WR_EXCL`, `L2D_CACHE_REFILL_DM_WR_ATOM`, `L2D_CACHE_BTC`, `L2D_CACHE_WB_VICTIM_CLEAN`, `L2D_CACHE_WB_NT`, `L2D_CACHE_WB_DCZVA`, and `L2D_CACHE_FB`.

## Control Flow, State, and Persistence
Build-time generation resolves standard aliases and writes direct event descriptors into perf. Runtime state is only the active PMU counter set selected by a perf command; the JSON remains static source metadata.

## Dependencies and Integration
Depends on common ARM64 L2 cache/TLB aliases plus Monaka-specific encodings. It integrates with L1D, L3, LL-cache, hardware-prefetch, TLB, memory, and backend stall topics to trace demand traffic beyond the L1.

## Risks and Test Signals
Risks include write-back subcategories not summing to aggregate write-backs, adjacent prefetch semantics being implementation-specific, and coherence events depending on multi-core sharing patterns. Test signals include successful `jevents.py` output, cache-size sweep microbenchmarks, non-temporal store and DC ZVA tests, atomic/write-exclusive workloads, and derived L2 miss ratios using consistent event scopes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l2_cache.json -->
