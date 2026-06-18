<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol_conf.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/symbol_conf.h

## Purpose

`symbol_conf.h` defines the global configuration object controlling perf symbol loading, filtering, display, annotation, demangling, addr2line behavior, callchain behavior, guest symbol paths, symfs layout, and parallelism filters.

## Important APIs, Types, and Functions

The main type is `struct symbol_conf`, with many booleans for behavior flags such as `try_vmlinux_path`, `ignore_vmlinux`, `use_modules`, `demangle`, `demangle_kernel`, `hide_unresolved`, `lazy_load_kernel_maps`, `keep_exited_threads`, `annotate_data_member`, `enable_latency`, and `prefer_latency`. It stores path strings for vmlinux, kallsyms, guest files, source prefix, graph function, addr2line path, and symfs. It stores filter input strings and parsed `strlist`/`intlist` objects for DSOs, comms, pids, tids, symbols, address filters, column widths, and backtrace stops. It defines `enum a2l_style` and an array of preferred addr2line styles. It also declares the global `symbol_conf`.

## Control Flow and Data Flow

Command-line and config parsing populate raw strings and flags in `symbol_conf`. `symbol__init()` later converts those strings into parsed lists, initializes symbol-private allocation size, computes kernel pointer restriction state, configures vmlinux paths, and validates parallelism filters. Symbol loading, reporting, annotation, and demangling code read the resulting fields to decide which DSOs/symbols to load, display, annotate, or suppress.

## State and Persistence Behavior

`symbol_conf` is process-global mutable state. It persists across all DSO loads and reports in a perf process until `symbol__exit()` frees parsed lists and clears initialization state. Some fields own allocated strings, while others point to command-line storage or static defaults depending on the setup path. `symfs` changes also redirect build-id cache lookup through `symbol__config_symfs()`.

## Dependencies and Integration Points

The header depends on `stdbool.h`, Linux bitmap support, `perf.h`, and forward declarations for `strlist` and `intlist`. It integrates with `symbol.c`, annotate/report code, addr2line implementations, callchain rendering, latency reporting, and any option parser that writes symbol configuration.

## Risks and Edge Cases

Because this is global state, initialization order matters. `symbol__annotation_init()` must run before `symbol__init()` if callers need annotation private storage. Ownership of string fields is not uniform, so cleanup must only free fields that the owning functions allocate. The parallelism bitmap has `MAX_NR_CPUS + 1` bits and represents filtered-out levels by clearing requested bits, which can be easy to misread. Changing defaults can alter many perf commands.

## Test Signals

Tests should verify default values, conversion of DSO/comm/pid/tid/symbol filters, address extraction from symbol filters, symfs flat versus hierarchy behavior, invalid field separator rejection, invalid parallelism levels, addr2line style parsing by users of the enum, and cleanup/reinitialization without leaks or stale parsed lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/symbol_conf.h -->
