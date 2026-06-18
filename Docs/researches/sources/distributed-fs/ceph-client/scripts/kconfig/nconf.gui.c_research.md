# sources/distributed-fs/ceph-client/scripts/kconfig/nconf.gui.c

## Purpose
`nconf.gui.c` provides reusable ncurses UI primitives for `nconf.c`: color/theme initialization, centered titles, text filling, button dialogs, input boxes, full-window refresh, and scrollable help/search windows.

## Important APIs, Types, and Functions
The file exports global attribute variables declared in `nconf.h`, including `attr_normal`, `attr_main_heading`, dialog attributes, scroll window attributes, and function-key attributes. `struct nconf_attr_param` describes one theme entry, with separate color and no-color tables. Public helpers include `set_colors()`, `print_in_middle()`, `get_line_no()`, `get_line()`, `get_line_length()`, `fill_window()`, `btn_dialog()`, `dialog_inputbox()`, `refresh_all_windows()`, `show_scroll_win()`, and `show_scroll_win_ext()`.

## Control Flow
`set_colors()` selects either color-capable or monochrome attributes and initializes curses color pairs. Dialog helpers compute dimensions from message text and terminal size, create windows/subwindows/panels, post menu or input UI, handle navigation keys, then free curses resources. `show_scroll_win_ext()` creates a pad for arbitrary text, tracks horizontal and vertical offsets, handles scroll keys, and optionally delegates unknown keys to a caller callback.

## State and Persistence
Most state is transient curses state. `dialog_inputbox()` grows and reuses a caller-owned result buffer through `resultp` and `result_len`, preserving input text across calls in the caller. Scroll offsets can persist across repeated `show_scroll_win_ext()` calls through optional `vscroll` and `hscroll` pointers.

## Dependencies and Integration Points
The file depends on ncurses menu/panel/form support via `nconf.h`, `xalloc.h`, and shared Kconfig string helpers indirectly. It is tightly coupled to `nconf.c` for attribute globals and function-key constants.

## Risks and Edge Cases
Dialog sizing can produce very small derived windows if the terminal is near the lower bound; input code must guard cursor positions against `prompt_width - 1`. `dialog_inputbox()` uses plain `realloc()` in the character insertion path rather than `xrealloc()`, so allocation failure would be less controlled there. The file contains a duplicate `menu_opts_off(menu, O_SHOWDESC)` call. `print_in_middle()` does not clamp negative x coordinates for strings wider than the target width.

## Test Signals
Manual `make nconfig` testing should cover color and monochrome terminals, long help text, horizontal scrolling, text insertion/deletion/home/end in input boxes, ESC/F-key exit paths, and terminal resize from the caller.
