# sources/distributed-fs/ceph-client/scripts/kconfig/gconf.c

## Purpose

`gconf.c` implements the GTK 3 graphical kconfig frontend. It renders the shared kconfig menu tree into one or two `GtkTreeView` widgets, shows symbol help, edits symbol values, loads/saves config files, and coordinates visible/full/split/single view modes.

## Important APIs, Types, and Functions

Important state includes `enum view_mode`, option-display modes, global GTK widgets, tree stores `tree1`/`tree2`, `pix_menu`, and menu pointers `browsed`/`selected`. Core functions include `set_node()`, `display_tree()`, `recreate_tree()`, `fixup_rootmenu()`, `set_view_mode()`, `update_tree()`, `visible_func()`, `change_sym_value()`, `toggle_sym_value()`, `renderer_edited()`, `init_main_window()`, `init_left_tree()`, `init_right_tree()`, and `main()`. Callback functions handle menu actions, toolbar buttons, tree clicks/keys, cursor changes, window deletion, and save prompts.

## Control Flow

`main()` initializes GTK, locates `gconf.ui`, parses Kconfig with `conf_parse()`, tags root menus for split view, builds the main window from GtkBuilder XML, initializes tree columns/models, reads `.config`, chooses the starting view, and enters `gtk_main()`. Tree creation walks `rootmenu` and stores `struct menu *` in each row. Selection updates help text through `menu_get_ext_help()`. User clicks or keypresses call symbol setters, then refresh tree row values and visibility filters. Save/load callbacks delegate to `conf_read()`, `conf_write()`, and `conf_write_autoconf()`.

## State and Persistence Behavior

UI state is process-global: view mode, option visibility mode, selected/browsed menu pointers, dirty button sensitivity, text tags, model contents, and loaded pixbufs. Persistent output is handled by `confdata.c`; `gconf` only chooses filenames through dialogs and triggers writes. The changed callback updates Save affordances when symbol APIs mark the configuration dirty.

## Dependencies and Integration Points

It depends on GTK/GDK/Pango, `gconf.ui`, XPM icons under `scripts/kconfig/icons`, `SRCTREE` for resource lookup, and shared kconfig APIs from `lkc.h`. It is built only when `gconf-cfg.sh` finds GTK+ 3.

## Risks and Edge Cases

Resource path construction depends on `SRCTREE`, `argv[0]`, or current directory matching the kernel script layout. Missing icons produce warnings; missing UI XML is fatal. `renderer_edited()` ignores the return value from `sym_set_string_value()`, so invalid values are not explicitly surfaced in this frontend. `gtk_tree_model_get()` ownership for string columns needs care; the current code fetches `old_def` but does not use/free it. Filtering calls `menu_is_visible()`, which recalculates symbol state and can be expensive on large trees.

## Test Signals

Build and launch `gconfig` with GTK+ 3, exercise load/save/save-as, dirty-state button toggling, single/split/full view switching, show-name/range/data toggles, normal/all/prompt filters, boolean/tristate edits, string/int/hex edits including invalid inputs, and resource lookup with and without `SRCTREE`.
