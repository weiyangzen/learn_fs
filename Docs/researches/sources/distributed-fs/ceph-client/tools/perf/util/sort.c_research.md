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
