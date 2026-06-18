# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/util.c

## Purpose

`gtk/util.c` owns GTK context allocation and GTK-specific error/warning presentation.

## Important APIs, Types, and Functions

It defines global `struct perf_gtk_context *pgctx`, `perf_gtk__activate_context`, `perf_gtk__deactivate_context`, static error/warning functions, and exported `perf_gtk_eops`.

## Control Flow and State

Activation allocates a context, stores the main window, and returns it. Deactivation frees and nulls the context pointer. Errors use a modal message dialog. Warnings prefer an info bar if compiled and active, otherwise the statusbar, otherwise they fall back to stderr-like behavior.

## Dependencies and Integration Points

It depends on `ui/util.h` error ops, GTK widgets, and optional info-bar fields from `gtk.h`. `gtk/setup.c` registers `perf_gtk_eops`.

## Risks and Test Signals

Risks include registering multiple UI error providers, stale `pgctx` after window close, and warnings before widget setup. Test with active/inactive context, info-bar and no-info-bar builds, repeated activation/deactivation, and warning/error display.
