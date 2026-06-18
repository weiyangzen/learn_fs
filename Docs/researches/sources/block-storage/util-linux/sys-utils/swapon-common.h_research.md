# File Research: sources/block-storage/util-linux/sys-utils/swapon-common.h

This header exposes the shared swap helper API implemented by `swapon-common.c`. It includes `libmount.h`, declares the global `mntcache`, and publishes table accessors for fstab and active swaps.

The exported functions cover three responsibilities: table lifecycle and parsing (`get_fstab()`, `get_swaps()`, `free_tables()`), swap matching/resolution diagnostics (`match_swap()`, `is_active_swap()`, `cannot_find()`), and retained command-line tag lists for labels and UUIDs.

It is a narrow internal header for util-linux swap commands, not a public libmount interface. The declarations make the cache/table/tag-list state available to `swapon.c` while keeping storage private to `swapon-common.c`.
