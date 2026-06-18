# sources/distributed-fs/ceph-client/scripts/kconfig/mnconf-common.c

## Purpose

`mnconf-common.c` provides shared search-result jump-key handling for menuconfig-style ncurses frontends.

## Important APIs, Types, and Functions

It defines global `jump_key_char` and implements `next_jump_key()`, `handle_search_keys()`, and `get_jump_key_char()`. It consumes `struct search_data` and `struct jump_key` lists.

## Control Flow

`get_jump_key_char()` cycles jump labels through `1` to `9`. `handle_search_keys()` receives a pressed key plus the visible text range from `dialog_textbox()`, scans jump entries whose offsets are visible, and when the key matches the visible ordinal it stores the target menu and returns 1 to close the textbox for navigation.

## State and Persistence Behavior

Only `jump_key_char` persists between calls; `mconf` resets it before rendering search results. No files are read or written.

## Dependencies and Integration Points

It depends on list iteration from `list.h`, expression/menu types from `expr.h`, and declarations in `mnconf-common.h`. `menu.c` calls weak/overridden `get_jump_key_char()` during relation-string generation, while `mconf.c` uses `handle_search_keys()` as a textbox callback.

## Risks and Edge Cases

Only nine jump keys are available per visible page. Offsets must match the generated `gstr` exactly; changes in help formatting can affect jump behavior. The implementation assumes callers reset `jump_key_char` at appropriate boundaries.

## Test Signals

Search results with more than nine matches, scrolled results, hidden/non-visible offsets, repeated searches, and jump-to-location behavior from `mconf` validate this file.
