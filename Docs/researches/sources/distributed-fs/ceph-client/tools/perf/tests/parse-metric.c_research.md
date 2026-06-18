# sources/distributed-fs/ceph-client/tools/perf/tests/parse-metric.c

## Purpose
Tests parsing and evaluation of perf metric expressions from the test PMU metrics table using synthetic runtime counter values.

## Important APIs, Types, and Functions
- `struct value` maps event names to synthetic counts.
- `find_value()` returns a configured event count or zero.
- `load_runtime_stat()` allocates aggregate stats and fills each evsel's count, enabled, and running values.
- `compute_single()` locates a `metric_expr` by metric name in `evlist->metric_events` and evaluates it with `test_generic_metric()`.
- `__compute_metric()` is the common driver: creates evlist, binds CPU map `0`, parses metric groups from `find_core_metrics_table("testarch", "testcpu")`, allocates stats, loads runtime counts, evaluates one or two metric names, then cleans up.
- Test functions cover IPC, Frontend_Bound_SMT, cache miss cycles, DCache L2 hits/misses, recursion failure, memory bandwidth, and metric groups.

## Control Flow
Each test builds a small `struct value` array with event counts, calls `compute_metric()` or `compute_metric_group()`, and asserts expected ratios. The shared compute path prepares an evlist in stat mode on CPU 0, parses the named metric or group into metric events, allocates stats, injects synthetic counts, evaluates requested metric expressions, frees stats, releases CPU map, and deletes the evlist. `test__parse_metric()` runs all metric cases in sequence.

## State and Persistence
All state is in-memory: evlists, CPU maps, metric events, allocated stats, and synthetic counts. No sysfs or perf fds are opened for real measurement.

## Dependencies and Integration Points
Depends on metric group parsing, PMU events test tables, expression evaluation, stat count structures, evlist stat allocation, and PMU helpers. Registered as `DEFINE_SUITE("Parse and process metrics", parse_metric)`.

## Risks and Edge Cases
- Exact floating-point equality is used for expected ratios such as `1.5`, `0.45`, `0.3`, `0.7`, and `1.28`.
- Missing event names resolve to zero, which is useful for synthetic setup but can hide accidental omissions unless expected values expose them.
- Recursion tests expect `compute_metric()` to return `-1` for recursive metric definitions `M1` and `M3`.
- The test relies on `testarch/testcpu` metrics being present and stable in the bundled PMU metrics table.

## Test Signals
Passing demonstrates metric parser/evaluator correctness for arithmetic ratios, nested derived metrics, metric groups, bandwidth unit math, and recursion detection using controlled counter data.
