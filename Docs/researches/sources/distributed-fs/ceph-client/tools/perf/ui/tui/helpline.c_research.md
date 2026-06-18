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
