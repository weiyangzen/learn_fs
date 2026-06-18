# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/annotate.c

## Purpose

`gtk/annotate.c` provides GTK annotation windows for perf symbols. It disassembles a selected symbol, calculates per-line percentages, and presents source/disassembly rows in a tabbed GTK notebook.

## Important APIs, Types, and Functions

Public functions are `hist_entry__gtk_annotate` and `perf_gtk__show_annotations`. Internal helpers format percentage markup (`perf_gtk__get_percent`), object offsets (`perf_gtk__get_offset`), escaped line text (`perf_gtk__get_line`), populate a `GtkListStore` (`perf_gtk__annotate_symbol`), and prepare annotation data (`symbol__gtk_annotate`).

## Control Flow and State

`hist_entry__gtk_annotate` annotates `he->ms`. `symbol__gtk_annotate` rejects DSOs already warned, calls `symbol__annotate`, marks failures, calculates percentages, and either reuses the active GTK context or creates a new top-level window, notebook, info bar, and status bar. `perf_gtk__annotate_symbol` fills rows, then frees the temporary disassembly list. `perf_gtk__show_annotations` runs `gtk_main` and deactivates `pgctx`.

## Dependencies and Integration Points

It depends on GTK, perf annotation/disasm APIs, evsel group iteration, maps/DSOs/symbols, and GTK context utilities from `gtk.h`. It is the GTK counterpart to TUI annotation.

## Risks and Test Signals

Risks include stale `notes->src` ownership, division by zero when sample counts are absent, markup escaping, and multi-event percentage layout. Tests should annotate symbols with source, disassembly only, grouped events, no samples, and disassembly failures, then verify tabs render and context cleanup happens.
