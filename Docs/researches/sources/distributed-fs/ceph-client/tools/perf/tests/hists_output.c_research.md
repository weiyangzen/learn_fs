# sources/distributed-fs/ceph-client/tools/perf/tests/hists_output.c

## Purpose
Validates histogram output sorting and field selection for several combinations of `field_order` and `sort_order`.

## Important APIs, Types, and Functions
- `fake_samples[]` defines ten samples with cpu, pid, and IP data; duplicate perf main entries collapse depending on sort keys.
- `add_hist_entries()` resolves samples and adds normal hist entries with period 100.
- `del_hist_entries()` removes all output/input rb-tree entries after each case.
- `test1()` verifies default sort (`comm,dso,sym`).
- `test2()` verifies mixed fields `overhead,cpu` with sort key `pid`.
- `test3()` verifies fields-only output `comm,overhead,dso`.
- `test4()` verifies duplicate field handling with `dso,sym,comm,overhead,dso` and sort `sym`.
- `test5()` verifies full sort keys without overhead field using `cpu,pid,comm,dso,sym` and sort `dso,pid`.

## Control Flow
The suite creates a `cpu-clock` evlist, initializes the fake machine, obtains the first evsel, and runs five test functions. Each test sets global `field_order`/`sort_order`, calls `setup_sorting()`, adds hist entries, runs `hists__collapse_resort()` and `evsel__output_resort()`, then walks the output rb-tree in expected order and asserts selected fields and periods.

## State and Persistence
State is in-memory but uses global output/sort fields that are reset after each test with `reset_output_field()`. Static map references are held in `fake_samples[]` and released at suite cleanup.

## Dependencies and Integration Points
Depends on sort-key parsing, output field setup, histogram collapse and output resorting, fake machine resolution, and rb-tree traversal. Registered as `DEFINE_SUITE("Sort output of hist entries", hists_output)`.

## Risks and Edge Cases
- Expected rb-tree order is exact and will fail for legitimate sort-order changes.
- The tests check representative entries in `test2` but not the entire expected output, while other tests are more exhaustive.
- Global `field_order` and `sort_order` must be cleaned between cases to avoid cross-test contamination.

## Test Signals
Passing means selected field/sort combinations produce stable grouping, ordering, and period aggregation. Verbose mode prints formatted hist output for diagnostics.
