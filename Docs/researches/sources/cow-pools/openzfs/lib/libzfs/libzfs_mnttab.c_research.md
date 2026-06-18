# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_mnttab.c

## Scope

Maintains an optional libzfs-side cache of mounted ZFS filesystems from `MNTTAB`.

## APIs And Behavior

- `libzfs_mnttab_init()` initializes a mutex and AVL tree keyed by `mnt_special`.
- `libzfs_mnttab_fini()` frees cached entries and destroys the AVL/mutex.
- `libzfs_mnttab_cache()` toggles cache retention.
- `libzfs_mnttab_find()` reloads from `MNTTAB` when caching is disabled or the cache is empty, then looks up a dataset by `mnt_special`.
- `libzfs_mnttab_add()` and `libzfs_mnttab_remove()` update the cache only when caching is enabled.
- Duplicate mount entries are ignored while loading.

## State And Dependencies

The cache lives in `libzfs_handle_t` as `zh_mnttab`, guarded by `zh_mnttab_lock`. Each node stores duplicated special, mountpoint, and options strings and a constant ZFS fstype string.

## Risks And Invariants

When caching is disabled, add/remove are no-ops and find drops/rebuilds the AVL. Returned `struct mnttab` fields point into cached nodes, so their lifetime is tied to the cache entry and lock-protected mutation discipline.
