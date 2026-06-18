# File Research: sources/block-storage/lvm2/lib/device/dev_util.c

## Purpose
Provides small list utility functions for LVM device lists. It contains no device I/O or scanning logic; it manipulates `dm_list` containers that hold `struct device_list` or `struct device_id_list` entries.

## Main Functions
- `device_id_list_remove` removes the first `device_id_list` entry whose `dev` pointer matches.
- `device_id_list_find_dev` returns the matching `device_id_list` entry.
- `device_list_remove` removes the first `device_list` entry whose `dev` pointer matches.
- `device_list_find_dev` returns the matching `device_list` entry.
- `device_list_add` allocates a `struct device_list` from a `dm_pool`, assigns `dev`, and appends it to the list.

## Dependencies
Uses `dm_list` iteration macros, `dm_pool_alloc`, and the list wrapper structs from `device.h`.

## Risk Notes
Matching is pointer identity, not dev_t or path equality. Callers must ensure that the compared `struct device *` values come from the same dev-cache/device object universe.
