# sources/distributed-fs/ceph-client/scripts/kconfig/mconf.c

## Purpose

`mconf.c` implements the terminal `menuconfig` frontend. It traverses the shared kconfig menu tree, renders menus via lxdialog, edits symbol values, shows help/search results, loads/saves alternate config files, and handles exit/save behavior.

## Important APIs, Types, and Functions

Important functions are `set_config_filename()`, `set_subtitle()`, `reset_subtitle()`, `show_textbox_ext()`, `show_help()`, `search_conf()`, `build_conf()`, `conf_choice()`, `conf_string()`, `conf_load()`, `conf_save()`, `conf()`, `conf_message_callback()`, `handle_exit()`, `sig_handler()`, and `main()`. Process-global state tracks current filename, subtitle trail, current menu, indentation, child count, single-menu mode, show-all mode, save-and-exit, and silent mode.

## Control Flow

`main()` parses optional silent mode, parses Kconfig, reads `.config`, initializes curses, installs config/message callbacks, then enters `conf(&rootmenu)`. `conf()` rebuilds the lxdialog item list from visible menu nodes, invokes `dialog_menu()`, and interprets returned actions. It descends into menus, opens choices, edits string/int/hex values, applies Y/N/M/toggle to tristate symbols, opens search/help dialogs, toggles hidden options, or loads/saves configs. `handle_exit()` prompts to save when dirty, writes `.config`, writes autoconf output, ends curses, and prints final status.

## State and Persistence Behavior

UI state is global and session-scoped: subtitle trail, single-menu expanded flags in `menu->data`, scroll positions, and current filename. Persistent behavior is delegated to `conf_read()`, `conf_write()`, and `conf_write_autoconf()`. `sig_handler()` exits through `handle_exit()` so SIGINT still offers save behavior.

## Dependencies and Integration Points

It depends on `lkc.h`, `lxdialog/dialog.h`, `mnconf-common.h`, locale/signal/system headers, and the menu/symbol/conf APIs. `MENUCONFIG_MODE=single_menu` changes navigation. `MENUCONFIG_COLOR` is consumed by lxdialog initialization.

## Risks and Edge Cases

The numeric return contract with `menubox.c` is implicit and fragile. Signal handling calls complex UI/save logic from a signal context, which is historically accepted here but not async-signal-safe. `build_conf()` relies on `menu_is_visible()` recalculation side effects. `single_menu_mode` stores booleans in `menu->data`, sharing a field that other frontends could also use in the same process.

## Test Signals

Run `menuconfig` through navigation, Y/N/M/toggle edits, choice menus, string/int/hex validation, search and jump keys, load/save alternate config, dirty exit save/discard/cancel, single-menu mode, show-all toggle, silent mode, SIGINT, resize, and small terminal handling.
