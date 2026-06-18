<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1i_cache.json

## Purpose
NVIDIA T410 L1 instruction-cache topic table. It describes instruction-cache accesses, refills, local misses, read and prefetch classes, hardware prefetches, hit and line-fill-buffer classifications, dropped hardware prefetch requests, CFC entries, invalidations, and prefetch request types.

## APIs, Types, and Functions
The records combine standard aliases with T410-specific `EventName`/`EventCode` entries. Important names include `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`, `L1I_CACHE_RD`, `L1I_CACHE_PRFM`, `L1I_CACHE_HWPRF`, `L1I_CACHE_REFILL_RD`, `L1I_CFC_ENTRIES`, `L1I_HWPRF_REQ_DROP`, `L1I_PRFM_REQ`, `L1I_HWPRF_REQ`, and several `*_FPRF` filtered hit events.

## Control Flow, State, and Persistence
Perf build tooling emits the combined standard/direct table for T410. Runtime perf sessions select aliases for active counters; the JSON remains static metadata.

## Dependencies and Integration
Depends on ARM64 instruction-cache standard aliases and NVIDIA T410 event encodings. It integrates with frontend-bound metrics, branch behavior, ITLB metrics, and instruction-fetch latency calculations.

## Risks and Test Signals
Risks include prefetch hit filters being hard to interpret, dropped request counts not directly mapping to performance loss, and CFC entry semantics requiring vendor knowledge. Test signals are alias generation, hot-code versus large-code-footprint benchmarks, instruction-prefetch experiments, frontend cache-bound metric correlation, and expected changes in `l1i_cache_miss_ratio` and `instruction_fetch_average_latency`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1i_cache.json -->
