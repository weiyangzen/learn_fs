# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/browser.c

## Purpose

`gtk/browser.c` contains shared GTK browser helpers: signal handling, default window sizing, percentage color markup, and standard info/status widgets.

## Important APIs, Types, and Functions

It exports `perf_gtk__signal`, `perf_gtk__resize_window`, `perf_gtk__get_percent_color`, `perf_gtk__setup_info_bar` when supported, and `perf_gtk__setup_statusbar`. The color policy maps high percentages to red, medium percentages to dark green, and low percentages to unmarked text.

## Control Flow and State

Signal handling calls `perf_gtk__exit(false)` then reports the signal. Resizing chooses three quarters of the monitor containing the GTK window. Widget setup stores pointers and statusbar context IDs in global `pgctx`. Info bars hide on OK response.

## Dependencies and Integration Points

It depends on GTK/GDK APIs, perf GTK context state, and `MIN_RED`/`MIN_GREEN` histogram color thresholds. It is used by GTK hists and annotation code.

## Risks and Test Signals

Risks include old GTK API assumptions (`window->window`), absent info-bar support, and `pgctx` null misuse. Test signals are GTK startup/shutdown, window sizing on multi-monitor setups, warning display via info/status bars, and percentage markup in hist and annotate views.
