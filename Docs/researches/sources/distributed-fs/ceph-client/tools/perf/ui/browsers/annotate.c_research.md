# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/annotate.c

Purpose: Implements the main perf TUI annotation browser for disassembled symbols, source interleaving, hottest-instruction navigation, jump visualization, searching, and optional data-type display.

Important APIs/types/functions: `struct annotate_browser` embeds `ui_browser` and tracks current hot rb-node, selected annotation line, architecture, hist entry, debuginfo, evsel, type hash, and search state. Public entry points are `hist_entry__tui_annotate` and `__hist_entry__tui_annotate`. Major helpers render rows, calculate percent rb-trees, toggle source, jump/call to targets, search forward/backward, update titles, and manage debuginfo/type hash state.

Control flow: Entry initializes S-Lang tty state, ensures the symbol is annotated, configures browser callbacks, optionally selects a requested address, then enters `annotate_browser__run`. The run loop refreshes via the generic browser, recalculates hot lines for timers, handles many command keys, calls nested annotation for call targets, toggles source and display options, and exits on navigation/quit keys. Jump arrows are drawn after list refresh using current selection and local target lookup.

State and persistence: It mutates global annotation options, symbol annotation caches, hist decay state, helpline stack, optional static `annotate_he` copy for perf top, debuginfo handles, and an in-memory type hash. It writes annotation dumps only when the user presses `P`.

Dependencies and integration points: Deeply integrated with perf symbol/disassembly, map/dso/thread, hists/evsel, annotation writing, debuginfo, branch counters, script browser, and `ui_browser`.

Risks: The file has many stateful UI paths; stale selection after source toggles, rb-node invalidation after timer recalculation, and perf-top lifetime handling are key hazards. Source reannotation purges and rebuilds lists, so index preservation is delicate.

Test signals: TUI annotate a symbol with and without source, with timers, branch counters, jump arrows, searches, call targets, source toggling, offset/full-address toggles, type display with/without debuginfo, and perf top. Validate no use-after-free with repeated nested call navigation.
