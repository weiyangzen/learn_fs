# subset-b-006771 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sort.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/sort.c

## Purpose

`sort.c` is perf report's central sort-key and output-field registry. It translates user-facing `--sort` and `--fields` names into `perf_hpp_fmt` columns, comparators, collapse functions, display functions, filters, and per-entry initializers for normal sample reports, branch-stack reports, memory reports, tracepoint reports, `perf top`, and `perf diff`.

## Important APIs, Types, and Functions

The file exports global sort configuration such as `sort_order`, `field_order`, `sort__mode`, `parent_pattern`, `ignore_callees_regex`, `default_mem_sort_order`, and `chk_double_cl`. It defines many `struct sort_entry` instances, including exported entries `sort_comm`, `sort_dso`, `sort_sym`, `sort_parent`, branch entries such as `sort_dso_from` and `sort_sym_to`, memory entries such as `sort_mem_dcacheline`, and data-type entries such as `sort_type`.

Public functions include `setup_sorting()`, `setup_output_field()` through the internal `__setup_output_field()`, `reset_output_field()`, `reset_dimensions()`, `sort_dimension__add()`, `output_field_add()`, `hpp_dimension__add_output()`, `sort__setup_elide()`, `perf_hpp__set_elide()`, `hist_entry__filter()`, `sort_help()`, `hist_entry__srcline()`, `sort__comm_nodigit_len()`, and memory-address comparators `sort__iaddr_cmp()`, `sort__daddr_cmp()`, and `sort__dcacheline_cmp()`.

## Control Flow and Data Flow

Setup starts in `setup_sorting()`. It parses default or user-provided sort keys, appends default overhead/latency output fields when needed, registers sort fields into `perf_hpp_list`, resets dimension state, initializes default hpp columns, parses `field_order`, allocates memory-stat columns, and then synchronizes sort and output lists. `sort_dimension__add()` searches common, branch, memory, hpp, and trace dynamic-field tables; it rejects mode-incompatible branch or memory keys and skips architecture-specific pipeline-stage keys when unsupported by `perf_env__arch()`.

At display time, each hpp wrapper delegates to the selected sort entry for header width, row text, comparison, collapse, sort, and optional initialization. Comparators read `hist_entry`, `branch_info`, `mem_info`, `map_symbol`, cgroup, callchain, timestamp, and data-type state. Tracepoint dynamic entries use libtraceevent fields when available.

## State and Persistence Behavior

Most state is process-local global state: taken flags in dimension tables, `perf_hpp_list` flags (`parent`, `sym`, `dso`, `need_collapse`), compiled regexes, user sort strings, and elision state. Per-entry derived strings such as `he->srcline`, `he->srcfile`, and `he->trace_output` are lazily cached on `hist_entry` objects. Data-type sorting may set `symbol_conf.annotate_data_member`. The code intentionally leaks a synthesized `sort_order` string for the lifetime of the process because other code continues to reference it.

## Dependencies and Integration Points

This file integrates with nearly every perf report data model: hists, hpp formatting, symbols, DSOs, maps, threads, branch stacks, memory data-source decoding, cgroups, trace events, callchains, annotation/data-type analysis, perf session environment, and UI error reporting. It also depends on optional libtraceevent support for trace output and dynamic trace fields.

## Risks and Edge Cases

Sort-key prefix matching uses `strncasecmp(tok, name, strlen(tok))`, so ambiguous prefixes can select the first matching dimension. Several arithmetic comparators subtract unsigned addresses or counters and cast to `int64_t`, which is conventional here but sensitive to wraparound. `sort__dcacheline_cmp()` depends on cacheline-size detection and special-cases anonymous/shared mappings and double-cacheline mode. Trace field formatting must handle binaries built without libtraceevent. Source-line and data-type sort keys allocate/cache strings and must respect ownership. Eliding every sort column is detected and undone to avoid empty output.

## Test Signals

Useful tests include `perf report --sort` and `--fields` smoke tests across normal, branch, memory, diff, top, and tracepoint modes; invalid and ambiguous key diagnostics; architecture-specific latency header behavior for x86/powerpc/nonmatching envs; `dcacheline` behavior with known cacheline size; trace field sorting with and without libtraceevent; elision with single-item symbol/DSO/comm filters; and source/data-type sorting with debug information present and absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sort.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/sort.h

## Purpose

`sort.h` declares the sort subsystem contract used by perf report, top, diff, memory, branch, and tracepoint views. It exposes sort modes, stable sort-key identifiers, configurable global state, the `struct sort_entry` callback interface, and setup/helper functions implemented in `sort.c`.

## Important APIs, Types, and Functions

`enum sort_mode` distinguishes normal, branch, memory, top, diff, and tracepoint contexts. `enum sort_type` enumerates common keys, branch-stack keys, and memory-specific keys; the ordering matches the implementation arrays in `sort.c`. `struct sort_entry` carries the column header plus callback pointers for comparison, collapse comparison, display sorting, row formatting, filtering, and per-hist-entry initialization. Exported sort entries include common symbols such as `sort_comm`, `sort_dso`, `sort_sym`, `sort_parent`, branch entries, `sort_srcline`, and `sort_type`.

The header declares `setup_sorting()`, `setup_output_field()`, `reset_output_field()`, `sort__setup_elide()`, `perf_hpp__set_elide()`, `sort_help()`, `report_parse_ignore_callees_opt()`, `is_strict_order()`, `hpp_dimension__add_output()`, `reset_dimensions()`, `sort_dimension__add()`, `output_field_add()`, address comparators, `_sort__sym_cmp()`, `hist_entry__srcline()`, and `sort__comm_nodigit_len()`.

## Control Flow and Data Flow

Consumers set globals such as `sort_order`, `field_order`, `sort__mode`, `parent_pattern`, and `chk_double_cl`, then call `setup_sorting()` to materialize callback-backed hpp fields. Later report rendering uses the registered callbacks rather than calling most functions directly.

## State and Persistence Behavior

The header exposes mutable process-global configuration. There is no on-disk persistence; state lasts for the perf command lifetime and is reset by `reset_output_field()` and `reset_dimensions()`.

## Dependencies and Integration Points

It depends on `hist.h`, regex support, and `struct perf_env`/`struct evlist` forward declarations. The API is consumed by report, top, diff, mem, trace, annotation, and hists code that needs a stable shared sorting contract.

## Risks and Edge Cases

Adding new `enum sort_type` values requires keeping implementation arrays and hpp column indexes coherent. Exposed globals can be mutated by option parsing before setup, so initialization order matters. Callback return semantics are signed 64-bit comparisons; implementers must avoid incompatible comparator directions.

## Test Signals

Compile-time coverage should catch missing declarations. Runtime signals are successful parsing of every documented sort key, correct help-string generation, and reset/setup idempotence across multiple report modes in one process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/sort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/spark.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/spark.c

## Purpose

`spark.c` renders a compact Unicode sparkline for a vector of unsigned long values. It is a small presentation helper for perf output that wants trend visualization without graphics.

## Important APIs, Types, and Functions

The only exported function is `print_spark(char *bf, int size, unsigned long *val, int numval)`. It uses the eight glyphs defined by `NUM_SPARKS` in `spark.h` and `SPARK_SHIFT` fixed-point scaling.

## Control Flow and Data Flow

The function scans all values to find `min` and `max`, computes a fixed-point step `f = ((max - min) << SPARK_SHIFT) / (NUM_SPARKS - 1)`, clamps `f` to at least one, then appends one tick glyph per value using `scnprintf()`. The glyph index is `((val[i] - min) << SPARK_SHIFT) / f`.

## State and Persistence Behavior

There is no persistent or global state other than the static tick table. Output is written into the caller-provided buffer and the function returns the number of bytes printed.

## Dependencies and Integration Points

It depends on Linux `scnprintf()` and `<limits.h>`. Callers must provide an adequately sized buffer and accept UTF-8 glyph output.

## Risks and Edge Cases

The implementation assumes `numval > 0`; an empty vector leaves `min` and `max` at sentinel values and can underflow. Very small buffers rely on `scnprintf()` truncation behavior. Since each glyph is multi-byte UTF-8, byte count and display column count differ.

## Test Signals

Tests should cover constant arrays, increasing/decreasing arrays, mixed ranges, small output buffers, and Unicode rendering in terminal output. A defensive caller test should avoid invoking it with zero values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/spark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/spark.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/spark.h

## Purpose

`spark.h` exposes the small sparkline-rendering interface used by perf text output.

## Important APIs, Types, and Functions

It defines `NUM_SPARKS` as 8 and declares `print_spark(char *bf, int size, unsigned long *val, int numval)`.

## Control Flow and Data Flow

The header has no control flow. Callers include it to size logic around the eight-level spark scale and to call the renderer implemented in `spark.c`.

## State and Persistence Behavior

No state is declared. The macro fixes the number of visual buckets at compile time.

## Dependencies and Integration Points

It is self-contained and integrates with text display code that wants compact trend output.

## Risks and Edge Cases

Changing `NUM_SPARKS` requires updating the tick table in `spark.c`. Callers should treat the rendered output as UTF-8 bytes, not one byte per visual cell.

## Test Signals

Build coverage and simple sparkline snapshots are sufficient for the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/spark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/srccode.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/srccode.c

## Purpose

`srccode.c` caches source files and returns raw source-line slices for annotation or source-code display. It avoids repeatedly opening and scanning the same files by mmaping source content and indexing line starts.

## Important APIs, Types, and Functions

The private `struct srcfile` stores hash/list nodes, filename, line pointer array, mmap pointer, line count, and map length. Public functions are `find_sourceline()` and `srccode_state_free()`. Helpers include `countlines()`, `fill_lines()`, `free_srcfile()`, and `find_srcfile()`.

## Control Flow and Data Flow

`find_sourceline(fn, line, lenp)` calls `find_srcfile()`. The cache lookup hashes by filename and moves hits to the front of `srcfile_list`. On a miss, the cache prunes least-recently-used entries while file count or mapped bytes exceed `MAXSRCFILES` or `MAXSRCCACHE`, opens and stats the file, mmap maps a page-rounded size, counts lines, allocates a line-start array, fills it, links the entry into both hash and LRU lists, and returns the selected line start plus byte length up to newline.

## State and Persistence Behavior

State is process-local: a 64-bucket filename hash, an LRU list, total mapped size, and source-file count. Mappings persist until pruned or process exit. `find_sourceline()` returns a non-NUL-terminated pointer into an mmap owned by the cache, so callers must copy or print with the returned length. `srccode_state_free()` releases the last `srcfile` string in a caller-owned state object.

## Dependencies and Integration Points

The file depends on Linux lists, hlist hashing, `mmap`, `open`, `fstat`, page size from internal lib support, perf debug logging, and `str_hash()`. It integrates with source annotation paths that need fast repeated line lookup.

## Risks and Edge Cases

If `open()` succeeds but `fstat()` fails, the current code returns without closing the descriptor. Empty files and out-of-range line numbers return `NULL`. `find_sourceline()` computes `p - l` after `memchr()`; the line indexer should ensure a newline or map-end path is valid, but malformed edge cases deserve attention. Returned pointers become invalid after cache pruning. The code is not thread-synchronized.

## Test Signals

Tests should cover empty files, files without a trailing newline, repeated lookup moving entries to the LRU front, cache pruning by count and size, missing files, long lines, and callers honoring the non-NUL-terminated result length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/srccode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/srccode.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/srccode.h

## Purpose

`srccode.h` declares the lightweight state and lookup API for retrieving source-code line slices.

## Important APIs, Types, and Functions

`struct srccode_state` holds a `srcfile` string and current line number. `srccode_state_init()` clears those fields. `srccode_state_free()` releases the state-owned filename. `find_sourceline()` returns a pointer and length for a given source filename and one-based line number.

## Control Flow and Data Flow

Consumers initialize state, resolve or update source file/line state elsewhere, and call `find_sourceline()` when they need the text. The result is a raw slice, not a C string.

## State and Persistence Behavior

The state struct owns `srcfile` when populated. The source-line data returned by `find_sourceline()` is owned by the cache in `srccode.c` and may be invalidated by cache eviction.

## Dependencies and Integration Points

The header is self-contained and is used by source annotation/display code.

## Risks and Edge Cases

Callers must not `free()` the returned line pointer or assume NUL termination. Line numbers are one-based in the API. Failing to call `srccode_state_free()` leaks `srcfile`.

## Test Signals

Compile coverage, initialization/free idempotence, and source-line display tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/srccode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/srcline.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/srcline.c

## Purpose

`srcline.c` resolves instruction addresses to source file/line strings and inline-frame lists. It provides fallback formatting when debug source lookup fails and stores resolved source lines and inline chains in DSO-owned rbtree caches.

## Important APIs, Types, and Functions

Public data includes `srcline_full_filename` and `srcline__unknown`. Public functions include `get_srcline()`, `__get_srcline()`, `get_srcline_split()`, `zfree_srcline()`, `srcline__tree_insert/find/delete()`, `dso__parse_addr_inlines()`, `inline_node__delete()`, `inlines__tree_insert/find/delete()`, `inline_list__append()`, `inline_list__append_tail()`, `srcline_from_fileline()`, `new_inline_sym()`, and `addr2line_configure()`.

## Control Flow and Data Flow

Resolution starts by selecting a DSO filename with `srcline_dso_name()`, skipping synthetic bracketed or perf pid-map DSOs. `addr2line()` initializes default resolver order on first use and then tries configured providers: libdw, LLVM, libbfd, and external `addr2line`. `__get_srcline()` converts successful file/line results to strings, resets DSO failure counts, or returns symbol/address fallbacks while incrementing failures. After `A2L_FAIL_LIMIT`, source-line lookup is disabled for that DSO and addr2line resources are freed.

Inline parsing creates an `inline_node`, asks addr2line providers to unwind inlines, and stores `inline_list` entries in caller-order-dependent order. Rbtree helpers cache source strings and inline nodes by address.

## State and Persistence Behavior

`symbol_conf.addr2line_style` is lazily initialized and can be configured by `addr2line_configure()`. DSOs retain failure counts, a `has_srcline` flag, and cached resolver state. Source-line and inline trees take ownership of inserted strings/nodes. `SRCLINE_UNKNOWN` is a static sentinel and must not be freed; `zfree_srcline()` handles that distinction.

## Dependencies and Integration Points

The file integrates with debug-info backends (`libdw`, LLVM, libbfd, external command), DSO/symbol abstractions, callchain ordering, perf basename policy, rbtree caches, and annotation/report source-line display.

## Risks and Edge Cases

Source lookup can be disabled after repeated failures, so transient backend failures may suppress later success for a DSO. Inline fake symbols are owned only when `symbol->inlined` is set; double-free avoidance depends on that flag. Resolver configuration silently warns on unknown styles but continues. `srcline_from_fileline()` changes output based on `srcline_full_filename`, which can affect sorting/grouping. Callers must respect sentinel ownership.

## Test Signals

Tests should cover successful DWARF lookup, fallback to symbol/address/unknown strings, configured resolver order, failure-limit disabling, inline list order for caller/callee callchain modes, rbtree insert/find/delete, demangled inline symbols, and basename versus full filename output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/srcline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/srcline.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/srcline.h

## Purpose

`srcline.h` declares the address-to-source-line and inline-frame cache API used by perf symbol, report, and callchain code.

## Important APIs, Types, and Functions

It exposes `srcline_full_filename`, `srcline__unknown`, `SRCLINE_UNKNOWN`, `MAX_INLINE_NEST`, `struct inline_list`, and `struct inline_node`. The API includes `get_srcline()`, `__get_srcline()`, `get_srcline_split()`, `zfree_srcline()`, source-line tree functions, inline tree functions, `dso__parse_addr_inlines()`, `inline_node__delete()`, `inline_list__append()`, `inline_list__append_tail()`, `srcline_from_fileline()`, `new_inline_sym()`, and `addr2line_configure()`.

## Control Flow and Data Flow

Callers resolve an address to a display string or split filename/line, optionally parse inline frames, and cache results in DSO rbtree structures. Tree insert calls transfer ownership to the DSO-side cache.

## State and Persistence Behavior

The header documents ownership: source-line tree insertion and inline tree insertion take ownership. `SRCLINE_UNKNOWN` is a shared sentinel. Inline lists contain symbol pointers and source-line strings with deletion handled by `inline_node__delete()`.

## Dependencies and Integration Points

It depends on Linux list/rbtree/types headers and forward declarations for `dso` and `symbol`. It is a shared contract between address resolution backends, DSO caches, callchain display, and sort keys.

## Risks and Edge Cases

Ownership is the main risk: callers must use `zfree_srcline()` and not normal `free()` for possible sentinel values. Inline fake symbols must be handled through the delete helpers. Address keys must use the same address space convention for insert and lookup.

## Test Signals

Build coverage plus source-line cache and inline-cache lifetime tests should validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/srcline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stat-display.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stat-display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stat-shadow.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/stat-shadow.c

## Purpose

`stat-shadow.c` evaluates derived `perf stat` metrics from raw counter aggregates. It prepares expression contexts, handles tool time events and PMU-specific aliases, classifies metric thresholds, and emits metrics through output callbacks supplied by `stat-display.c`.

## Important APIs, Types, and Functions

Public functions are `perf_stat__print_shadow_stats()`, `perf_stat__print_shadow_stats_metricgroup()`, `perf_stat__skip_metric_event()`, and `test_generic_metric()`. Private core functions are `tool_pmu__is_time_event()`, `prepare_metric()`, `generic_metric()`, and `perf_stat__print_metricgroup_header()`.

## Control Flow and Data Flow

`perf_stat__print_shadow_stats()` optionally lets iostat print metrics, then calls the metricgroup iterator. `perf_stat__print_shadow_stats_metricgroup()` finds metric expressions associated with an evsel, optionally chunks default metricgroups so each group can be printed separately, and calls `generic_metric()` for each expression. `generic_metric()` creates an expression parse context, populates it through `prepare_metric()`, parses the metric expression and threshold expression, applies unit scaling with `perf_pmu__convert_scale()`, formats unit/name text, and calls the selected `print_metric` callback.

`prepare_metric()` maps each metric event to the correct aggregate value. It handles time tool events as CPU0/first aggregate and converts nanoseconds to seconds, substitutes matching PMU aliases for uncore/hybrid metric leaders, uses `NAN` for unsupported or not-running events, and adds source-count metadata for expression functions.

## State and Persistence Behavior

Most state is per call. `perf_stat__print_metricgroup_header()` keeps static `last_name` and `last_pmu` to avoid repeating adjacent default metricgroup headers. Metric values are not stored; they are derived from `evsel->stats->aggr` at print time.

## Dependencies and Integration Points

It depends on metricgroup lookup, expression parsing, PMU unit scaling, tool PMU event classification, iostat metrics, cgroup headers through output callbacks, and aggregation data generated by `stat.c`. It is tightly coupled to `stat-display.c` through `struct perf_stat_output_ctx`.

## Risks and Edge Cases

Unsupported events are intentionally `NAN`, while not-counted events with zero runtime also produce `NAN`; expression behavior must tolerate that. Tool time events rely on CPU0 existing in the aggregation map or fall back to index zero. Static metricgroup header suppression may be surprising across independent print sequences. PMU alias remapping assumes matching `metric_leader` relationships. Threshold classification currently treats zero threshold expression result as good and nonzero as bad.

## Test Signals

Tests should cover simple ratios, missing events, disabled counters, time-event conversion, nested metric references, PMU alias substitution, unit scaling, threshold classification, default metricgroup pagination, metric-only headers, and `test_generic_metric()` for expression-unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stat-shadow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stat.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stat.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strbuf.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/strbuf.c

## Purpose

`strbuf.c` implements a growable, NUL-terminated byte/string buffer for perf utilities. It is modeled on Git-style strbuf behavior and supports appending bytes, chars, formatted text, and file-descriptor contents.

## Important APIs, Types, and Functions

Public functions are `strbuf_init()`, `strbuf_release()`, `strbuf_detach()`, `strbuf_grow()`, `strbuf_addch()`, `strbuf_add()`, `strbuf_addf()`, and `strbuf_read()`. The file defines the global `strbuf_slopbuf[1]` used by empty buffers.

## Control Flow and Data Flow

Initialization points empty buffers at `strbuf_slopbuf`. `strbuf_grow()` computes required allocation as `len + extra + 1`, detects overflow, uses `alloc_nr()` growth when larger, and avoids reallocating the static slop buffer. Add functions grow first, copy/write data, and update length through `strbuf_setlen()`. Formatted appends try `vsnprintf()` once, grow to the reported size if needed, then retry with a saved `va_list`. `strbuf_read()` grows by a hint or 8192 bytes, reads until EOF, grows between chunks, and rolls back to the old length or releases if the first read fails.

## State and Persistence Behavior

All state is caller-owned in `struct strbuf`. `strbuf_detach()` transfers the allocated buffer to the caller and reinitializes the shell. `strbuf_release()` frees only allocated buffers and returns the object to empty state.

## Dependencies and Integration Points

It depends on `cache.h` for `alloc_nr()`, Linux string/kernel helpers, zalloc, debug logging, stdio, errno, and `read()`. It is used wherever perf builds dynamic strings, including sort help generation.

## Risks and Edge Cases

`strbuf_setlen()` asserts `len < alloc`; callers that manually grow then set length must respect available capacity. `strbuf_grow()` returns `-E2BIG` on overflow. A broken `vsnprintf()` can be detected and reported as `-EINVAL`. Partial read failure rolls back previous content, which is useful but may surprise callers expecting partial data.

## Test Signals

Tests should cover empty initialization, growth from slop, formatted append requiring retry, detach ownership, release idempotence, binary data append, overflow guards, and `strbuf_read()` success and rollback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strbuf.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/strbuf.h

## Purpose

`strbuf.h` defines the growable buffer API and invariants used by perf utility code.

## Important APIs, Types, and Functions

It declares `strbuf_slopbuf`, `struct strbuf { alloc, len, buf }`, `STRBUF_INIT`, lifecycle functions, `strbuf_avail()`, `strbuf_grow()`, `strbuf_setlen()`, append helpers, formatted append, and `strbuf_read()`.

## Control Flow and Data Flow

Callers initialize or statically create a buffer, grow or append into it, optionally manipulate the available tail directly, then set the length. The buffer is always NUL-terminated, even when used for byte data.

## State and Persistence Behavior

The object owns its allocated buffer unless the caller detaches it. An empty object points at `strbuf_slopbuf`. `strbuf_setlen()` forces allocation when called on an unallocated buffer.

## Dependencies and Integration Points

The header depends on assert, stdarg, stddef, string, Linux compiler attributes, and sys/types. It is a generic helper used by sort/help and other string-building code.

## Risks and Edge Cases

The comments say `buf` is malloced, but the implementation uses a static slop buffer for empty state; callers must follow the API and not free `buf` directly. Direct tail writes require a later valid `strbuf_setlen()`.

## Test Signals

Compile coverage and API-level buffer append/grow/detach tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stream.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/stream.c

## Purpose

`stream.c` compares hot callchain streams between evsels, typically for perf diff-style analysis. It selects the top N hottest callchain nodes per event, matches callchains across two evsels, and prints matched and unmatched hot streams.

## Important APIs, Types, and Functions

Public functions are `evlist__create_streams()`, `evlist_streams__delete()`, `evsel_streams__entry()`, `evsel_streams__match()`, and `evsel_streams__report()`. Private helpers allocate per-evsel stream arrays, select hot callchain nodes, initialize from hists, match callchains, link pairs, and print reports.

## Control Flow and Data Flow

Creation allocates an `evlist_streams` sized to the evlist and a fixed-size `stream` array for each evsel. It resorts hists output, walks each hist entry's sorted callchain tree, and keeps the highest-hit callchain nodes using a simple replacement of the current smallest hit. Matching iterates base streams, finds the first pair stream whose callchain node matches via `callchain_cnode_matched()`, and stores reciprocal `pair_cnode` pointers. Reporting prints matched pairs, old-only streams, and new-only streams with hit percentages and average cycles.

## State and Persistence Behavior

Stream structures borrow callchain node pointers from hists; they do not own callchain data. Pairing state is stored in `pair_cnode` fields until the stream object is deleted. Output goes directly to stdout.

## Dependencies and Integration Points

It depends on hists, sort resorting, evlist/evsel iteration, callchain node/list helpers, debug support, and zalloc. It integrates with analysis that compares old and new perf data callchains.

## Risks and Edge Cases

The hot-stream selection is O(N * max_streams) and intentionally simple for small N. Equal hit counts do not replace existing streams. Borrowed callchain pointers require the underlying hists to outlive the stream object. Reporting assumes pair callchains have compatible list traversal. `printf()` to stdout bypasses configurable perf output streams.

## Test Signals

Tests should cover creation/deletion, top-N replacement, no callchains, matching and unmatched streams, hit percentage calculation, average cycle display, multiple evsels, and lifetime ordering with hists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stream.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/stream.h

## Purpose

`stream.h` declares the hot-callchain stream comparison data structures and API.

## Important APIs, Types, and Functions

`struct stream` stores a selected callchain node and its matched pair node. `struct evsel_streams` stores one evsel's stream array, capacity, count, total hits, and evsel pointer. `struct evlist_streams` stores all evsel stream sets. The API creates, deletes, finds, matches, and reports streams.

## Control Flow and Data Flow

Consumers create streams from an evlist, fetch entries for particular evsels, match two `evsel_streams`, report results, and delete the container.

## State and Persistence Behavior

The structures own only their arrays, not callchain nodes. Pair state is mutable and process-local.

## Dependencies and Integration Points

The header forward-declares callchain, evlist, and evsel types and is implemented by `stream.c`.

## Risks and Edge Cases

Callchain owners must outlive stream structures. Callers should not reuse pair state across unrelated comparisons without rebuilding or clearing it.

## Test Signals

Build coverage plus stream comparison tests against synthetic hists validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strfilter.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/strfilter.c

## Purpose

`strfilter.c` parses and evaluates glob-based boolean string filters. It supports rule expressions containing glob leaves, grouping parentheses, logical AND, OR, and NOT.

## Important APIs, Types, and Functions

Public functions are `strfilter__new()`, `strfilter__or()`, `strfilter__and()`, `strfilter__compare()`, `strfilter__delete()`, and `strfilter__string()`. Private functions tokenize (`get_token()`), allocate/delete AST nodes, parse expressions recursively, append new root operators, evaluate nodes, and reconstruct a string.

## Control Flow and Data Flow

`strfilter__new()` allocates a filter and parses rules into an AST. The parser reads tokens, builds operator nodes by adjusting the current/root right branch, recursively handles parentheses, and stores glob strings in leaf nodes. AND binds more tightly than OR through the parser's root/last-op manipulation. `strfilter__compare()` recursively evaluates the AST and calls `strglobmatch()` for leaves. Append functions parse a second rule and wrap the existing root and new subtree under an OR or AND node.

## State and Persistence Behavior

The filter owns its AST and duplicated glob strings. Operator node `p` pointers reference static operator strings and are not freed; leaf `p` strings are freed. Reconstructed rule strings are newly allocated and caller-owned.

## Dependencies and Integration Points

It depends on `string2.h` glob matching, Linux ctype/string helpers, zalloc, and errno. It can be used by perf filtering options that need simple boolean glob matching.

## Risks and Edge Cases

Parsing reports syntax errors by returning an error pointer into the input, or NULL for allocation failure. Escaped separators and `!` inside glob character classes receive special token handling. Recursion depth is unbounded by this code. `strfilter__string()` does not explicitly write the final NUL after reconstruction, relying on malloc contents would be unsafe if not otherwise terminated by copied leaf strings; callers should test this path carefully.

## Test Signals

Tests should cover precedence (`a|b&c`), parentheses, NOT, escaped operators, `!` in glob classes, syntax-error pointers, append OR/AND, AST deletion, string reconstruction, and glob match behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strfilter.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/strfilter.h

## Purpose

`strfilter.h` defines the AST structures and public API for glob-based boolean string filters.

## Important APIs, Types, and Functions

`struct strfilter_node` stores left/right children and an operator or rule string. `struct strfilter` stores the root. Declared functions create, append OR/AND rules, compare strings, delete filters, and reconstruct rule strings.

## Control Flow and Data Flow

Callers parse a rule string into a filter, evaluate candidate strings with `strfilter__compare()`, optionally append more rules, and delete the filter.

## State and Persistence Behavior

The filter owns its parsed tree. Error reporting from creation/append returns a pointer into the input rule or NULL on allocation failure.

## Dependencies and Integration Points

The header depends on Linux list inclusion and bool support. It is implemented by `strfilter.c` and uses glob behavior from `string.c`.

## Risks and Edge Cases

Callers must handle NULL filters and distinguish syntax from allocation failures through the error pointer. The AST is mutable when appending rules.

## Test Signals

Parser/evaluator unit tests with valid and invalid expressions are the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strfilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/string.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/string.c

## Purpose

`string.c` provides generic string helpers for perf: size parsing, glob and lazy matching, tail comparison, trace-filter expression generation, escaped/quoted token scanning and duplication, hex decoding, and character replacement.

## Important APIs, Types, and Functions

Public data includes `graph_dotted_line` and `dots`. Public functions include `perf_atoll()`, `strglobmatch()`, `strglobmatch_nocase()`, `strlazymatch()`, `strtailcmp()`, `asprintf_expr_inout_ints()` plus wrappers in the header, `asprintf__tp_filter_pids()` declared in the header but not present in this file, `strpbrk_esc()`, `strpbrk_esq()`, `strdup_esc()`, `strdup_esq()`, `hex()`, and `strreplace_chars()`.

## Control Flow and Data Flow

`perf_atoll()` parses decimal sizes with optional byte/K/M/G/T suffixes. Glob matching is recursive with support for `*`, `?`, character classes, ranges, complement, escapes, optional case-insensitivity, and optional whitespace ignoring for lazy matching. Escaped scanning walks to stop characters while skipping single-backslash escapes; quoted scanning extends that to quoted substrings. Duplication helpers remove escape characters and, for quoted strings, remove surrounding quotes while preserving quoted content semantics. `strreplace_chars()` counts target characters, allocates a larger string if needed, and copies replacement chunks.

## State and Persistence Behavior

There is no mutable global state beyond static string constants. Functions returning strings allocate caller-owned memory.

## Dependencies and Integration Points

It depends on Linux kernel/string/ctype helpers and standard allocation. It is used by filter parsing, event expression construction, command parsing, and display helpers.

## Risks and Edge Cases

`perf_atoll()` shifts signed values and can overflow silently for very large inputs. `hex()` assumes alphabetic input is a hex letter and does not reject characters above `F`/`f`. Recursive glob matching can be expensive for pathological patterns with many wildcards. Escape scanning has subtle behavior around double backslashes. `strreplace_chars()` copies one extra byte before replacement and should be covered by tests for adjacent and leading needles.

## Test Signals

Tests should cover suffix parsing and invalid suffixes, glob classes/ranges/escapes/case modes, lazy whitespace matching, tail comparison, in/not-in expression generation, escaped and quoted separators, malformed quotes, hex conversion, and replacement at beginning/middle/end/no match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/string2.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/string2.h

## Purpose

`string2.h` declares perf's miscellaneous string helper API.

## Important APIs, Types, and Functions

It exposes `graph_dotted_line`, `dots`, `perf_atoll()`, glob matching functions, `strisglob()`, `strtailcmp()`, integer-expression formatting helpers, tracepoint PID filter formatting, escaped/quoted scanning and duplication, `hex()`, and `strreplace_chars()`.

## Control Flow and Data Flow

The header's inline helpers route `asprintf_expr_in_ints()` and `asprintf_expr_not_in_ints()` to `asprintf_expr_inout_ints()` with the inclusion flag. `strisglob()` uses `strpbrk()` to detect glob metacharacters.

## State and Persistence Behavior

No state is declared beyond external constant string pointers. Functions returning `char *` generally allocate caller-owned memory.

## Dependencies and Integration Points

It depends on Linux string/types, sys/types for `pid_t`, stddef, and string. It is shared by filters, parsers, tracepoint tooling, and display code.

## Risks and Edge Cases

The header declares `asprintf__tp_filter_pids()` even though it is not implemented in the nearby `string.c`; link coverage must ensure another object supplies it or unused declarations remain harmless. Callers must free allocated return strings and handle NULL.

## Test Signals

Compile/link coverage plus unit tests for each declared helper validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/string2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strlist.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/strlist.c

## Purpose

`strlist.c` implements an ordered unique string set on top of perf's `rblist`. It can parse comma-separated lists, load entries from files, and optionally treat list entries as filenames relative to a directory.

## Important APIs, Types, and Functions

Public functions are `strlist__new()`, `strlist__delete()`, `strlist__add()`, `strlist__load()`, `strlist__remove()`, `strlist__find()`, and `strlist__entry()`. Private callbacks implement node allocation, deletion, and string comparison. Parsing helpers include `strlist__parse_list_entry()` and `strlist__parse_list()`.

## Control Flow and Data Flow

`strlist__new()` initializes an `rblist`, installs callbacks, sets `file_only`, and parses the optional comma-separated list. Each entry may be substituted with `dirname/entry`; if accessible, it is loaded as a file of newline-separated entries. If not accessible and `file_only` is set, parsing fails with `-ENOENT`; otherwise the entry string is inserted. `strlist__load()` reads each line, strips the final newline byte, and inserts it into the tree. Lookup and indexed access delegate to `rblist`.

## State and Persistence Behavior

The strlist owns duplicated node strings and rbtree nodes. It stores entries sorted by `strcmp()` and does not preserve input order. `strlist__delete()` deletes rblist contents but does not free the `struct strlist` wrapper in this implementation, so caller conventions must be checked. Removed nodes are deleted through rblist callbacks.

## Dependencies and Integration Points

It depends on `rblist`, Linux zalloc, stdio, errno, string, stdlib, and `access()`. It is used by filter lists such as symbols, DSOs, comms, and sort elision logic.

## Risks and Edge Cases

`strlist__load()` strips `entry[len - 1]` even if the last line has no newline, removing the final character. `strlist__parse_list()` returns early on error without freeing the duplicated list string, causing a leak. `strlist__new()` frees only the wrapper on parse error and may rely on rblist cleanup elsewhere. Sorted uniqueness means duplicate inputs collapse and input order is lost.

## Test Signals

Tests should cover duplicate insertion, sorted lookup, indexed access, removal, list parsing, file loading with and without trailing newline, `file_only` behavior, dirname substitution, and parse-error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strlist.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/strlist.h

## Purpose

`strlist.h` declares the ordered string-list API backed by `rblist`.

## Important APIs, Types, and Functions

`struct str_node` stores an rbtree node and string pointer. `struct strlist` wraps `struct rblist` plus a `file_only` flag. `struct strlist_config` controls dirname substitution and filename-only behavior. The header declares create/delete/add/load/remove/find/index functions and inline helpers for membership, emptiness, count, first/next, and iteration macros.

## Control Flow and Data Flow

Consumers create a list from an optional comma-separated string, add or load entries, query by string or index, iterate in sorted order, remove entries, and delete the list.

## State and Persistence Behavior

The list owns inserted nodes and strings. Iteration is over rbtree order, not insertion order. `file_only` affects parsing at creation time.

## Dependencies and Integration Points

It depends on Linux rbtree, bool support, and `rblist.h`. It is used by perf option filters and elision helpers.

## Risks and Edge Cases

The safe-iteration macro computes `strlist__next(pos)` even when `pos` is NULL for empty lists, but the inline handles NULL. Callers must respect that returned `str_node->s` is owned by the list.

## Test Signals

Compile coverage and strlist parser/iteration/removal tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/strlist.h -->
