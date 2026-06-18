# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/header.c

Purpose: Provides a TUI window for browsing perf session header information.

Important APIs/types/functions: `tui__header_window` is the public entry. `ui__list_menu` creates a generic argv-backed browser. `list_menu__run` handles the header browser event loop. `ui_browser__argv_write` renders one line with horizontal offset support.

Control flow: `tui__header_window` writes `perf_header__fprintf_info` into an `open_memstream`, counts newline-separated rows, builds an argv array by replacing newlines with NULs, and passes it to the list menu. The menu uses generic browser navigation, `LEFT`/`RIGHT` adjust the horizontal offset stored in `browser->priv`, help shows a static key list, and quit returns.

State and persistence: All state is transient: the memstream buffer, argv vector, and horizontal offset. No header data is modified.

Dependencies and integration points: Depends on perf session/header printing, generic `ui_browser` argv backend, key symbols, and S-Lang UI helpers.

Risks: If `open_memstream` fails, `fp` is not checked before use in this snapshot. The newline count drives allocation and assumes final parsing produces `argc + 1` positions, guarded by `BUG_ON`.

Test signals: Open header windows for normal and unusual perf.data files, exercise horizontal scrolling, help, resize, and exit paths. Test allocation/open_memstream failure where possible.
