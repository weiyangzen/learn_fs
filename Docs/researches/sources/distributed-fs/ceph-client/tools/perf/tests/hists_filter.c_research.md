# sources/distributed-fs/ceph-client/tools/perf/tests/hists_filter.c

## Purpose
Validates histogram filtering by thread, DSO, symbol, socket, and combined filters while ensuring total sample/entry/period statistics remain invariant and non-filtered statistics change correctly.

## Important APIs, Types, and Functions
- `struct sample` includes pid, IP, resolved thread/map/symbol, and socket.
- `fake_samples[]` supplies ten samples, with one duplicate `perf/perf/main` that collapses to produce nine hist entries.
- `add_hist_entries()` iterates every evsel, resolves samples, sets `al.socket`, and uses `hist_entry_iter__add()` with `hist_iter_normal`.
- `put_fake_samples()` releases stored map references.
- `test__hists_filter()` drives parsing, fake machine setup, sorting, histogram population, collapse/output resort, and filter assertions.

## Control Flow
The test creates an evlist with `cpu-clock` and `task-clock`, initializes the fake machine, calls `setup_sorting()`, and adds the same ten synthetic samples to each evsel. For each evsel it verifies baseline totals: 10 samples, 9 entries, total period 1000, all non-filtered stats equal totals. It then applies and removes filters: bash thread, kernel DSO, symbol string `main`, socket `2`, and a combined thread+DSO filter. After each filter it asserts total stats are unchanged and non-filtered samples/entries/periods match expected reduced counts.

## State and Persistence
The test mutates per-hists filter fields (`thread_filter`, `dso_filter`, `symbol_filter_str`, `socket_filter`) and histogram rb-trees. It also holds map references in static sample entries until cleanup. No persistent storage is used.

## Dependencies and Integration Points
Uses shared histogram fixture, parse-events, evlist/evsel hists, machine resolution, sorting, and `hists__filter_by_*` APIs. Registered as `DEFINE_SUITE("Filter hist entries", hists_filter)`.

## Risks and Edge Cases
- Expected counts depend on the duplicate main sample collapsing into one entry while still counting as three samples for symbol filtering.
- Static sample map references must be put after all evsels are processed to avoid leaks across repeated suite execution.
- Combined filter coverage is limited to thread+DSO, not all possible filter combinations.

## Test Signals
Passing indicates each filter updates `nr_non_filtered_*` and `total_non_filtered_period` correctly without corrupting raw totals. Verbose mode can print intermediate histograms for diagnosis.
