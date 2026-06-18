# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/hists.c

## Purpose

`hists.c` is the SLang/TUI histogram browser used by `perf report`, `perf top`, and block-hist views. It presents `struct hists` data as navigable rows, renders callchains and hierarchy mode, manages hotkeys, and bridges from histogram entries to annotation, map browsing, perf script, data-file switching, thread/DSO/socket zoom filters, and event selection.

## Important APIs, Types, and Functions

The file implements `hist_browser__init`, `hist_browser__new`, `hist_browser__delete`, `hist_browser__run`, `evlist__tui_browse_hists`, and `block_hists_tui_browse`. Internal state is `struct hist_browser` from `hists.h`, plus `struct popup_action` and `struct evsel_menu`. Important helper families handle folding (`hist_entry__set_folding`, `hist_browser__toggle_fold`), row counts (`callchain__count_rows`, `hierarchy_count_rows`), rendering (`hist_browser__show_entry`, `hist_browser__show_hierarchy_entry`, header functions), navigation (`ui_browser__hists_seek`), and actions (`do_annotate`, `do_run_script`, zoom helpers).

## Control Flow and State

The main loop enters through `evlist__tui_browse_hists`; single-event sessions go straight to `evsel__hists_browse`, while multi-event sessions first show an `evsel_menu`. Each histogram browser initializes SLang input, builds row counts, pushes a helpline, then repeatedly calls `hist_browser__run`. Hotkeys update local browser state, global `symbol_conf`, `input_name`, perf-top counters, or hist filters, then reset visible rows when needed. Expanded callchains persist in `hist_entry` folding fields and `nr_rows`; temporary zoom state is stored in hists filters and a `pstack`.

## Dependencies and Integration Points

This file depends on perf hist/callchain/sort/thread/map/evlist internals, SLang browser primitives, annotation TUI code, script browsing, resource-sample browsing, and `perf_env` objdump lookup. It is the point where backend-neutral histogram formatting from `ui/hist.c` becomes interactive terminal UI. It also calls `tui__header_window`, `map__browse`, `hist_entry__annotate_data_tui`, and `evlist__toggle_enable`.

## Risks and Test Signals

Risks are off-by-one row accounting when combining filters, callchain folding, hierarchy entries, and terminal resizing; stale selection pointers after resort/filter changes; leaks or stale `input_name` during data-file switching; and command construction for scripts. Test signals include browsing single and grouped events, TAB/UNTAB switching, percent-limit changes, all callchain modes, `perf top` timer refresh/lost-event warnings, annotation from normal and branch views, script menus, map browsing, and block-hist annotation.
