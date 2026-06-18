# sources/distributed-fs/ceph-client/tools/perf/util/callchain.h

Purpose: declares the callchain data model, help text, option enums, global parameters, cursor types, and public APIs used by perf record/report/top and histogram code.

Important APIs/types: defines `enum perf_call_graph_mode`, `enum chain_mode`, `enum chain_order`, `enum chain_key`, `enum chain_value`, `struct callchain_node`, `struct callchain_root`, `struct callchain_param`, `struct callchain_list`, `struct callchain_cursor_node`, and `struct callchain_cursor`. Declares append/merge/cursor, sample resolution, formatting, branch count, TLS cursor, deferred merge, and iteration helpers.

Control flow: callers initialize a root, append frames to a cursor, commit the cursor to switch from write to read mode, then call append/merge APIs. Inline helpers expose sequential reading and cumulative hit/count helpers.

State and persistence: exposes global `callchain_param`, `callchain_param_default`, and `dwarf_callchain_users`. Roots own rb-tree/list nodes; cursors cache allocated nodes across samples.

Dependencies and integration: includes Linux list/rbtree, `map_symbol.h`, and `branch.h`, and forward-declares perf sample, evsel, hists, thread, map, and record types. It is the contract between callchain implementation, symbol resolution, histograms, UI/reporting, and branch display.

Risks: many structs are directly mutable, so initialized lists, cursor `last` pointers, refcounted `map_symbol` copies, and rb-tree ordering must be preserved by all users. TUI state is embedded in aggregation nodes.

Test signals: compile all users and run append, commit, advance, reset, merge, free, and print tests across chain modes and keys.
