# subset-b-006754 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/hists.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/hists.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/hists.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/hists.h

## Purpose

`hists.h` declares the TUI histogram browser object and its small public lifecycle API. It lets other perf UI code allocate, initialize, run, and destroy a browser over a `struct hists` tree.

## Important APIs, Types, and Functions

`struct hist_browser` embeds `struct ui_browser` and stores the active `struct hists`, selected `hist_entry`, selected `map_symbol`, timer, filter stack, perf environment, optional block event, print sequence, display flags, percent limit, row counters, c2c filtering flag, and title callback. Public functions are `hist_browser__new`, `hist_browser__delete`, `hist_browser__run`, and `hist_browser__init`.

## Control Flow and State

The header does not execute code, but it defines the mutable state contract used by `browsers/hists.c`. Ownership is mixed: the browser owns its allocated wrapper but references hists, evsel/env/timer data owned by report/top paths. Row counters are derived state and must be recomputed after filters or folding change.

## Dependencies and Integration Points

It includes `ui/browser.h` and forward-declares `struct evsel`; other referenced types come from included browser/hist headers. Consumers are primarily `browsers/hists.c` and code that launches block histogram browsers.

## Risks and Test Signals

Risks are ABI drift between this struct and its implementation, especially selection and row-count fields. Compile coverage catches declaration mismatches; runtime coverage should exercise selection, filtering, and block browser paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/hists.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/map.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/map.c

## Purpose

`map.c` implements a TUI symbol-map browser for a perf `struct map`. It displays each symbol's start/end address, binding, and name, and optionally supports name/address search when verbose indexing is enabled.

## Important APIs, Types, and Functions

The public API is `map__browse(struct map *map)`. Internal `struct map_browser` embeds `ui_browser`, stores the viewed `map`, and tracks address display width. `map_browser__write` renders rows from DSO symbols, `map_browser__search` resolves input by hex address or symbol name, `map_browser__run` handles keys, and `symbol__browser_index` accesses the extra index slot expected near symbol storage.

## Control Flow and State

`map__browse` walks `dso__symbols(map__dso(map))`, counts entries, finds maximum end address, and in verbose mode stores each symbol's row index. `map_browser__run` shows the map and loops until ESC/left/q/Ctrl-C. Search updates browser top/index when a symbol is found; otherwise it pushes a helpline message. No persistent state is written outside optional per-symbol index memory.

## Dependencies and Integration Points

This depends on perf map/DSO/symbol helpers, SLang browser primitives, keysyms, and helpline handling. It is reached from the histogram context menu's “Browse map details” action.

## Risks and Test Signals

The `symbol__browser_index` pointer arithmetic is explicitly fragile and depends on symbol allocation layout. Search is only useful when indexes were prefilled under verbose mode. Tests should browse maps with local/global/weak symbols, verify address-width formatting, search by `0x...` and name, and ensure empty or missing symbol trees fail gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/map.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/map.h

## Purpose

`map.h` exposes the TUI map browser entry point.

## Important APIs, Types, and Functions

It forward-declares `struct map` and declares `int map__browse(struct map *map)`.

## Control Flow and State

There is no runtime behavior here. The header defines the integration contract for callers that want to inspect a map's symbols interactively.

## Dependencies and Integration Points

It is included by the histogram browser and implemented by `map.c`.

## Risks and Test Signals

The risk surface is limited to declaration drift. Build coverage of `browsers/hists.c` and `map.c` validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/res_sample.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/res_sample.c

## Purpose

`res_sample.c` presents a menu of representative samples for a histogram entry and opens contextual `perf script` output around the selected sample. It supports normal, disassembly, and source-code context modes.

## Important APIs, Types, and Functions

`res_sample_init` reads the `samples.context` config value into the static `context_len`, defaulting to 10 ms. `res_sample_browse` builds display labels from `struct res_sample` timestamps, CPU, and TID, then constructs a `perf script` command with `--time`, optional `--cpu`, optional `--tid`, event-specific formatting from `attr_to_script`, optional `--inline`, lost/switch/task events, `--ns`, and a `less` search positioned at the sample timestamp.

## Control Flow and State

The function allocates menu strings, uses `ui__popup_menu`, frees the menu, and returns if the choice is invalid. For a valid sample it computes a time range around `r->time` using `context_len`, formats the exact sample timestamp, builds the command with `asprintf`, and delegates terminal handling to `run_script`. Persistent state is only the process-global configured `context_len`.

## Dependencies and Integration Points

It depends on browser script helpers, `perf_exe`, event attributes, time formatting, `symbol_conf`, and global `input_name`. It is invoked by the TUI histogram context menu for entries with representative samples.

## Risks and Test Signals

Command-string construction must preserve quoting assumptions and tolerate missing CPU/TID/input name. Time underflow around early samples and large configured context windows are edge cases. Tests should cover all `enum rstype` modes, inline on/off, CPU/TID filters, and entries with zero, one, or many representative samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/res_sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/scripts.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/scripts.c

## Purpose

`scripts.c` implements the TUI script picker used from histogram browsing. It offers built-in `perf script` views, user-configured report scripts, custom command arguments, and discovered scripts from perf's script directories.

## Important APIs, Types, and Functions

`attr_to_script` augments script fields based on sample type, including trace, raw, addr, and data source. `scripts_config` handles `scripts.*` config entries. `check_ev_match` filters scripts against event requirements embedded in script comments. `find_scripts` scans language subdirectories under `perf exec-path/scripts`, skipping `top.*` scripts. `list_scripts` builds the popup menu. Public functions are `run_script` and `script_browse`.

## Control Flow and State

`script_browse` asks `list_scripts` for a command, then wraps it with event filters, optional `-i input_name`, stderr redirection, and `less`. `run_script` leaves SLang raw mode, executes the shell command, resets the terminal with escape sequences, reinitializes SLang, and refreshes the screen. Configured script entries allocate name/path strings and are freed after menu use.

## Dependencies and Integration Points

This file depends on perf config, sessions, evlist/hists, symbol metadata, script directories under perf's exec path, SLang, and global `input_name`. It is called from `browsers/hists.c` and `res_sample.c`.

## Risks and Test Signals

Shell command construction and user-configured scripts are the main risk. Directory entries with unknown `d_type`, event-name matching, missing scripts, and terminal restore after failures need coverage. Test signals include built-in sample modes, custom command entry, configured scripts, discovered scripts with and without event match comments, and returning cleanly to the TUI after `system()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/browsers/scripts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/annotate.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/annotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/browser.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/browser.c

## Purpose

`gtk/browser.c` contains shared GTK browser helpers: signal handling, default window sizing, percentage color markup, and standard info/status widgets.

## Important APIs, Types, and Functions

It exports `perf_gtk__signal`, `perf_gtk__resize_window`, `perf_gtk__get_percent_color`, `perf_gtk__setup_info_bar` when supported, and `perf_gtk__setup_statusbar`. The color policy maps high percentages to red, medium percentages to dark green, and low percentages to unmarked text.

## Control Flow and State

Signal handling calls `perf_gtk__exit(false)` then reports the signal. Resizing chooses three quarters of the monitor containing the GTK window. Widget setup stores pointers and statusbar context IDs in global `pgctx`. Info bars hide on OK response.

## Dependencies and Integration Points

It depends on GTK/GDK APIs, perf GTK context state, and `MIN_RED`/`MIN_GREEN` histogram color thresholds. It is used by GTK hists and annotation code.

## Risks and Test Signals

Risks include old GTK API assumptions (`window->window`), absent info-bar support, and `pgctx` null misuse. Test signals are GTK startup/shutdown, window sizing on multi-monitor setups, warning display via info/status bars, and percentage markup in hist and annotate views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/browser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/gtk.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/gtk.h

## Purpose

`gtk.h` is the shared GTK UI interface for perf. It declares the GTK context, initialization/exit hooks, helper widgets, histogram browser entry point, and annotation entry points.

## Important APIs, Types, and Functions

`struct perf_gtk_context` stores main window, notebook, optional info bar/message label, status bar, and statusbar context ID. Declarations include `perf_gtk__init`, `perf_gtk__exit`, `perf_gtk__activate_context`, `perf_gtk__deactivate_context`, `perf_gtk__init_helpline`, `gtk_ui_progress__init`, `perf_gtk__init_hpp`, `evlist__gtk_browse_hists`, and `hist_entry__gtk_annotate`.

## Control Flow and State

The header has no runtime flow, but it defines `pgctx` as the global active GTK UI context and provides an inline active-context check. A stub `perf_gtk__setup_info_bar` returns `NULL` when info-bar support is not compiled in.

## Dependencies and Integration Points

It includes GTK while suppressing strict-prototype diagnostics, and forward-declares perf event/hist/timer types. It is included by all GTK backend files and dynamically loaded by `ui/setup.c` when GTK browser mode is selected.

## Risks and Test Signals

The main risks are build-configuration drift around GTK and info-bar support, and global context lifetime mistakes. Build tests with and without GTK info bar support plus runtime annotation/hist browsing validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/gtk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/helpline.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/helpline.c

## Purpose

`gtk/helpline.c` adapts perf's generic helpline interface to GTK statusbar output.

## Important APIs, Types, and Functions

It defines `gtk_helpline_pop`, `gtk_helpline_push`, `gtk_helpline_show`, a `struct ui_helpline gtk_helpline_fns`, and the public initializer `perf_gtk__init_helpline`.

## Control Flow and State

Push/pop no-op when `pgctx` is inactive; otherwise they use the GTK statusbar and stored context ID. `gtk_helpline_show` accumulates formatted text into `ui_helpline__current` until a newline is seen, then displays only the first line and resets the static backlog.

## Dependencies and Integration Points

It depends on `gtk.h`, generic `ui/helpline.h`, and `ui_helpline__current`. `perf_gtk__init` installs these operations so generic `ui__warning` and helpline calls show in GTK.

## Risks and Test Signals

Risks are backlog overflow/truncation and lost multiline messages. Tests should push, pop, and show warnings before and after GTK context activation, including multiline messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/helpline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/hists.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/hists.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/progress.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/progress.c

## Purpose

`gtk/progress.c` implements `ui_progress_ops` for GTK using a modal-ish progress dialog and progress bar.

## Important APIs, Types, and Functions

It defines static GTK widgets `dialog` and `progress`, `gtk_ui_progress__update`, `gtk_ui_progress__finish`, a `gtk_ui_progress__ops` vtable, and public `gtk_ui_progress__init`.

## Control Flow and State

The first update lazily creates a window and progress bar titled from `ui_progress->title`. Updates compute `curr / total`, format a percentage string, set the fraction/text, show widgets, and drain pending GTK events. Finish destroys the dialog and clears globals.

## Dependencies and Integration Points

It depends on GTK and generic `ui/progress.h`. `perf_gtk__init` installs it so long-running perf operations can report progress in GTK mode.

## Risks and Test Signals

Risks include division by zero if callers violate progress initialization, reentrancy while pumping GTK events, and stale widget globals after destroy. Tests should initialize/update/finish multiple progress objects and verify clean behavior for small, large, and completed totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/progress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/setup.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/setup.c

## Purpose

`gtk/setup.c` initializes and exits the GTK backend.

## Important APIs, Types, and Functions

It exports `perf_gtk__init` and `perf_gtk__exit`.

## Control Flow and State

Initialization calls `gtk_init_check`; on success it registers GTK error ops, installs GTK helpline/progress/hpp callbacks, and returns 0. Exit unregisters GTK error ops. The `wait_for_ok` argument is unused.

## Dependencies and Integration Points

It depends on GTK, generic UI error registration, GTK helpline/progress/hist helpers, and is loaded by `ui/setup.c` through `dlsym`.

## Risks and Test Signals

Risks are partial initialization when GTK is unavailable and mismatched error-op registration. Tests should run with DISPLAY available and unavailable, then verify fallback behavior and unregister on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/util.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/util.c

## Purpose

`gtk/util.c` owns GTK context allocation and GTK-specific error/warning presentation.

## Important APIs, Types, and Functions

It defines global `struct perf_gtk_context *pgctx`, `perf_gtk__activate_context`, `perf_gtk__deactivate_context`, static error/warning functions, and exported `perf_gtk_eops`.

## Control Flow and State

Activation allocates a context, stores the main window, and returns it. Deactivation frees and nulls the context pointer. Errors use a modal message dialog. Warnings prefer an info bar if compiled and active, otherwise the statusbar, otherwise they fall back to stderr-like behavior.

## Dependencies and Integration Points

It depends on `ui/util.h` error ops, GTK widgets, and optional info-bar fields from `gtk.h`. `gtk/setup.c` registers `perf_gtk_eops`.

## Risks and Test Signals

Risks include registering multiple UI error providers, stale `pgctx` after window close, and warnings before widget setup. Test with active/inactive context, info-bar and no-info-bar builds, repeated activation/deactivation, and warning/error display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/gtk/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/helpline.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/helpline.c

## Purpose

`ui/helpline.c` provides the backend-neutral helpline dispatch layer. It supplies no-op defaults and forwards calls to TUI or GTK implementations once installed.

## Important APIs, Types, and Functions

It defines `ui_helpline__current`, default `ui_helpline` operations, global `helpline_fns`, and wrappers `ui_helpline__pop`, `ui_helpline__push`, `ui_helpline__vpush`, `ui_helpline__fpush`, `ui_helpline__puts`, `ui_helpline__vshow`, and `ui_helpline__printf`.

## Control Flow and State

Calls dispatch through the current vtable. Formatted push allocates a temporary string with `vasprintf`, falls back to `vfprintf` on allocation failure, then frees. `ui_helpline__puts` replaces the current message by popping then pushing.

## Dependencies and Integration Points

Backends update `helpline_fns` in `tui/helpline.c` or `gtk/helpline.c`. Histogram browsers, warnings, and dialogs use this generic API.

## Risks and Test Signals

Risks are backend vtable lifetime and allocation-failure paths. Tests should call all wrappers before UI init, after TUI init, after GTK init, and under formatted long messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/helpline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/helpline.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/helpline.h

## Purpose

`helpline.h` declares the generic perf helpline interface and shared buffers.

## Important APIs, Types, and Functions

`struct ui_helpline` contains `pop`, `push`, and `show` callbacks. The header declares `helpline_fns`, `ui_helpline__init`, all helpline wrapper functions, `ui_helpline__current[512]`, and `ui_helpline__last_msg[]`.

## Control Flow and State

There is no executable flow. The header defines the state that TUI and GTK backends mutate and generic callers consume.

## Dependencies and Integration Points

It is included by generic, TUI, GTK, and browser code.

## Risks and Test Signals

Risks are buffer-size assumptions and missing definitions when a backend is omitted. Build tests across UI configurations and runtime helpline smoke tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/helpline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/hist.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/hist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/keysyms.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/keysyms.c

## Purpose

`keysyms.c` converts key codes into human-readable names for UI warnings and help.

## Important APIs, Types, and Functions

It implements `const char *key_name(int key, char *bf, size_t size)`. Printable keys are returned as one-character strings; control keys and SLang key constants are mapped to names such as ENTER, ESC, BACKSPACE, UP, DOWN, F1, TAB, and TIMER; unknown keys are formatted numerically.

## Control Flow and State

The function is stateless and writes into caller-provided storage for non-static names.

## Dependencies and Integration Points

It depends on `keysyms.h`, Linux ctype/kernel helpers, and SLang constants through `libslang.h`. Browser code uses it for unhandled-hotkey messages.

## Risks and Test Signals

Risks are missing key mappings and buffer truncation. Tests should cover printable, control, navigation, function, timer, resize, and unknown keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/keysyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/keysyms.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/keysyms.h

## Purpose

`keysyms.h` centralizes perf UI key constants.

## Important APIs, Types, and Functions

It includes `libslang.h`, defines control-key macro usage and perf-specific pseudo keys such as timer, error, resize, tab/untab, switch-input-data, and reload, and declares `key_name`.

## Control Flow and State

There is no runtime flow. It defines the shared numeric vocabulary used by SLang input and browser hotkey handling.

## Dependencies and Integration Points

TUI setup, browser utilities, map/hist browsers, and warning code include it.

## Risks and Test Signals

Risks are collisions between pseudo keys and SLang key values. Build and runtime hotkey tests across all browser paths validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/keysyms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/libslang.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/libslang.h

## Purpose

`libslang.h` wraps inclusion of SLang headers for perf UI code and handles feature-test macro compatibility.

## Important APIs, Types, and Functions

It includes `<features.h>`, conditionally preserves/restores `_XOPEN_SOURCE`, and includes `<slang.h>`.

## Control Flow and State

No runtime behavior exists. Its state effect is preprocessor-level: it prevents SLang headers from breaking other libc feature declarations.

## Dependencies and Integration Points

Every TUI file that uses SLang primitives includes this wrapper instead of including `<slang.h>` directly.

## Risks and Test Signals

Risks are platform libc macro differences and SLang header compatibility. Build tests with supported libc/SLang versions are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/libslang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/progress.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/progress.c

## Purpose

`ui/progress.c` provides a generic progress object and backend dispatch for long-running perf operations.

## Important APIs, Types, and Functions

It defines a null progress backend, global `ui_progress__ops`, `ui_progress__update`, `__ui_progress__init`, and `ui_progress__finish`.

## Control Flow and State

Initialization sets title, total, current count, and display size, then calls backend `init` if available. Updates advance `curr` and only call the backend when `curr >= next` or the operation is complete; this throttles UI redraws. Finish calls backend `finish` if present. The active backend is process-global.

## Dependencies and Integration Points

TUI and GTK progress files replace `ui_progress__ops`. Callers use the generic `ui_progress__init` macro from `progress.h`.

## Risks and Test Signals

Risks include total zero handling, overflow in `curr + adv`, and backend replacement order. Tests should check no-op behavior, throttling, final update, and backend-specific progress rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/progress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/progress.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/progress.h

## Purpose

`progress.h` declares the generic perf UI progress API.

## Important APIs, Types, and Functions

`struct ui_progress` stores title, total, current value, size, next update threshold, and step. `struct ui_progress_ops` carries optional `init`, `update`, and `finish` callbacks. It declares `ui_progress__finish`, `__ui_progress__init`, `ui_progress__update`, and the `ui_progress__init` convenience macro.

## Control Flow and State

The header does not execute code but defines the mutable state that generic and backend progress code share.

## Dependencies and Integration Points

It is used by generic progress, TUI progress, GTK progress, and perf operations that report long-running work.

## Risks and Test Signals

Risks are callers passing transient title storage or inconsistent totals. Compile coverage plus runtime progress tests in TUI/GTK modes validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/progress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/setup.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/setup.c

## Purpose

`ui/setup.c` chooses and initializes perf's output UI mode: stdio/pager, TUI/SLang, or GTK. It also exposes global browser state and SIGWINCH masking helpers.

## Important APIs, Types, and Functions

Globals are `ui__lock`, `perf_gtk_handle`, and `use_browser`. Public APIs are `stdio__config_color`, `setup_browser`, `exit_browser`, `pthread__block_sigwinch`, and `pthread__unblock_sigwinch`. GTK support is loaded dynamically by `setup_gtk_browser` and `exit_gtk_browser` through `dlopen`/`dlsym`.

## Control Flow and State

`setup_browser` normalizes `use_browser`: `-2` tries GTK, `-1` tries TUI, fallback may open the pager, and successful TUI initialization sets browser mode and initializes histogram formatting. `exit_browser` dispatches to GTK or TUI cleanup. SIGWINCH helpers block/unblock resize signals around threaded work.

## Dependencies and Integration Points

It depends on pager support, color config, generic hist hpp init, optional GTK dynamic symbols, TUI `ui__init/ui__exit`, and perf's global UI selection.

## Risks and Test Signals

Risks are fallback surprises, dynamic-load failures, stale GTK handles, and signal-mask side effects. Tests should cover `--stdio`, `--tui`, `--gtk`, no-terminal fallback, pager fallback, repeated setup/exit, and SIGWINCH behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/stdio/hist.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/stdio/hist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/helpline.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/tui/helpline.c

## Purpose

`tui/helpline.c` implements the generic helpline interface for SLang terminal UI.

## Important APIs, Types, and Functions

It defines `ui_helpline__last_msg`, `tui_helpline__set`, TUI pop/push/show callbacks, exported `tui_helpline_fns`, and `ui_helpline__init`.

## Control Flow and State

Push writes the message on the last terminal row, refreshes SLang, and stores the current text. Show accumulates formatted output in `ui_helpline__last_msg` under `ui__lock` until a newline, then replaces the displayed helpline and resets backlog. Init installs the vtable and displays a blank message.

## Dependencies and Integration Points

It depends on SLang, generic helpline state, `ui__lock`, and terminal dimensions. TUI setup calls it during initialization.

## Risks and Test Signals

Risks are backlog indexing on empty strings, terminal resize interactions, and concurrent warnings. Tests should show short, long, multiline, and concurrent messages while resizing the terminal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/helpline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/progress.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/tui/progress.c

## Purpose

`tui/progress.c` implements terminal progress bars for the SLang UI backend.

## Important APIs, Types, and Functions

It defines `__tui_progress__init`, `get_title`, `tui_progress__update`, `tui_progress__finish`, a `ui_progress_ops` instance, and public `tui_progress__init`.

## Control Flow and State

Initialization sets the update step based on terminal width. Update returns when browser mode is inactive or total is zero, formats optional unit-scaled title, refreshes dimensions, draws a centered three-row box and filled bar under `ui__lock`, then refreshes SLang. Finish clears the same region.

## Dependencies and Integration Points

It depends on generic progress, SLang, terminal dimensions, unit formatting, `ui__lock`, and global `use_browser`.

## Risks and Test Signals

Risks include narrow terminal division, resize during progress, and drawing over active browser content. Tests should exercise zero total, small total, large total, resize, and finish cleanup in TUI and non-browser modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/progress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/setup.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/tui/setup.c

## Purpose

`tui/setup.c` initializes, runs input for, and exits the SLang terminal UI backend.

## Important APIs, Types, and Functions

Public APIs are `ui__refresh_dimensions`, `ui__getch`, `ui__init`, and `ui__exit`. Internal handlers cover SIGWINCH, fatal signals/backtraces, and SIGTSTP/SIGCONT terminal suspension. It also references `perf_tui_eops`, `tui_helpline__set`, and `hist_browser__init_hpp`.

## Control Flow and State

`ui__init` initializes SLang terminal/screen/keypad, colors, helpline, error ops, progress, browser internals, and signal handlers. `ui__getch` uses `select` for optional timer delays, distinguishes bare ESC from escape sequences, and maps timeouts to `K_TIMER`. `ui__exit` restores terminal state, unregisters error ops, optionally waits for confirmation, and handles suspended terminal restoration.

## Dependencies and Integration Points

It depends on SLang, color setup, browser initialization, generic UI utilities, signal handling, and progress/helpline backends. It is selected by `ui/setup.c`.

## Risks and Test Signals

Risks include terminal corruption after signals/scripts, ESC timing, resize races, and signal-handler safety. Tests should start/exit TUI, press navigation/function keys, trigger timer mode, resize, suspend/resume, and force error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/tui.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/tui/tui.h

## Purpose

`tui.h` declares TUI-specific initialization hooks not exposed through the generic UI headers.

## Important APIs, Types, and Functions

It declares `void tui_progress__init(void);`.

## Control Flow and State

There is no runtime flow. The declaration lets TUI setup install the terminal progress backend.

## Dependencies and Integration Points

It is included by `tui/setup.c` and implemented by `tui/progress.c`.

## Risks and Test Signals

Risk is declaration drift. Build coverage of the TUI backend validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/tui.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/util.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/tui/util.c

## Purpose

`tui/util.c` implements common terminal dialogs: popup menus, input windows, info/help/question windows, yes/no prompts, and TUI error/warning callbacks.

## Important APIs, Types, and Functions

Public APIs include `ui__popup_menu`, `ui_browser__input_window`, `__ui__info_window`, `ui__info_window`, `ui__question_window`, `ui__help_window`, and `ui__dialog_yesno`. It also exports `perf_tui_eops` with TUI error/warning functions.

## Control Flow and State

Popup menus use a temporary `ui_browser` over argv strings. Input windows draw a boxed prompt, edit a buffer with printable characters/backspace/escape/enter, and preserve terminal state under `ui__lock`. Info/question windows size text, draw boxes, and wait for a key through `ui__getch`. Error/warning callbacks format a message and show it as a question window.

## Dependencies and Integration Points

It depends on SLang, browser primitives, keysyms, helpline, generic UI utilities, and `ui__lock`. Histogram, script, map, and setup code use these dialogs.

## Risks and Test Signals

Risks include buffer bounds in text input, long-line clipping, terminal resize during modal windows, and `vasprintf` failure fallback. Tests should cover popup hotkey return, text editing, ESC/ENTER behavior, long prompts, yes/no dialogs, and warning display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/tui/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/ui.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/ui.h

## Purpose

`ui.h` declares the high-level perf UI selection and lifecycle API shared by stdio, TUI, and GTK modes.

## Important APIs, Types, and Functions

It declares global `ui__lock`, `perf_gtk_handle`, and `use_browser`; lifecycle functions `setup_browser`, `exit_browser`, optional `ui__init/ui__exit`, `ui__refresh_dimensions`, `stdio__config_color`, and SIGWINCH mask helpers.

## Control Flow and State

When SLang support is absent, inline stubs make `ui__init` fail and `ui__exit` a no-op. Otherwise implementation lives in TUI setup and generic setup.

## Dependencies and Integration Points

It includes the perf mutex abstraction and is used throughout UI code and command frontends that select browser mode.

## Risks and Test Signals

Risks are compile-configuration mismatches and incorrect global `use_browser` assumptions. Build with and without SLang/GTK plus runtime setup/fallback tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/ui.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/util.c -->
# sources/distributed-fs/ceph-client/tools/perf/ui/util.c

## Purpose

`ui/util.c` provides generic error and warning dispatch for perf UI backends.

## Important APIs, Types, and Functions

It implements `ui__error`, `ui__warning`, `perf_error__register`, and `perf_error__unregister`. Static defaults print to stderr, with warnings suppressed when `quiet` is set.

## Control Flow and State

A static `perf_eops` pointer starts at default stdio operations. Backends may register exactly when defaults are active; unregister only succeeds for the currently registered vtable. Errors/warnings vararg-forward to the active vtable.

## Dependencies and Integration Points

GTK and TUI setup register their own `perf_error_ops`. Generic code calls `ui__error/ui__warning` without knowing the active UI.

## Risks and Test Signals

Risks include double registration, unregistering the wrong backend, and varargs misuse. Tests should register/unregister TUI/GTK ops, verify quiet warning suppression, and exercise default stderr fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/util.h -->
# sources/distributed-fs/ceph-client/tools/perf/ui/util.h

## Purpose

`ui/util.h` declares generic UI dialogs and error-operation registration.

## Important APIs, Types, and Functions

It declares input/menu/help/dialog/info functions, `struct perf_error_ops`, and `perf_error__register/perf_error__unregister`.

## Control Flow and State

No runtime behavior exists here. The header defines the UI utility contract used by TUI implementations and generic callers.

## Dependencies and Integration Points

It is included by generic util, TUI util, GTK util/setup, browser code, and script dialogs.

## Risks and Test Signals

Risks are backend implementations missing a declared function or incompatible callback signatures. Build coverage of all UI configurations validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/ui/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/PERF-VERSION-GEN -->
# sources/distributed-fs/ceph-client/tools/perf/util/PERF-VERSION-GEN

## Purpose

`PERF-VERSION-GEN` is a shell script that generates `PERF-VERSION-FILE`, defining the `PERF_VERSION` macro used by perf builds.

## Important APIs, Types, and Functions

It accepts an optional output directory prefix, computes `GVF=${OUTPUT}PERF-VERSION-FILE`, obtains a kernel version tag via `make -sC ../.. kernelversion`, optionally appends an abbreviated git commit suffix, strips a leading `v`, compares against the existing file, and rewrites only on changes.

## Control Flow and State

When inside a git repository, it uses the kernel makefile version and `git log -1 --abbrev=12`; outside git, it can reuse an existing top-level `PERF-VERSION-FILE`. If `TAG` is still empty it falls back to kernelversion. Persistent state is the generated file content.

## Dependencies and Integration Points

It depends on POSIX shell, make, git when available, sed, expr, cut, and the top-level kernel makefile. It is invoked from perf's build system.

## Risks and Test Signals

Risks include relative-path assumptions, non-git source trees, missing make/git, and unnecessary rebuilds if comparison is wrong. Tests should run in git, exported tarball, with output directory set, and with unchanged/changing version strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/PERF-VERSION-GEN -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/addr2line.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/addr2line.c

## Purpose

`addr2line.c` maintains a persistent subprocess interface to GNU `addr2line` or LLVM `llvm-addr2line` so perf can resolve addresses to source file/line and inline frames.

## Important APIs, Types, and Functions

Public APIs are `cmd__addr2line` and `dso__free_a2l`. Internal helpers split `file:line`, start/cleanup `struct child_process`, detect command style with a sentinel request, parse records with `read_addr2line_record`, and append inline records through `inline_list__append_record`.

## Control Flow and State

`cmd__addr2line` lazily starts and stores a subprocess in the DSO when debug line info exists. It configures command style once, writes an address plus comma sentinel, reads the first record, stores file/line outputs, optionally appends inline frames up to `MAX_INLINE_NEST`, drains remaining records until sentinel, and cleans up if EOF is seen. The subprocess is reused across calls per DSO.

## Dependencies and Integration Points

It depends on perf DSO/symbol/srcline/inline infrastructure, `api/io` buffered reads with timeout, `run-command`, and `symbol_conf` options for path, timeout, and warnings. It feeds annotation and source-line reporting.

## Risks and Test Signals

Risks include protocol differences between GNU and LLVM, sentinel misdetection, subprocess hangs/timeouts, SIGPIPE handling, leaked child processes, and inline recursion limits. Tests should resolve normal addresses, address zero, unknown locations, no `.debug_line`, GNU/LLVM tools, inline stacks, timeout/eof, and cleanup on DSO destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/addr2line.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/addr2line.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/addr2line.h

## Purpose

`addr2line.h` declares perf's source-line resolution entry point backed by external addr2line tools.

## Important APIs, Types, and Functions

It forward-declares `struct dso`, `struct inline_node`, and `struct symbol`, and declares `cmd__addr2line` with parameters for DSO path, address, output file/line, DSO cache, inline unwinding, inline output node, and symbol.

## Control Flow and State

No runtime behavior exists. The declaration exposes a function that can both return a direct file/line and populate inline frame state.

## Dependencies and Integration Points

It is used by srcline and annotation code that need file/line data.

## Risks and Test Signals

Risks are signature drift with callers and ownership expectations for returned strings. Build tests plus srcline/annotation resolution tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/addr2line.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/addr_location.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/addr_location.c

## Purpose

`addr_location.c` manages initialization, cleanup, and copying of `struct addr_location`, the perf object that binds a sampled address to thread, maps, map, symbol, CPU, and filtered state.

## Important APIs, Types, and Functions

It implements `addr_location__init`, `addr_location__exit`, and `addr_location__copy`.

## Control Flow and State

Init zeroes/sets default sentinel fields, notably `cpu = -1`. Exit drops references with `maps__zput`, `map__zput`, and `thread__zput`. Copy performs a struct copy, then increments references on maps, map, and thread in the destination.

## Dependencies and Integration Points

It depends on map, maps, and thread reference-counting APIs. Address locations are used widely during sample resolution, hist insertion, branch handling, and annotation.

## Risks and Test Signals

Risks are reference leaks or use-after-free if copy/exit balance is wrong. Tests should initialize, copy, exit, and reuse locations with null and non-null maps/map/thread references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/addr_location.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/addr_location.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/addr_location.h

## Purpose

`addr_location.h` defines `struct addr_location`, perf's resolved-address carrier.

## Important APIs, Types, and Functions

The struct stores thread, maps, map, symbol, address, object address, filtered flag, CPU, socket, and related fields. It declares init/exit/copy helpers.

## Control Flow and State

There is no runtime flow. The header defines ownership-sensitive pointer fields that implementation code reference-counts.

## Dependencies and Integration Points

It forward-declares thread/maps/map/symbol types and is included by sample processing and hist code.

## Risks and Test Signals

Risks are adding pointer fields without updating copy/exit semantics. Build plus reference-count tests around sample resolution validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/addr_location.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/affinity.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/affinity.c

## Purpose

`affinity.c` provides helpers to bind the current thread/process to CPUs while preserving and later restoring the original CPU mask.

## Important APIs, Types, and Functions

Public APIs are `affinity__setup`, `affinity__set`, `affinity__cleanup`, and `cpu_map__set_affinity`. `get_cpu_set_size` derives the mask size from `sysconf(_SC_NPROCESSORS_CONF)` and `CPU_ALLOC_SIZE`.

## Control Flow and State

Setup allocates `sched_getaffinity` masks for original and current affinity and records the original CPU set. `affinity__set` clears and sets one CPU, then calls `sched_setaffinity`; repeated calls avoid reapplying the same CPU. Cleanup restores the original mask once and frees allocations. `cpu_map__set_affinity` builds a stack CPU set from a perf CPU map and applies it.

## Dependencies and Integration Points

It depends on sched affinity APIs, Linux bitmap helpers, perf CPU maps, and `perf_cpu_map__max`. Perf stat/record paths use it when pinning work to target CPUs.

## Risks and Test Signals

Risks include CPU numbers beyond allocated masks, systems with large CPU counts, failed restore on cleanup, and invalid CPU maps. Tests should cover setup failure, repeated set, cleanup idempotence, sparse CPU maps, and permission errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/affinity.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/affinity.h

## Purpose

`affinity.h` declares perf's CPU affinity helper state and APIs.

## Important APIs, Types, and Functions

`struct affinity` stores allocated CPU-set size, original and active masks, current CPU, and a `changed` flag. It declares setup, set, cleanup, and CPU-map affinity functions.

## Control Flow and State

There is no runtime flow. The struct encodes restoration state that callers must clean up.

## Dependencies and Integration Points

It forward-declares `struct perf_cpu_map` and is used by perf utilities that temporarily pin execution.

## Risks and Test Signals

Risks are callers skipping cleanup or copying the struct by value. Compile coverage and affinity lifecycle tests validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/affinity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/amd-sample-raw.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/amd-sample-raw.c

## Purpose

`amd-sample-raw.c` decodes AMD IBS raw sample MSR payloads for `perf report/script -D` style dumps. It turns fetch and op raw data into readable fields, with CPU-family erratum handling and PMU capability-dependent output.

## Important APIs, Types, and Functions

Public APIs are `evlist__amd_sample_raw` and `evlist__has_amd_ibs`. Helpers print IBS fetch control, extended fetch control, op control/data/data2/data3, fetch/op addresses, and branch targets. Static state caches CPU family/model, PMU type numbers for `ibs_fetch` and `ibs_op`, and capabilities `zen4_ibs_extensions`, `ldlat_cap`, and `dtlb_pgsize_cap`.

## Control Flow and State

`evlist__has_amd_ibs` parses PMU mappings and capabilities from `perf_env`, then parses CPUID if IBS PMUs exist. During event dumping, `evlist__amd_sample_raw` checks event type and raw size, maps the sample to an evsel, validates enable/valid bits, and dispatches to fetch or op decoders. Decoders cast raw MSR order into IBS union types and print fields conditionally.

## Dependencies and Integration Points

It depends on AMD IBS union definitions, perf env/session/evlist/sample APIs, and debug output. It integrates with generic sample raw dumping through `sample-raw.h`.

## Risks and Test Signals

Risks include raw-size assumptions, PMU type zero ambiguity, CPU errata conditions, reserved data-source values, and stale static capability state across sessions. Tests need AMD IBS fetch/op samples from Zen generations, invalid raw samples, Zen4 capability fields, erratum-affected family 0x19 models, and sessions without IBS mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/amd-sample-raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arc.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arc.c

## Purpose

`annotate-arc.c` creates the ARC architecture descriptor used by perf annotation/disassembly.

## Important APIs, Types, and Functions

It implements `arch__new_arc`, allocating `struct arch`, setting `name = "arc"`, copying machine ID flags, and configuring objdump comment character `;`.

## Control Flow and State

The function allocates with `zalloc`, returns `NULL` on failure, and otherwise returns the initialized architecture object as `const struct arch *`.

## Dependencies and Integration Points

It depends on the generic disasm architecture model and is selected when perf annotates ARC binaries.

## Risks and Test Signals

Risks are minimal but include missing ARC-specific instruction classification. Tests should disassemble ARC code and verify comments are parsed correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arm.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arm.c

## Purpose

`annotate-arm.c` creates the ARM architecture descriptor for perf annotation and classifies ARM call/jump instructions.

## Important APIs, Types, and Functions

`struct arch_arm` embeds `struct arch` and stores compiled regexes for call and jump instructions. `arm__associate_instruction_ops` matches instruction names against `blx?` with optional conditions and branch/jump regexes, then associates `call_ops` or `jump_ops`. Public `arch__new_arm` allocates and initializes the descriptor.

## Control Flow and State

Creation sets objdump comment and skip-function characters, installs the associate callback, compiles regexes, and returns `NULL` on allocation or regex failure. Instruction association caches matched ops in the generic arch table.

## Dependencies and Integration Points

It depends on regex, generic annotate/disasm ops, and ARM objdump syntax. Annotation uses it to build call graphs and branch semantics in ARM disassembly.

## Risks and Test Signals

Risks are regex incompleteness for ARM/Thumb mnemonics and leaks on partial regex failure. Tests should annotate ARM binaries containing calls, conditional branches, unconditional branches, and non-branch instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arm64.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arm64.c

## Purpose

`annotate-arm64.c` creates the ARM64 architecture descriptor for perf annotation and adds ARM64-specific instruction parsing, especially move-immediate target parsing.

## Important APIs, Types, and Functions

`struct arch_arm64` embeds `struct arch` and compiled regexes. `arm64_mov__parse` parses `mov` operands and records immediate values as jump targets when present. `arm64_mov_ops` installs that parser. `arm64__associate_instruction_ops` recognizes calls, jumps, and mov instructions. Public `arch__new_arm64` initializes the descriptor and regexes.

## Control Flow and State

Creation allocates state, sets architecture metadata and callback, compiles regexes for call/jump matching, and returns the generic arch pointer. During annotation, instruction names are matched lazily and associated with ops for later parsing/rendering.

## Dependencies and Integration Points

It depends on regex, generic annotate/disasm instruction operations, and ARM64 objdump syntax. It feeds annotation's branch/call classification and immediate target display.

## Risks and Test Signals

Risks include operand parser assumptions, missing aliases, regex drift with objdump output, and partial initialization cleanup. Tests should cover ARM64 `bl`, `b.*`, `cbz/cbnz/tbz/tbnz`, `ret`, `mov` immediate forms, and non-branch instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-arm64.c -->
