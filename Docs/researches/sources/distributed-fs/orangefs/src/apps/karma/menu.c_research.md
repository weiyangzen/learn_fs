# sources/distributed-fs/orangefs/src/apps/karma/menu.c

## Purpose
`menu.c` builds Karma's GTK menu bar and About dialog. It provides File actions for selecting a filesystem and quitting, plus Help/About.

## Important APIs, Types, and Functions
`menu_items[]` is a `GtkItemFactoryEntry` table defining menu paths, accelerators, callbacks, and stock item metadata. `gui_menu_setup(GtkWidget *window)` creates an accelerator group and item factory, materializes the menu entries, attaches accelerators to the main window, stores the window in a file-level `main_window`, and returns the menu bar widget. `gui_menu_about_popup()` creates a modal-ish GTK dialog with static About text and an OK button that destroys the dialog.

## Control Flow
`karma.c` calls `gui_menu_setup()` once during startup. Menu activation is then GTK-driven: Ctrl-S invokes `gui_fsview_popup()`, Ctrl-Q invokes `gtk_main_quit()`, and Help/About invokes the local popup helper.

## State and Persistence
The file stores a `GtkWidget *main_window` static/global for dialog parenting. No persistent state is written. GTK item factory and accelerator objects remain owned by the GTK widget hierarchy.

## Dependencies and Integration Points
It depends on GTK2 item factory APIs, `gui_fsview_popup()` from `fsview.c`, and the main window supplied by `karma.c`. The UI is part of the Karma module list in `module.mk.in`.

## Risks and Edge Cases
This file defines `GtkWidget *main_window = NULL` while `karma.c` also defines a global `main_window`; because this definition is not `static`, it can collide at link time on toolchains that do not permit common symbols. GTK item factory is deprecated, so porting to newer GTK requires replacing this menu construction. The About dialog text is fixed and does not include version/build information.

## Test Signals
Build/link Karma with modern compiler defaults such as `-fno-common` to detect duplicate global definitions. UI smoke tests should trigger Select File System, Quit, and About actions and verify accelerators work.
