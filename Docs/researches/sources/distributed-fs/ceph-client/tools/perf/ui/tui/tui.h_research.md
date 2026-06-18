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
