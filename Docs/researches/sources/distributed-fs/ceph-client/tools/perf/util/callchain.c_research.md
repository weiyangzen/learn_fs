# sources/distributed-fs/ceph-client/tools/perf/util/callchain.c

Purpose: implements perf call graph option parsing, sample callchain resolution, insertion/merge into a compressed callchain tree, sorting for report/top output, branch-count annotation, and lifecycle helpers for callchain roots and cursors.

Important APIs/functions: `parse_callchain_record_opt`, `parse_callchain_report_opt`, `parse_callchain_top_opt`, `record_opts__parse_callchain`, `perf_callchain_config`, `callchain_register_param`, `callchain_append`, `callchain_merge`, `callchain_cursor_append`, `sample__resolve_callchain`, `hist_entry__append_callchain`, `free_callchain`, `decay_callchain`, `get_tls_callchain_cursor`, `callchain_param_setup`, `sample__for_each_callchain_node`, and `sample__merge_deferred_callchain`.

Control flow: option parsing sets global `callchain_param` and symbol flags, then registers a sorter. Samples resolve into a TLS `callchain_cursor`, commit for reading, and append into `callchain_root.node`. Insertion walks child rb-trees, compares by srcline/function/address, splits partially matched nodes, and updates hit/count totals. Report flow sorts the hierarchy using absolute or relative thresholds. Merge flow replays source nodes into a destination root.

State and persistence: global state includes `callchain_param`, `callchain_param_default`, `dwarf_callchain_users`, and a pthread key for per-thread cursors. Runtime state persists in `callchain_root` trees and `callchain_list` entries holding `map_symbol` references, srcline strings, branch stats, and hit counters.

Dependencies and integration: depends on perf symbols, maps, DSOs, machines, threads, hist entries, branch metadata, record options, `symbol_conf`, libpthread TLS, Linux rbtrees/lists, and architecture constants. Integrates with record option parsing, config parsing, sample resolution, histograms, report formatting, and branch-stack display.

Risks: prefix token parsing can become ambiguous. Tree split/merge ownership for `map_symbol` and branch stats is complex. Sorting thresholds depend on current cumulative hit math. TLS allocation failure is soft in some paths. Deferred callchain merge replaces a sample pointer, so callers must honor ownership flags.

Test signals: exercise `perf record --call-graph fp,dwarf,lbr`, report/top graph modes, config keys, branch callstack display, srcline/function/address sorting, aarch64 FP fallback, deferred callchains, and memory checks around split/merge/free.
