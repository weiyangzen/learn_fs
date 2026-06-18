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
