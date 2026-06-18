# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/cache.json

## Purpose

This file defines 29 POWER8 raw PMU events for data-cache reload source attribution, demand load L1 behavior, data-side tablewalk and SLB misses, and store misses. It distinguishes local L2/L3 hits, L2/L3 misses, dispatch conflicts, MEPF state, local L4, on-chip cache, off-chip cache, remote and distant L2/L3 modified or shared sources, and data-side page-table-entry sourcing.

## APIs, types, and schema

POWER8 event entries use `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. The public contract includes events such as `PM_DATA_FROM_L2`, `PM_DATA_FROM_L3`, `PM_DATA_FROM_L3MISS`, `PM_DATA_FROM_RL2L3_MOD`, `PM_DATA_FROM_DL2L3_SHR`, `PM_DATA_TABLEWALK_CYC`, `PM_DSLB_MISS`, `PM_L1_DCACHE_RELOADED_ALL`, `PM_LD_MISS_L1`, `PM_LD_REF_L1`, and `PM_ST_MISS_L1`.

## Control flow and integration

Perf's PMU generator turns these definitions into generated event tables. Runtime consumers use them directly for cache locality studies or indirectly through any POWER8 metric formulas in the broader PMU tree. The event taxonomy lets users decompose demand-load cache misses by cache level, conflict type, coherency state, and topology distance.

## State and persistence

The file is static. Event names, codes, and descriptions persist into perf output. The `PublicDescription` text provides longer user-facing semantics and is therefore part of the documentation contract as well as the generated event metadata.

## Dependencies

Dependencies include POWER8 PMU encodings, hardware definitions for MEPF, local/remote/distant topology, L4 cache behavior, SLB and tablewalk counters, and perf's JSON generation path. Integration points include generated `pmu-events.c`, `perf list`, direct `perf stat -e` use, and any cache-miss metric formulas.

## Risks

The file contains fine-grained topology and coherency categories that are easy to aggregate incorrectly. Some descriptions have historical wording issues, so tests cannot rely on prose equality alone. Event semantics may depend on POWER8 system topology and L4 availability. Mis-coded reload source events can lead to misleading NUMA/cache locality conclusions.

## Test signals

Use JSON validation, event-name and event-code uniqueness checks, generated PMU build tests, and `perf list` inspection. Hardware validation should compare demand-load miss decomposition against broad counters such as `PM_LD_MISS_L1` and `PM_L1_DCACHE_RELOADED_ALL`.
