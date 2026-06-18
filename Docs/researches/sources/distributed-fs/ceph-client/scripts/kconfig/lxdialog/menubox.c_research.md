# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/menubox.c

## Purpose

`lxdialog/menubox.c` implements the main ncurses menu dialog for `mconf`, including scrolling lists, hotkeys, command buttons, and kconfig-specific key returns for Y/N/M/search/show-all actions.

## Important APIs, Types, and Functions

The exported API is `dialog_menu()`. Internal helpers include `do_print_item()`, `print_arrows()`, `print_buttons()`, and `do_scroll()`. It reads items from the global dialog item list and returns numeric action codes consumed by `mconf.c`.

## Control Flow

`dialog_menu()` sizes the dialog from current terminal geometry, creates a menu subwindow, chooses the initial item based on a selected menu pointer and saved scroll offset, renders visible rows, and enters a key loop. Arrow, page, `+`, `-`, and hotkey navigation update `choice` and `scroll`. Enter returns the active button. Direct keys map to actions: `y`/`s` set yes, `n` set no, `m` set module, space toggles, `/` searches, `z` toggles hidden options, `h`/`?` shows help, and ESC exits. Resize rebuilds from scratch.

## State and Persistence Behavior

Static `menu_width` and `item_x` hold layout. The caller-owned `s_scroll` stores scroll position across invocations. Current selection is written into the global item list. No filesystem state is touched.

## Dependencies and Integration Points

It depends on ncurses, lxdialog theme/drawing helpers, and the item list populated by `mconf build_conf()`. Return codes are tightly coupled to the switch in `mconf.c::conf()`.

## Risks and Edge Cases

Menu labels are truncated to fit; hotkey detection skips bracketed option state and exempt letters. The return-code protocol is numeric and implicit. Very small terminals return `-ERRDISPLAYTOOSMALL`. Callers must reset item state and preserve `s_scroll` appropriately.

## Test Signals

Exercise large menus, page scrolling, preserved scroll after returning from submenus, hotkeys, Y/N/M/space actions, search key, show-all key, resize handling, small terminal failure, and empty item lists.
