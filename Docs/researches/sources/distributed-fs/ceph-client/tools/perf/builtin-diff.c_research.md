<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-diff.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-diff.c

## Purpose
Implements `perf diff`, the perf.data comparison command. It opens two or more perf.data inputs, builds histograms from samples, pairs matching events and histogram entries across files, and renders differential columns such as baseline percentage, period, delta, absolute delta, ratio, weighted difference, cycles block difference, and hot stream comparison.

## Important APIs, Types, and Functions
The command entry point is `cmd_diff()`, which initializes hist support, configures a `struct perf_tool`, parses options, initializes symbols and sorting, and calls `__cmd_diff()`. `struct perf_diff` stores the active perf tool, time filtering state, branch-stack availability, and stream mode. `struct data__file` wraps one input `perf_data`, its session, selected histograms, optional stream state, and per-file `diff_hpp_fmt` column objects. Core processing functions are `diff__process_sample_event()`, `data_init()`, `check_file_brstack()`, `__cmd_diff()`, `data_process()`, `stream_process()`, `hists__precompute()`, `hists__process()`, and `ui_init()`.

Computation helpers include `compute_delta()`, `compute_ratio()`, `compute_wdiff()`, `compute_cycles_diff()`, `formula_delta()`, `formula_ratio()`, `formula_wdiff()`, and the `hist_entry__cmp_*` sort callbacks. Output integration uses perf hpp callbacks such as `hpp__color_baseline()`, `hpp__color_delta()`, `hpp__color_ratio()`, `hpp__color_wdiff()`, `hpp__color_cycles()`, `hpp__color_cycles_hist()`, `hpp__entry_global()`, `hpp__header()`, and `hpp__width()`. Cycles mode uses `struct block_hist`, `block_info__process_sym()`, `hist__account_cycles()`, and per-block hists.

## Control Flow
`cmd_diff()` configures the tool handlers for samples, mmap/mmap2, comm, fork/exit, lost, namespaces, and cgroups, then reads `diff.*` config and CLI options. `data_init()` chooses default files (`perf.data.old` and `perf.data`, or host/guest defaults), validates `--order`, and creates the `data__files` array. `check_file_brstack()` briefly opens each session to require branch stack data for cycles or stream modes. Non-stream mode registers hpp columns with `ui_init()` and prepares sort keys; stream mode enables srcline callchain settings and changes `sort_order`.

`__cmd_diff()` opens each perf session, parses per-file absolute or percentage time filters, applies CPU filters, processes events through `diff__process_sample_event()`, and collapses histograms. Sample processing resolves addresses, skips samples outside the time or CPU filters, and either adds normal histogram entries, stream callchain entries, or cycles block entries. After all inputs are processed, `data_process()` iterates baseline evsels, matches equivalent evsels by attr type/config, links or pairs entries, precomputes requested metrics, and prints the baseline hists. `stream_process()` compares only the old/new stream sets. Cleanup deletes sessions, frees column headers, data arrays, and time ranges.

## State and Persistence Behavior
State is process-local and centered in static globals: `data__files`, `data__files_cnt`, `pdiff`, `force`, `show_period`, `show_formula`, `show_baseline_only`, `cycles_hist`, `sort_compute`, `compute`, weighted-diff weights, `cpu_list`, and `cpu_bitmap`. Persistent input is read from perf.data files; output is textual only. The command mutates in-memory histogram entries by adding pair links and storing computed diff fields in `hist_entry->diff`. It also changes global perf symbol/sort/callchain configuration for the current invocation.

Time filtering is transient: `pdiff.ptime_range` is parsed per file and freed after that file is processed. Branch-stack capability is detected by reopening headers before the main processing pass. In stream mode, `evlist_streams` is allocated per file and deleted through `data__free()`.

## Dependencies and Integration Points
This file integrates with perf's session, evlist/evsel, histogram, hpp column, symbol, sort, time-utils, annotation, map/srcline, branch block, stream, config, pager, and parse-options subsystems. It depends on perf.data event handlers to populate machines/maps before resolving samples. It uses `symbol__init()`, `setup_sorting()`, `sort__setup_elide()`, and `setup_pager()` from wider perf command infrastructure.

Cycles mode depends on branch stacks and `util/block-info.h`; stream mode depends on callchain and branch callstack support. The `--symfs`, symbol, dso, comm, pid/tid, percentage, time, CPU, and kallsyms options share global symbol and sort configuration with other perf report-style commands.

## Risks and Edge Cases
This snapshot contains duplicated source fragments that would be compile-time risks if not hidden by the exact tree state: duplicated `for (i = 0; i < COMPUTE_MAX; i++)`, duplicated `struct data__file *d;`, and an extra `};` after `diff_usage`. Functional risks include event matching only by attr type/config, which can pair semantically different events if names or sample fields differ; divisions by histogram totals or old periods that rely on defensive fallbacks; stream/cycles modes failing silently when every file lacks branch stacks; and global sort/callchain state changes leaking across command setup paths in-process.

Time parsing is subtle because absolute ranges can be colon-separated per file, while percentage ranges are parsed against each session. `sort_compute` is one-based by default and must remain below the number of files. CPU filtering relies on `sample->cpu` being valid. Cycles block output relies on srcline lookup and block indexes lining up between paired block histograms.

## Test Signals
Useful tests include `perf diff` with default two files, multiple input files, a single explicit new file, host/guest default names, each compute mode (`delta`, `delta-abs`, `ratio`, `wdiff:w1,w2`, `cycles`), `--cycles-hist`, `--stream`, `--baseline-only`, `--period`, `--formula`, `--order`, `--time` absolute and percentage ranges, and `--cpu`. Regression signals are correct hpp columns and sort ordering, graceful rejection of cycles/stream without branch stacks, correct handling of missing event pairs, no callchain sorting in normal diff mode, and no leaks or crashes on invalid files or invalid time strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-diff.c -->
