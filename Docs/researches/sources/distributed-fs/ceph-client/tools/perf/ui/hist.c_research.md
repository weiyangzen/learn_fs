# sources/distributed-fs/ceph-client/tools/perf/ui/hist.c

## Purpose

`ui/hist.c` defines perf's backend-neutral histogram column formatting framework. It converts `hist_entry` statistics into `perf_hpp` columns, manages output/sort field lists, formats percentages/latency/raw/average/memory-stat values, and prepares hierarchy-specific hpp formats.

## Important APIs, Types, and Functions

Core APIs include `hpp__fmt`, `hpp__fmt_acc`, `hpp__fmt_mem_stat`, `hpp_color_scnprintf`, `perf_hpp__init`, column/sort registration helpers, `perf_hpp__cancel_cumulate`, `perf_hpp__cancel_latency`, `perf_hpp__setup_output_field`, `perf_hpp__append_sort_keys`, `perf_hpp__reset_output_field`, `hists__sort_list_width`, `hists__overhead_width`, `hists__reset_column_width`, `perf_hpp__set_user_width`, `perf_hpp__setup_hists_formats`, and `perf_hpp__alloc_mem_stats`. Global data includes `perf_hpp__format[]` and `perf_hpp_list`.

## Control Flow and State

Formatter macros generate entry/color/sort callbacks for built-in columns. Formatting handles event groups by collecting peer hist entries and emitting per-member values. Registration mutates linked lists in `perf_hpp_list` and per-hists hierarchy nodes. Width calculations derive from active formats, skip-empty policy, and user widths. Memory-stat columns allocate per-hists total arrays and print only populated subcolumns.

## Dependencies and Integration Points

This file depends on hist/callchain/sort/evsel/evlist/mem-events/string utilities and global `symbol_conf`. TUI, GTK, and stdio renderers all consume these format definitions.

## Risks and Test Signals

Risks include list ownership errors when unregistering duplicated formats, group-event sorting mismatches, division by zero in memory stats, and strict field-order interactions. Test signals include all output fields, grouped events with skipped empty members, cumulative callchain on/off, latency columns, memory-stat reports, hierarchy mode, user column widths, and repeated setup/reset cycles.
