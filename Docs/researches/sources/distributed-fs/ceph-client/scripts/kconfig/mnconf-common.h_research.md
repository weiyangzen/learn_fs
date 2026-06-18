# sources/distributed-fs/ceph-client/scripts/kconfig/mnconf-common.h

## Purpose

`mnconf-common.h` declares shared data and functions for ncurses frontend search jump-key support.

## Important APIs, Types, and Functions

It defines `struct search_data` with a jump-entry list head and selected target menu pointer. It declares `jump_key_char`, `next_jump_key()`, `handle_search_keys()`, and `get_jump_key_char()`.

## Control Flow

No flow is implemented in the header. It gives `mconf.c`, `mnconf-common.c`, and menu help generation a common contract for numbered search-result navigation.

## State and Persistence Behavior

The header exposes only process-global jump-key state. It has no persistence.

## Dependencies and Integration Points

It includes `stddef.h` and `list_types.h`, and forward-uses `struct menu` through the pointer in `struct search_data`. It is included by `mconf.c` and `mnconf-common.c`.

## Risks and Edge Cases

Any change to `struct search_data` must be coordinated with the textbox callback and search-result generation. The global jump-key counter remains non-reentrant.

## Test Signals

Compile coverage and menuconfig search/jump behavior are sufficient signals for this small header.
