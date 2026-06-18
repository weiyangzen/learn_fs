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
