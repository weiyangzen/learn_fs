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
