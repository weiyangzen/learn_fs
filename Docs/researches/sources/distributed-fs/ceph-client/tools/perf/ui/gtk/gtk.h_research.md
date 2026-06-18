# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/gtk.h

## Purpose

`gtk.h` is the shared GTK UI interface for perf. It declares the GTK context, initialization/exit hooks, helper widgets, histogram browser entry point, and annotation entry points.

## Important APIs, Types, and Functions

`struct perf_gtk_context` stores main window, notebook, optional info bar/message label, status bar, and statusbar context ID. Declarations include `perf_gtk__init`, `perf_gtk__exit`, `perf_gtk__activate_context`, `perf_gtk__deactivate_context`, `perf_gtk__init_helpline`, `gtk_ui_progress__init`, `perf_gtk__init_hpp`, `evlist__gtk_browse_hists`, and `hist_entry__gtk_annotate`.

## Control Flow and State

The header has no runtime flow, but it defines `pgctx` as the global active GTK UI context and provides an inline active-context check. A stub `perf_gtk__setup_info_bar` returns `NULL` when info-bar support is not compiled in.

## Dependencies and Integration Points

It includes GTK while suppressing strict-prototype diagnostics, and forward-declares perf event/hist/timer types. It is included by all GTK backend files and dynamically loaded by `ui/setup.c` when GTK browser mode is selected.

## Risks and Test Signals

The main risks are build-configuration drift around GTK and info-bar support, and global context lifetime mistakes. Build tests with and without GTK info bar support plus runtime annotation/hist browsing validate the contract.
