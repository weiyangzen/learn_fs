<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1d_cache.json

## Purpose
NVIDIA T410 L1 data-cache topic table. It covers standard L1D accesses/refills/write-backs, read/write splits, inner/outer refill sources, invalidations, read-write and prefetch classes, demand miss/refill classes, hardware/software prefetch hit and refill classifications, line-fill-buffer hits, and outer LLC/DRAM/remote refill classes.

## APIs, Types, and Functions
The file mixes `ArchStdEvent` aliases with direct T410 event records. Names include `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_INNER`, `L1D_CACHE_REFILL_OUTER`, `L1D_CACHE_RW`, `L1D_CACHE_PRFM`, `L1D_CACHE_HIT_RW_FPRF*`, `L1D_LFB_HIT_RW_FPRF*`, and `L1D_CACHE_REFILL_OUTER_*`.

## Control Flow, State, and Persistence
Build-time generation resolves standard events and includes T410-specific encodings. Runtime state is PMU counter state selected by perf aliases; the JSON does not persist measurements.

## Dependencies and Integration
Depends on ARM64 cache aliases and T410 implementation-specific refill/source events. It integrates with T410 metrics for L1D miss ratio, MPKI, prefetch accuracy/coverage, demand accesses/misses, and backend cache-bound analysis.

## Risks and Test Signals
Risks include overlapping demand, prefetch, hardware prefetch, and outer-source categories; remote refill classifications being topology-specific; and metrics requiring matching denominators. Test signals are `jevents.py` success, streaming/random load-store tests, prefetch control tests, cache-size sweeps, and metric sanity for L1D demand and prefetch groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1d_cache.json -->
