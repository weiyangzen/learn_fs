# File Research: sources/block-storage/util-linux/sys-utils/swapon-common.c

This file provides shared state and helpers for the `swapon`/swap tooling. It owns lazily parsed `libmnt_table` instances for fstab and active swaps, plus the global `struct libmnt_cache *mntcache` used for source/tag resolution.

`get_fstab()` allocates the fstab table once, installs `table_parser_errcb()`, attaches the global cache, and parses the requested fstab path. `get_swaps()` does the same for `/proc/swaps` through `mnt_table_parse_swaps()`. Parse errors are reported as warnings and ignored by returning `1` from the callback. `free_tables()` unreferences both cached tables.

The small query helpers are `match_swap()`, which delegates to `mnt_fs_is_swaparea()`, and `is_active_swap()`, which checks the cached swaps table for a source match in reverse iteration order. `cannot_find()` centralizes the warning and `-1` return used when a requested swap device or tag cannot be resolved.

The file also stores command-line `-L` label and `-U` UUID lists in growable arrays. `add_label()`, `get_label()`, `numof_labels()`, `add_uuid()`, `get_uuid()`, and `numof_uuids()` are intentionally minimal; they retain pointers to option arguments rather than duplicating strings.
