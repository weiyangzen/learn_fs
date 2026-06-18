# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/util.c

## Purpose

`lxdialog/util.c` provides shared ncurses infrastructure for `mconf`: theme selection, color initialization, screen clearing, dialog lifecycle, drawing primitives, ESC/resize handling, and the global linked list of dialog items.

## Important APIs, Types, and Functions

Public functions include `init_dialog()`, `set_dialog_backtitle()`, `set_dialog_subtitles()`, `end_dialog()`, `attr_clear()`, `dialog_clear()`, `print_title()`, `print_autowrap()`, `print_button()`, `draw_box()`, `draw_shadow()`, `first_alpha()`, `on_key_esc()`, `on_key_resize()`, `item_reset()`, `item_make()`, `item_add_str()`, `item_set_tag()`, `item_set_data()`, `item_set_selected()`, `item_activate_selected()`, `item_data()`, `item_tag()`, `item_count()`, `item_set()`, `item_n()`, `item_str()`, `item_is_selected()`, and `item_is_tag()`. Internal theme helpers configure mono, classic, black background, and blue-title themes.

## Control Flow

`init_dialog()` starts curses, saves cursor position, validates minimum terminal size, configures theme/color from `MENUCONFIG_COLOR`, enables keypad/cbreak/noecho, and clears the screen. Drawing functions are called by every widget. `on_key_esc()` temporarily disables keypad and drains pending bytes to distinguish standalone ESC from escape sequences. Item-list functions build and traverse a simple linked list that dialog widgets render.

## State and Persistence Behavior

Global state includes `saved_x`, `saved_y`, `dlg`, `item_head`, `item_cur`, and `item_nil`. Theme and subtitle state persist for the life of the dialog session. No files are written.

## Dependencies and Integration Points

It depends on ncurses and is linked into `mconf` with all other lxdialog widgets. `mconf.c` uses `saved_x/saved_y` during signal exit, supplies backtitles/subtitles, and repeatedly rebuilds the item list before menus/checklists.

## Risks and Edge Cases

The item list uses unchecked `malloc()` and fixed-size item strings. Global state makes the library non-reentrant. `print_autowrap()` copies prompts into a fixed buffer, truncating long prompts. Color-pair numbering assumes enough curses color pairs. ESC handling is delicate because terminal escape sequences and user double-ESC share input timing.

## Test Signals

Run menuconfig under supported color themes, monochrome/limited terminals, small terminals, terminal resize, ESC/double-ESC, long prompts/items, repeated menu rebuilds with leak checks, and signal-triggered exit cleanup.
