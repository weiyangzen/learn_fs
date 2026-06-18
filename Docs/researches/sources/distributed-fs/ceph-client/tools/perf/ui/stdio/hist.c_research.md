# sources/distributed-fs/ceph-client/tools/perf/ui/stdio/hist.c

## Purpose

`stdio/hist.c` prints perf histograms, hierarchy reports, block reports, callchains, and event statistics to `FILE *` streams. It is the non-interactive renderer used by stdio and report dumping paths.

## Important APIs, Types, and Functions

Public APIs are `__hist_entry__snprintf`, `hists__fprintf_headers`, `hists__fprintf`, and `events_stats__fprintf`. Internal callchain printers support graph absolute/relative, flat, and folded modes. Entry printers cover normal, hierarchy, block, and individual-block reports.

## Control Flow and State

`hists__fprintf` resets widths, optionally prints headers, allocates a line buffer, walks the cached RB tree with forced hierarchy traversal, filters by percent and `h->filtered`, emits entries, optional callchains, “no entry” hierarchy rows, and verbose maps for unresolved entries. A temporary `[...]` symbol is allocated for remaining filtered graph hits and freed at the end.

## Dependencies and Integration Points

It depends on perf hists, hpp formatting from `ui/hist.c`, callchain state, maps/symbols/thread data, block-info, and global `symbol_conf`. TUI dump-to-file also reuses similar formatting concepts.

## Risks and Test Signals

Risks include graph depth mask overflow, folded separator correctness, max row/column truncation, and hierarchy indentation when `field_sep` is set. Tests should compare stdio output for all callchain modes, hierarchy mode, block modes, min-percent filtering, max rows/cols, skip-empty, verbose unresolved maps, and event stats.
