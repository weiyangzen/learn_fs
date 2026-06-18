<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mbcache.h -->
# sources/distributed-fs/ceph-client/include/linux/mbcache.h

## Purpose
This header defines the metadata block cache interface used by filesystems to cache keyed reusable entries with refcounted hash/list membership.

## Important APIs, types, and functions
`struct mb_cache_entry` contains list and hash nodes, `e_refcnt`, `e_key`, flags `MBE_REFERENCED_B` and `MBE_REUSABLE_B`, and user `e_value`. APIs include `mb_cache_create`, `mb_cache_destroy`, `mb_cache_entry_create`, `mb_cache_entry_put`, `mb_cache_entry_delete_or_get`, `mb_cache_entry_get`, `mb_cache_entry_find_first`, `mb_cache_entry_find_next`, `mb_cache_entry_touch`, `mb_cache_entry_wait_unused`, and internal free helper `__mb_cache_entry_free`.

## Control flow
Filesystems create a cache with a bucket count, insert keyed values, look up entries by key/value, iterate matching entries, touch entries for replacement policy, and put references when done. `mb_cache_entry_put()` decrements the refcount, wakes waiters for low counts, and frees when the count reaches zero.

## State and persistence
State is in-memory only: hash membership, cache list ordering, flags, refcounts, keys, and values. Entries are guaranteed hashed while refcounted.

## Dependencies and integration points
It uses hash helpers, bit-locked hlist nodes, lists, atomics, and filesystem types. Ext-family filesystems are typical consumers.

## Risks and test signals
Risks include refcount underflow, delete races with active references, waiting for unused entries while new users acquire references, and reusable flag policy mistakes. Test create/destroy, duplicate key/value handling, concurrent get/delete/put, low-refcount wakeups, and iteration with removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mbcache.h -->
