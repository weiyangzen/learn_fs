<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/ll_cache.json

## Purpose
Monaka last-level cache summary topic. It selects standard aliases for last-level read accesses and read misses, described locally in terms of L3D cache activity and L2D refill miss behavior.

## APIs, Types, and Functions
The two records are `ArchStdEvent` aliases `LL_CACHE_RD` and `LL_CACHE_MISS_RD`, each with a Monaka-specific `BriefDescription`. There are no local event codes or functions.

## Control Flow, State, and Persistence
The build resolves the two aliases from the ARM64 standard catalog and includes them in the generated Monaka PMU table. Runtime measurement state is held by PMU counters only.

## Dependencies and Integration
Depends on ARM64 standard last-level cache events and the Monaka mapfile mapping. It integrates with `l3_cache.json` as a concise denominator/numerator pair for high-level LLC miss analysis.

## Risks and Test Signals
Risks include the `LL_CACHE_MISS_RD` description inheriting the L3 miss inaccuracy warning and users assuming LL-cache aliases are independent from L3-topic events. Test signals are alias generation, `perf stat -e LL_CACHE_RD,LL_CACHE_MISS_RD`, and workload sweeps that show read misses increasing once data exceeds local L3 capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/ll_cache.json -->
