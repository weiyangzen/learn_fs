# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/hists.c

## Purpose

`gtk/hists.c` renders perf histograms and callchains in GTK tree views. It is the GTK backend equivalent of stdio/TUI histogram display for `perf report --gtk`.

## Important APIs, Types, and Functions

`perf_gtk__init_hpp` installs GTK markup-aware percent color callbacks. Callchain population is split across flat, folded, and graph modes: `perf_gtk__add_callchain_flat`, `perf_gtk__add_callchain_folded`, `perf_gtk__add_callchain_graph`, and `perf_gtk__add_callchain`. Histogram rendering is done by `perf_gtk__show_hists`, hierarchy rendering by `perf_gtk__add_hierarchy_entries` and `perf_gtk__show_hierarchy`. The public entry point is `evlist__gtk_browse_hists`.

## Control Flow and State

The browser creates GTK tree stores, appends event/hist rows, inserts columns from `perf_hpp` formats, expands callchain nodes according to global `callchain_param`, and opens one notebook tab per event or event group. Row activation triggers annotation via `hist_entry__gtk_annotate`. State is GTK model/view state plus shared `perf_hpp__format` callback mutation.

## Dependencies and Integration Points

It depends on GTK, perf hists, evlist/evsel, callchain, sort, hpp formatting, helpline, and the GTK context from `gtk.h`. It is selected through dynamic GTK browser setup.

## Risks and Test Signals

Risks include MAX_COLUMNS truncation, incorrect group-event columns, hierarchy indentation mismatches, folded-callchain allocation failures, and annotation callbacks with stale hist entries. Tests should cover single and multi-event sessions, grouped events, hierarchy mode, all callchain modes, row activation, empty hists, and percent color markup.
