# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/checklist.c

## Purpose

`lxdialog/checklist.c` implements the ncurses radiolist/checklist dialog used by `mconf` for choice menus. In this kconfig usage, it presents one selectable item plus a Help button.

## Important APIs, Types, and Functions

The exported function is `dialog_checklist()`. Internal helpers are `print_item()`, `print_arrows()`, and `print_buttons()`. It consumes the global item list API from `dialog.h`/`util.c` (`item_foreach()`, `item_set()`, `item_set_selected()`, `item_is_tag()`, `item_str()`, and related helpers).

## Control Flow

`dialog_checklist()` chooses an initial item from the active or preselected tag, sizes and centers the dialog, creates a list subwindow, renders items and scroll arrows, and enters a key loop. Arrow keys and `+`/`-` move or scroll; hotkeys jump within visible rows; `s`, space, or Enter marks the current item selected and returns the current button; `h`/`?` returns Help; resize recreates the dialog; ESC is passed through `on_key_esc()`.

## State and Persistence Behavior

It uses static layout fields `list_width`, `check_x`, and `item_x`, and mutates selection flags in the global dialog item list. It has no file persistence.

## Dependencies and Integration Points

It depends on ncurses, global `dlg` theme colors, drawing helpers from `util.c`, and the item list built by `mconf` before calling `dialog_checklist()`.

## Risks and Edge Cases

Small terminals return `-ERRDISPLAYTOOSMALL`. Long labels are truncated to `list_width - item_x`. It allocates a temporary string for each printed item; allocation failure is not checked. Because selection is stored globally, callers must `item_reset()` before building each list.

## Test Signals

Exercise choices with no default, default selected item, comments, long labels, hotkeys, scrolling, Help, resize, small terminal failure, and ESC behavior.
