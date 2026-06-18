# sources/distributed-fs/ceph-client/tools/perf/ui/tui/progress.c

## Purpose

`tui/progress.c` implements terminal progress bars for the SLang UI backend.

## Important APIs, Types, and Functions

It defines `__tui_progress__init`, `get_title`, `tui_progress__update`, `tui_progress__finish`, a `ui_progress_ops` instance, and public `tui_progress__init`.

## Control Flow and State

Initialization sets the update step based on terminal width. Update returns when browser mode is inactive or total is zero, formats optional unit-scaled title, refreshes dimensions, draws a centered three-row box and filled bar under `ui__lock`, then refreshes SLang. Finish clears the same region.

## Dependencies and Integration Points

It depends on generic progress, SLang, terminal dimensions, unit formatting, `ui__lock`, and global `use_browser`.

## Risks and Test Signals

Risks include narrow terminal division, resize during progress, and drawing over active browser content. Tests should exercise zero total, small total, large total, resize, and finish cleanup in TUI and non-browser modes.
