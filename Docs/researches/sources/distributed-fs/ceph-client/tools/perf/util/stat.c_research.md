# sources/distributed-fs/ceph-client/tools/perf/util/stat.c

## Purpose

`stat.c` owns `perf stat` counter storage, aggregation, delta scaling, repeated-run statistics, per-package de-duplication, alias merging, per-core postprocessing, and stat event ingestion from perf data.

## Important APIs, Types, and Functions

Public functions include `update_stats()`, `avg_stats()`, `stddev_stats()`, `rel_stddev_stats()`, `evlist__alloc_stats()`, `evlist__free_stats()`, `evlist__reset_stats()`, `evlist__alloc_aggr_stats()`, `evlist__reset_aggr_stats()`, `evlist__reset_prev_raw_counts()`, `evlist__copy_prev_raw_counts()`, `evlist__copy_res_stats()`, `perf_stat_process_counter()`, `perf_stat_merge_counters()`, `perf_stat_process_percore()`, `perf_event__process_stat_event()`, and stat event fprintf helpers.

Private helpers allocate/free/reset `perf_stat_evsel`, aggregate arrays, group data, raw and previous raw counts, per-package masks, and percore aggregate values.

## Control Flow and Data Flow

Allocation starts with `evlist__alloc_stats()`, which allocates per-evsel stat-private data, raw counts, and optional previous raw counts sized from the aggregation map. Processing a counter calls `process_counter_maps()`, which visits every thread/CPU count, applies per-package duplicate suppression, computes deltas unless the event is snapshot-based, scales counts, and folds values into either thread aggregates or CPU aggregation buckets. In global mode, aggregate zero is also fed into Welford repeated-run stats. After all counters are processed, optional alias merging combines wildcard-matched uncore/hybrid events, and percore processing duplicates core totals across sibling CPU entries for display.

Recorded stat events are ingested by resolving event ID to evsel, CPU to cpumap index, and thread index to count storage, then storing value/enabled/running and marking the counter supported.

## State and Persistence Behavior

State lives in `evsel->stats`, `evsel->counts`, `evsel->prev_raw_counts`, and optional `evsel->per_pkg_mask`. Repeated-run summary state is `res_stats`. Aggregated counts track value/enabled/running, contributing entry count, failure, and used flags. On-disk persistence is only through perf record stat events read by `perf_event__process_stat_event()`.

## Dependencies and Integration Points

The file depends on counts, CPU/thread maps, aggregation ID helpers, evsel/evlist/session objects, target behavior, perf event headers, and hashmap utilities. It feeds `stat-display.c` and `stat-shadow.c`.

## Risks and Edge Cases

Per-package de-duplication ignores entries that did not run so later running CPUs in the same package can still contribute; this is subtle and important. Aggregation failure zeroes a whole aggregate for consistent interval output except for global mode. Allocation failures must unwind all evsels. Alias merge requires matching aggregate counts. `evlist__copy_prev_raw_counts()` assumes previous counts were allocated. `perf_event__process_stat_event()` rejects unknown IDs, invalid CPUs, and missing count slots.

## Test Signals

Tests should cover Welford mean/stddev, allocation/unwind paths, delta versus snapshot counters, scaled and unscaled counts, per-package duplicate suppression, global/thread/socket/core/node aggregation, unsupported/not-running failure propagation, wildcard alias merge, percore postprocessing, and perf.data stat event replay.
