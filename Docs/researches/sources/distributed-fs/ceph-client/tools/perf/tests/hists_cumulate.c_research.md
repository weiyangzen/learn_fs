# sources/distributed-fs/ceph-client/tools/perf/tests/hists_cumulate.c

## Purpose
Tests histogram accumulation of child periods and callchain rendering under four modes: no callchains/no children, callchains/no children, children/no callchains, and both callchains and children.

## Important APIs, Types, and Functions
- Static `fake_samples[]` defines ten samples across perf and bash processes.
- `fake_callchains[][10]` encodes synthetic `struct ip_callchain` payloads, including repeated/cyclic-looking xmalloc/malloc chains.
- `add_hist_entries()` resolves samples through `machine__resolve()` and adds them with either `hist_iter_normal` or `hist_iter_cumulative` based on `symbol_conf.cumulate_callchain`.
- `del_hist_entries()` erases output and input rb-tree nodes and deletes hist entries.
- `do_test()` collapses/resorts, output-resorts, then validates rb-tree order, self periods, accumulated child periods, and optional callchain nodes.
- `test1()` through `test4()` set `symbol_conf.use_callchain`, `symbol_conf.cumulate_callchain`, sample bits, sorting, and expected result tables.

## Control Flow
`test__hists_cumulate()` builds an evlist with `cpu-clock`, initializes machines and the fake machine fixture, obtains the first evsel, and runs the four mode-specific tests. Each mode configures global callchain/sorting state, adds hist entries from the same fake samples, validates expected output with `do_test()`, then deletes entries and resets output fields.

## State and Persistence
State is in-memory but includes global perf settings: `symbol_conf.use_callchain`, `symbol_conf.cumulate_callchain`, `callchain_param`, sample bits on the evsel, and output fields. Fake sample map/thread references are retained and later released by `put_fake_samples()`.

## Dependencies and Integration Points
Depends on the shared fake machine fixture, histogram iterators, callchain registration, sort setup, evsel/hists data structures, and rb-tree traversal. Registered as `DEFINE_SUITE("Cumulate child hist entries", hists_cumulate)`.

## Risks and Edge Cases
- The expected order is tightly coupled to perf's sort ordering and callchain accumulation rules.
- `do_test()` contains a TODO noting it only handles callchain validation for a single child node shape.
- Global callchain/symbol settings must be restored by surrounding test infrastructure or reset paths.
- The test expects exact accumulated periods such as 7000 for `perf/main`, so changes in duplicate folding or callchain propagation will surface as failures.

## Test Signals
Passing shows that histogram collapse/output resort preserves expected self periods, child accumulated periods, and callchain node sequences for synthetic perf/bash workloads. Failures identify the first mismatched hist entry or callchain node.
