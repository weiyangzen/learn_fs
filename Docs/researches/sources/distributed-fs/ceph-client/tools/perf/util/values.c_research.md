# sources/distributed-fs/ceph-client/tools/perf/util/values.c

## Purpose

`values.c` accumulates read-format counter values by PID/TID and evsel, then prints them in pretty or raw tabular form.

## Important APIs, Types, and Functions

Public functions are `perf_read_values_init()`, `perf_read_values_destroy()`, `perf_read_values_add_value()`, and `perf_read_values_display()`. Internal helpers grow thread arrays, find or create thread rows, grow counter arrays, find or create counter columns, and render pretty/raw output.

## Control Flow and State

Initialization allocates arrays for 16 threads and 16 counters. Adding a value creates a row for `(pid, tid)` if needed, creates a counter column for the evsel if needed, and accumulates into `value[row][column]`. Pretty display computes dynamic column widths for PID/TID and event names/counts. Raw display prints PID, TID, event name, raw evsel index, and count for each row/column pair.

## Dependencies and Integration Points

It depends on evsel names and indices, debug logging, and zalloc helpers. It is used by perf read/stat style reporting paths that need per-thread counter summaries.

## State and Persistence Behavior

All state is in caller-owned `struct perf_read_values`. Destroy frees per-thread value arrays and all top-level arrays. Values are accumulated in memory only.

## Risks and Test Signals

Risks include partial realloc leaks in enlarge paths, raw display missing line terminators, large table memory growth, and evsel pointer identity being the counter key. Tests should initialize/destroy, add repeated values, force thread/counter growth, print pretty/raw output, and handle allocation failures.
