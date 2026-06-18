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
