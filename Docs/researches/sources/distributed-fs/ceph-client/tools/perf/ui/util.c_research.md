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
