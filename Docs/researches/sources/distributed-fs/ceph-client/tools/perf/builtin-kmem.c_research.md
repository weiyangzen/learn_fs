<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kmem.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-kmem.c

## Purpose
Implements `perf kmem`, including `perf kmem record` and `perf kmem stat`. It records or analyzes kernel memory allocation tracepoints for slab allocations and page allocator activity, producing per-allocation, per-callsite, live-page, GFP flag, migration-type, fragmentation, ping-pong, and summary statistics.

## Important APIs, Types, and Functions
The entry point is `cmd_kmem()`. Recording is implemented by `__cmd_record()`, which builds a `perf record` argv for slab and/or page tracepoints. Analysis is implemented by `__cmd_kmem()`, with sample dispatch in `process_sample_event()`. Slab state uses `struct alloc_stat` and rb-trees `root_alloc_stat`, `root_caller_stat`, and sorted variants; handlers are `evsel__process_alloc_event()` and `evsel__process_free_event()`. Page state uses `struct page_stat`, live/alloc/caller rb-trees, sort-input lists, `order_stats`, and handlers `evsel__process_page_alloc_event()` and `evsel__process_page_free_event()`.

Callsite discovery for page allocations uses `build_alloc_func_list()` to collect kernel allocation functions by regex from the kernel map and `find_callsite()` to walk callchains until the first non-allocation function. GFP formatting uses `struct gfp_flag`, `parse_gfp_flags()`, `compact_gfp_flags()`, `compact_gfp_string()`, and the static compact-name table. Output and sorting are handled by `sort_result()`, `__sort_slab_result()`, `__sort_page_result()`, `__print_slab_result()`, `__print_page_alloc_result()`, `__print_page_caller_result()`, `print_gfp_flags()`, `print_slab_summary()`, `print_page_summary()`, and many `*_cmp()` sort-dimension callbacks.

## Control Flow
`cmd_kmem()` loads `kmem.default` config, parses subcommands and options, defaults to slab or page analysis when neither was requested, and dispatches `record` by synthesizing a `perf record -a -R -c 1` command with the relevant tracepoints. Slab record includes legacy `_node` tracepoints only when exposed. Page record adds `-g` so stat mode can resolve callsites from callchains.

For `stat`, the command opens the input perf.data session with ordered events, verifies required tracepoints exist, gets page size from traceevent metadata for page mode, enables callchains for page mode, initializes symbols, parses time filters, sets locale and CPU-to-node mapping, installs default sort keys and page grouping keys, then calls `__cmd_kmem()`. `__cmd_kmem()` verifies trace data, registers tracepoint handlers by name, detects `pfn` versus `page` field naming, processes events, sorts accumulated rb-trees, and prints selected reports plus summaries.

Slab allocation events aggregate by allocation pointer and callsite, update total requested/allocated bytes and NUMA cross-allocation counts. Slab free events find the pointer, add freed bytes, and record cross-CPU ping-pong if freed on a different CPU. Page allocation events parse page/PFN, order, GFP flags, migration type, allocation bytes, and callsite, then update live, allocation, caller, and order/migration trees. Page free events match the live page, account unmatched frees, update free bytes, and in live mode remove or decrement live allocation records.

## State and Persistence Behavior
Analysis state is entirely in static globals for the invocation: mode flags, line limits, sort lists, rb-trees, counters, GFP cache, callsite function list, page size, time filter, and `kmem_session`. Input perf.data is read-only. `record` writes perf.data through `cmd_record()` using synthesized tracepoint options. `stat` writes text to stdout/pager. The command mutates rb-tree membership when sorting by moving nodes from raw trees to sorted trees, so printing is terminal for the accumulated state.

## Dependencies and Integration Points
Depends on perf session/tool/evsel tracepoint handler infrastructure, traceevent/libtraceevent field decoding, kernel symbol maps, callchain resolution, CPU-to-NUMA mapping, rbtree/list utilities, parse-options subcommands, perf time filtering, locale-aware printing, and `cmd_record()` from the perf record command. It integrates with kernel tracepoints `kmem:kmalloc`, `kmem:kfree`, `kmem:kmem_cache_alloc`, `kmem:kmem_cache_free`, optional legacy node allocation tracepoints, `kmem:mm_page_alloc`, and `kmem:mm_page_free`.

## Risks and Edge Cases
This snapshot contains duplicated source fragments (`kmem_cache_alloc` handler entry, duplicated `while (true)`, duplicated `else`) that are compile-time or maintenance risk signals. Page migration type indexes are used directly against a fixed six-entry string/table and `order_stats[MAX_PAGE_ORDER][MAX_MIGRATE_TYPES]`, so unexpected kernel values can index out of bounds. GFP compaction can return NULL for unknown flags, yet printing uses the returned string with `%s`. `process_sample_event()` returns early on time-skip without `thread__put(thread)`, which is a leak risk in this source. `parse_filter_event()`-style ownership is not present here, but many sort dimensions are duplicated with `memdup()` and not freed before process exit.

Accounting is tracepoint-format sensitive: field names changed from `page` to `pfn`, slab node fields are optional, legacy tracepoints may or may not exist, and page callsite attribution requires callchains and successfully loaded kernel symbols. Live page mode changes semantics by decrementing/removing records on free rather than aggregating total alloc/free. Unmatched frees and allocation failures are tracked but can skew summary interpretation.

## Test Signals
Test `perf kmem record --slab`, `--page`, both modes, and legacy-tracepoint detection. For `stat`, test slab-only, page-only, combined, `--caller`, `--alloc`, custom `--sort`, `--line`, `--raw-ip`, `--live`, and `--time`. Validate NUMA cross allocation counts, ping-pong counts, fragmentation math, page/PFN field detection, GFP compact legend generation, migration/order summary, unmatched free and allocation failure counts, symbolized and raw callsites, default `kmem.default` config, and graceful error messages when required tracepoints are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-kmem.c -->
