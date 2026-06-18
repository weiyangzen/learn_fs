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
