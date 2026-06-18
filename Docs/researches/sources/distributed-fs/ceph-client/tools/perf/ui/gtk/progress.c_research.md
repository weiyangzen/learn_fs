# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/progress.c

## Purpose

`gtk/progress.c` implements `ui_progress_ops` for GTK using a modal-ish progress dialog and progress bar.

## Important APIs, Types, and Functions

It defines static GTK widgets `dialog` and `progress`, `gtk_ui_progress__update`, `gtk_ui_progress__finish`, a `gtk_ui_progress__ops` vtable, and public `gtk_ui_progress__init`.

## Control Flow and State

The first update lazily creates a window and progress bar titled from `ui_progress->title`. Updates compute `curr / total`, format a percentage string, set the fraction/text, show widgets, and drain pending GTK events. Finish destroys the dialog and clears globals.

## Dependencies and Integration Points

It depends on GTK and generic `ui/progress.h`. `perf_gtk__init` installs it so long-running perf operations can report progress in GTK mode.

## Risks and Test Signals

Risks include division by zero if callers violate progress initialization, reentrancy while pumping GTK events, and stale widget globals after destroy. Tests should initialize/update/finish multiple progress objects and verify clean behavior for small, large, and completed totals.
