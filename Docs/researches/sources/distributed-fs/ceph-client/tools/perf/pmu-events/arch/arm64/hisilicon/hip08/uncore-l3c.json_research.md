<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-l3c.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-l3c.json

## Purpose
Hip08 uncore L3 cache PMU event table. It records read/write traffic and hits in CPIPE and SPIPE paths, victim counts, invalidations, CPU and ring retries, and dropped prefetches.

## APIs, Types, and Functions
Each event uses `EventName`, `ConfigCode`, `BriefDescription`, and `Unit`. Aliases include `rd_cpipe`, `wr_cpipe`, `rd_hit_cpipe`, `wr_hit_cpipe`, `victim_num`, `rd_spipe`, `wr_spipe`, `rd_hit_spipe`, `wr_hit_spipe`, `back_invalid`, `retry_cpu`, `retry_ring`, and `prefetch_drop`.

## Control Flow, State, and Persistence
Perf encodes the uncore table at build time and uses config codes at runtime for L3C PMU instances. The JSON has no state and does not define cross-instance aggregation.

## Dependencies and Integration
Depends on the Hip08 L3C uncore PMU driver and unit naming. It integrates with HHA directory/coherence counters, DDRC traffic counters, and core L2/L3 miss metrics to diagnose LLC behavior and fabric backpressure.

## Risks and Test Signals
Risks include CPIPE/SPIPE meaning being vendor-specific, retries indicating congestion but not the full source, and prefetch-drop interpretation depending on hardware prefetch policy. Test signals are `perf list` visibility, cache-resident and cache-thrashing workloads, retry increases under contention, and hit/access ratios that move predictably with working-set size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-l3c.json -->
