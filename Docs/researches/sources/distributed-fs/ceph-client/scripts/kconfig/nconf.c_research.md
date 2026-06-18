# sources/distributed-fs/ceph-client/scripts/kconfig/nconf.c

## Purpose
`nconf.c` implements the ncurses-based `nconfig` frontend for Kconfig. It parses the Kconfig tree through the shared `lkc` API, displays menus and symbols in a terminal UI, lets users change bool/tristate/string/int/hex values, performs symbol searches, loads alternate `.config` files, and writes the selected configuration plus autoconf output on exit.

## Important APIs, Types, and Functions
The central local type is `struct mitem`, which binds an ncurses `ITEM` string/tag to a `struct menu *` and visibility flag. Global UI state includes `main_window`, `curses_menu`, `curses_menu_items`, `k_menu_items`, `items_num`, `current_menu`, `show_all_items`, `single_menu_mode`, and `global_exit`.

Key handlers are represented by `struct function_keys` and dispatch to `handle_f1()` through `handle_f9()` for global help, symbol help, instructions, show-all toggle, back, save, load, search, and exit. Menu construction and interaction live in `build_conf()`, `selected_conf()`, `conf()`, `conf_choice()`, and `conf_string()`. Persistence entry points are `conf_load()`, `conf_save()`, `do_exit()`, and `set_config_filename()`.

Search uses `search_conf()`, `sym_re_search()`, `get_relations_str()`, and `show_scroll_win_ext()` with `handle_search_keys()` from the shared menuconfig/nconfig support. Incremental in-menu matching is handled by `struct match_state`, `do_match()`, and `get_mext_match()`.

## Control Flow
`main()` optionally silences early parser messages for `-s`, calls `conf_parse()` and `conf_read(NULL)`, reads `NCONFIG_MODE`, initializes curses/color/menu settings, builds the root window, and loops through `conf(&rootmenu)` until `global_exit` is set. `conf()` calls `selected_conf()`, which repeatedly rebuilds the visible item list, posts the menu, handles navigation and special keys, and applies symbol changes or enters submenus.

`build_conf()` recursively converts the Kconfig `struct menu` tree into ncurses items. It distinguishes ordinary symbols, menus, comments, choices, invisible entries, menuconfig submenus, and string-like symbols. Value changes route into shared Kconfig functions such as `sym_toggle_tristate_value()`, `sym_set_tristate_value()`, `choice_set_value()`, and `sym_set_string_value()`, which then invalidate and recalculate symbol state.

## State and Persistence
Terminal state is managed through ncurses windows, panels, and menu items and is cleaned up before exit. Configuration state is held by the shared Kconfig symbol/menu graph. The currently selected config filename is stored in static `filename` and displayed in `menu_backtitle`. `conf_write()` writes the chosen configuration and `conf_write_autoconf(0)` refreshes generated autoconf state.

`dialog_input_result` is a reusable heap buffer grown by `dialog_inputbox()`. `single_menu_mode` uses `menu->data` as a fold/unfold flag, which is a UI-specific reuse of a generic menu data field and must not collide with other frontends in the same process.

## Dependencies and Integration Points
The file depends on ncurses menu/form/panel APIs via `nconf.h`, shared Kconfig internals from `lkc.h`, `mnconf-common.h`, and helper functions implemented in `nconf.gui.c`. It integrates with the Kconfig parser, config file reader/writer, symbol calculation engine, and relation/help rendering utilities.

## Risks and Edge Cases
`MAX_MENU_ITEMS` caps displayed items at 4096; large Kconfig trees can be truncated silently by `item_make()`. Several fixed 256 byte item buffers can truncate prompts or values. Source contains duplicated statements/braces in a few places, such as a duplicate `continue`, suggesting this tree may include accidental merge artifacts that should be compile-tested. Terminal size below 75x20 is rejected. Interactive save paths call `conf_write_autoconf(0)` even after a failed write attempt in `do_exit()`, which is worth checking against expected build behavior.

## Test Signals
Coverage comes indirectly from Kconfig frontend use, `make nconfig`, and the Kconfig pytest fixtures in this subset for choices, transitional symbols, visibility, and recursive dependency handling. Manual tests should exercise resize, search, F-key fallback, alternate save/load, single menu mode, choice menus, invalid numeric input, and write failure dialogs.
