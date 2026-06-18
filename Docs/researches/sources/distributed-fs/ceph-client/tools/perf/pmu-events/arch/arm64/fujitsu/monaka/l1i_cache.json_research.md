<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1i_cache.json

## Purpose
Monaka L1 instruction-cache topic table. It covers instruction cache access, refill, demand reads, local misses, hardware and software prefetch refills, hits, line-fill-buffer hits, and refill pressure per cycle.

## APIs, Types, and Functions
The JSON uses standard aliases plus direct Monaka definitions `L1I_CACHE_DM_RD` and `L1I_CACHE_REFILL_DM_RD`. Other key aliases are `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`, `L1I_CACHE_HWPRF`, `L1I_CACHE_REFILL_HWPRF`, `L1I_CACHE_HIT_RD`, `L1I_CACHE_HIT`, `L1I_LFB_HIT_RD`, `L1I_CACHE_REFILL_PRF`, and `L1I_CACHE_REFILL_PERCYC`.

## Control Flow, State, and Persistence
The perf build resolves `ArchStdEvent` records and stores direct encodings in generated tables. Runtime selection is static per Monaka CPU; measurement state is PMU counter state only.

## Dependencies and Integration
Depends on common ARM64 instruction-cache events and Monaka event-code definitions. It integrates with frontend stalls, ITLB events, branch/pipeline events, and the `core-imp-def.json` prefetch alias.

## Risks and Test Signals
Risks include demand and prefetch access overlap, instruction-side hardware prefetch behavior varying with firmware settings, and ratio mistakes when pairing all-access denominators with demand-only numerators. Test signals are `perf list` exposure, code-footprint microbenchmarks increasing refills, hot-loop tests showing hits, and frontend memory-bound stalls correlating with L1I/L2I miss activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1i_cache.json -->
