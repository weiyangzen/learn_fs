# sources/distributed-fs/ceph-client/tools/perf/util/stat.h

## Purpose

`stat.h` defines the shared data structures and public API for `perf stat` processing, metric printing, and counter display.

## Important APIs, Types, and Functions

Key structures are `struct stats` for Welford repeated-run statistics, `struct perf_stat_aggr` for one aggregate bucket, `struct perf_stat_evsel` for per-evsel stat-private state, `enum aggr_mode`, `aggr_get_id_t`, `struct perf_stat_config`, `enum metric_threshold_classify`, and `struct perf_stat_output_ctx`.

The header declares stat math functions, allocation/reset/free/copy functions, counter processing, merge/percore processing, perf event stat processing/fprintf helpers, `evlist__print_counters()`, metric-shadow functions, and `test_generic_metric()`.

## Control Flow and Data Flow

Callers configure `struct perf_stat_config`, allocate evlist stats, read counters into evsel counts, process counters into aggregates, optionally merge/percore-process them, and finally print counters through `evlist__print_counters()`. Metric output is callback-driven through `perf_stat_output_ctx`.

## State and Persistence Behavior

The header declares external `stat_config`. Most fields in `perf_stat_config` are command-line/session state: output mode, aggregation mode, interval/timing options, cgroup lists, maps, output stream, and metric behavior. `init_stats()` initializes repeated-run state with max zero and min all-ones.

## Dependencies and Integration Points

It depends on Linux types, stdio/resource headers, cpumap, counts, evsel/evlist/session forward declarations, and perf stat record types. It is the shared contract between stat collection, metric evaluation, display, and command-line code.

## Risks and Edge Cases

`perf_stat_config` is broad and mutable, so adding fields requires initializing all command paths. Aggregation mode ordering is used by display arrays in `stat-display.c`; mismatches can corrupt headers. Metric callback contracts must agree about whether `fmt`/`unit` may be NULL.

## Test Signals

Build coverage plus stat command tests for every aggregation/output mode validate the header contract. Static assertions in display code help catch enum/color array drift.
