# sources/distributed-fs/ceph-client/scripts/kconfig/gconf.ui

## Purpose

`gconf.ui` is the GtkBuilder XML layout consumed by `gconf.c`. It declares the main GTK window, menubar, toolbar, split panes, tree views, and help text view for the graphical kconfig frontend.

## Important APIs, Types, and Functions

There are no functions. Important object IDs are `window1`, `menubar1`, `load1`, `save1`, `save_as1`, `quit1`, `show_name1`, `show_range1`, `show_data1`, `set_option_mode1/2/3`, `introduction1`, `about1`, `license1`, toolbar buttons `button1` through `button8`, `hpaned1`, `vpaned1`, `treeview1`, `treeview2`, and `textview3`.

## Control Flow

Runtime flow is declarative: `gtk_builder_new_from_file()` loads this file, then `init_main_window()` looks up object IDs and attaches C callbacks. Accelerators for load/save/quit/introduction/about are declared here; all dynamic behavior is implemented in `gconf.c`.

## State and Persistence Behavior

The file stores static UI defaults such as window size, widget visibility, labels, tooltips, active radio/check menu defaults, paned layout, and text view wrapping. It has no runtime persistence; user configuration persistence is handled by `confdata.c`.

## Dependencies and Integration Points

It must remain synchronized with the object IDs expected by `gconf.c`. GTK stock IDs and deprecated widget names indicate it targets older GTK 3 compatibility. It is located through `SRCTREE` or an executable-relative path in `gconf.c`.

## Risks and Edge Cases

Renaming an object ID silently breaks callback wiring because `gtk_builder_get_object()` may return NULL and later GTK calls can fail. UI changes must preserve the two-tree plus help-pane structure assumed by the C code. Deprecated GTK constructs can create portability warnings or future compatibility issues.

## Test Signals

Load the file with GtkBuilder, launch `gconfig`, verify all menu items and toolbar buttons are connected, switch option radio modes, toggle visible columns, and confirm tree/help panes resize without missing widget warnings.
