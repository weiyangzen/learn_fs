# sources/distributed-fs/ceph-client/tools/perf/util/stat-display.c

## Purpose

`stat-display.c` is the output layer for `perf stat`. It formats processed counter values, runtime percentages, noise, metric expressions, metric groups, cgroup labels, aggregation IDs, interval timestamps, headers, footers, and optional iostat output in standard, CSV, JSON, and metric-only modes.

## Important APIs, Types, and Functions

The exported entry point is `evlist__print_counters()`. It also exports `metric_threshold_classify__color()`. Important private structures and functions include `struct outstate`, `printout()`, `print_counter_aggrdata()`, `print_aggr()`, `print_aggr_cgroup()`, `print_counter()`, `print_no_aggr_metric()`, `print_percore()`, `print_cgroup_counter()`, metric callback implementations for std/CSV/JSON/metric-only modes, aggregation ID printers, header/footer printers, and `should_skip_zero_counter()`.

## Control Flow and Data Flow

`evlist__print_counters()` uniquifies event names, prepares iostat selection and interval timestamps, prints headers, then dispatches by aggregation mode. Aggregated modes iterate `config->aggr_map`; global/thread modes print all counters on one metric-only line or per counter line; `AGGR_NONE` either prints per-CPU metric-only rows or per-counter/per-core rows. Each row flows through `print_counter_aggrdata()`, which skips merged alias events, default-metric hidden events, irrelevant zero rows, and then formats counter value, noise, runtime, and shadow metrics through callback tables selected by output format.

## State and Persistence Behavior

Display state is transient in `struct outstate`: JSON comma state, standard-output newline behavior, CSV padding, timestamp, current aggregation ID, cgroup, evsel, and aggregation count. A static `num_print_iv` throttles repeated interval headers. `config->print_free_counters_hint` may be set when supported counters did not run. No data is persisted beyond the output stream.

## Dependencies and Integration Points

This file depends on processed aggregation state in `evsel->stats`, metric evaluation in `stat-shadow.c`, cgroup metadata, CPU/thread aggregation maps, iostat helpers, PMU/hybrid detection, tool PMU events, color output, sysctl checks, and target metadata. It is the last stage after `stat.c` computes counters and before users see results.

## Risks and Edge Cases

The formatting matrix is broad: metric-only plus CSV/JSON, default metricgroups, cgroups, iostat, intervals, hybrid PMUs, percore events, unsupported/skippable events, and summary CSV all alter output shape. JSON and CSV functions manually manage separators, so missing state resets can corrupt output. `should_skip_zero_counter()` must not hide meaningful zeroes for metric computation. Runtime percentages divide by enabled time and rely on earlier bad-count detection to avoid zero denominators. Static metricgroup header state can affect repeated print passes.

## Test Signals

Tests should compare standard/CSV/JSON output for all aggregation modes, metric-only headers and rows, default metricgroup hiding/showing, cgroup grouping, iostat output, interval timestamps, percore aggregation display, unsupported/not-counted counters, NMI watchdog hint behavior, hybrid PMU merge skipping, and repeated-run noise/footer formatting.
