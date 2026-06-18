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
