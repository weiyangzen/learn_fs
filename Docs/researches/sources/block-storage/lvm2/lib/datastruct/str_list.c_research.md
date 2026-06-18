# File Research: sources/block-storage/lvm2/lib/datastruct/str_list.c

## Purpose
Implements small string-list utilities around `struct dm_list` and `struct dm_str_list`, using `dm_pool` allocation.

## Main APIs
- `str_list_create()` allocates and initializes a list head.
- `str_list_add()`, `str_list_add_no_dup_check()`, and `str_list_prepend_no_dup_check()` add string references.
- `str_list_add_list()` appends a list while skipping duplicates.
- `str_list_del()` removes all matching entries.
- `str_list_wipe()` unlinks all entries.
- `str_list_dup()` duplicates both list nodes and strings into a pool.
- `str_list_match_item()`, `str_list_match_list()`, and `str_list_lists_equal()` implement membership/set comparisons.
- `str_list_to_str()` joins list items with a delimiter.
- `str_to_str_list()` splits a string on a delimiter into pool-allocated list entries.

## Integration
Used widely for device aliases, WWID filtering, LV role/layout string lists, configuration-derived lists, and CLI/device selection state.

## Risk Notes
Most add functions store the provided string pointer without copying it; callers must ensure the string lifetime exceeds the list lifetime. Equality assumes no duplicate strings. `str_to_str_list()` can create empty string entries when delimiters are adjacent unless `ignore_multiple_delim` is set.
