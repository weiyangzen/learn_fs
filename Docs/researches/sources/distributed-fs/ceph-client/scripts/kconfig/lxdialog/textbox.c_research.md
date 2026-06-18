# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/textbox.c

## Purpose

`lxdialog/textbox.c` implements the scrollable ncurses text viewer used by `mconf` for help, README, search results, and status messages.

## Important APIs, Types, and Functions

The exported function is `dialog_textbox()`. Internal helpers are `back_lines()`, `get_line()`, `print_line()`, `print_page()`, `print_position()`, and `refresh_text_box()`. Optional callback `extra_key_cb` lets search results handle jump-key navigation.

## Control Flow

The dialog initializes page pointers and optional saved vertical/horizontal scroll, sizes and draws the window, renders a page, then processes movement keys. Home/end, vi-style keys, arrows, page up/down, space, and horizontal scroll keys adjust `page` and `hscroll`; ESC exits through `on_key_esc()`. Unknown keys are offered to `extra_key_cb`, which can request dialog exit. On close, optional scroll pointers are updated for caller reuse.

## State and Persistence Behavior

Static file-local state tracks current buffer, page pointer, scroll offsets, page length, and visible start/end offsets. It persists only during the dialog call, except scroll offsets returned to the caller.

## Dependencies and Integration Points

It uses ncurses drawing helpers and theme colors. `mconf` uses it directly for help/search and passes `handle_search_keys()` from `mnconf-common.c` to make numbered search jump entries actionable.

## Risks and Edge Cases

Line buffers are capped at `MAX_LEN`, so very long lines are truncated for display. Percent calculation divides by `strlen(buf)` and expects non-null text; an empty buffer can be risky. Scrolling is pointer-based, so newline accounting is important when preserving positions. Resize rebuilds and backs up by the old height.

## Test Signals

Test empty and long text, long single lines, vertical and horizontal scrolling, saved scroll restoration, jump-key callbacks, resize, ESC, first/last page, and terminal sizes near minimum.
