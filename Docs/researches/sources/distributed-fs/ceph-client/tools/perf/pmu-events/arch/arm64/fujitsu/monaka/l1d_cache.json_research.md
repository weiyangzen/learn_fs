<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1d_cache.json

## Purpose
Monaka L1 data-cache topic table. It exposes standard and implementation-defined aliases for L1D access, refill, write-back, read/write split, demand access, coherence requests, miss/hit classification, line-fill-buffer hits, prefetch activity, and refill pressure per cycle.

## APIs, Types, and Functions
The file mixes `ArchStdEvent` entries with direct event codes such as `L1D_CACHE_DM`, `L1D_CACHE_DM_RD`, `L1D_CACHE_DM_WR`, `L1D_CACHE_REFILL_DM*`, and `L1D_CACHE_BTC`. Standard aliases include `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_HIT`, `L1D_LFB_HIT_*`, and `L1D_CACHE_REFILL_PERCYC`.

## Control Flow, State, and Persistence
`jevents.py` resolves standard aliases and emits direct encodings into the Monaka PMU event table. Runtime perf sessions program selected counters; the JSON retains only the static event catalog.

## Dependencies and Integration
Depends on ARM64 common event aliases plus Monaka event codes in the 0x0200 range. It integrates with `hwpf.json`, `memory.json`, `tlb.json`, and `stall.json` to diagnose demand misses, prefetch behavior, write traffic, and backend memory stalls.

## Risks and Test Signals
Risks include overlap between aggregate access/refill counters and demand/prefetch subcounters, nonexclusive LFB hit classifications, and coherence events being platform-sensitive. Test signals are generation success, load/store/cache-thrashing microbenchmarks, prefetch-on/off comparisons, and derived miss ratios that stay bounded when using matching numerator and denominator aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1d_cache.json -->
