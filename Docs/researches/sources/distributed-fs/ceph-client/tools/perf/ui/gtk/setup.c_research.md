# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/setup.c

## Purpose

`gtk/setup.c` initializes and exits the GTK backend.

## Important APIs, Types, and Functions

It exports `perf_gtk__init` and `perf_gtk__exit`.

## Control Flow and State

Initialization calls `gtk_init_check`; on success it registers GTK error ops, installs GTK helpline/progress/hpp callbacks, and returns 0. Exit unregisters GTK error ops. The `wait_for_ok` argument is unused.

## Dependencies and Integration Points

It depends on GTK, generic UI error registration, GTK helpline/progress/hist helpers, and is loaded by `ui/setup.c` through `dlsym`.

## Risks and Test Signals

Risks are partial initialization when GTK is unavailable and mismatched error-op registration. Tests should run with DISPLAY available and unavailable, then verify fallback behavior and unregister on exit.
