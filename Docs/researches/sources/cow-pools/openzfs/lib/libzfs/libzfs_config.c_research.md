# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_config.c

This file manages libzfs’s in-memory view of pool configuration namespace and exposes pool/root iteration helpers.

Primary concept:
- Pool configuration is stored kernel-side and mirrored from `/etc/zfs/zpool.cache`.
- Userland obtains it through `ZFS_IOC_POOL_CONFIGS`, which also works from local zones.

Important structure:
- `config_node_t`: AVL node containing pool name and duplicated pool config nvlist.

Namespace lifecycle:
- `namespace_reload()` initializes the namespace AVL on first use.
- It sends `ZFS_IOC_POOL_CONFIGS` with the handle’s generation counter.
- `EEXIST` means the namespace generation has not changed.
- `ENOMEM` expands the destination nvlist buffer and retries.
- On success, it updates `libzfs_ns_gen`, clears existing config nodes, reads the returned packed nvlist, duplicates each pool config, and inserts it into the AVL.
- `namespace_clear()` frees all configs, names, nodes, and destroys the AVL.

Pool config/stat helpers:
- `zpool_get_config()` returns the current config and optionally the old config pointer.
- `zpool_get_features()` ensures feature stats are present, refreshing pool stats if needed, then returns `ZPOOL_CONFIG_FEATURE_STATS`.
- `zpool_refresh_stats()` sends `ZFS_IOC_POOL_STATS`, expanding the buffer on `ENOMEM`. It updates:
  - old config pointer;
  - current config;
  - config buffer size;
  - pool state active/unavailable.
- Missing/destroyed pools are detected through `ENOENT` or `EINVAL` and reported via the `missing` output flag.
- `zpool_refresh_stats_from_handle()` copies config/state from a source pool handle to a destination handle for the same pool, avoiding a duplicate kernel round trip.

Pool filtering:
- `zpool_skip_pool()` reads undocumented test-only environment variables once:
  - `__ZFS_POOL_EXCLUDE`: space-separated pools to skip.
  - `__ZFS_POOL_RESTRICT`: space-separated allowlist.
- Exclude wins first; restrict skips all non-listed pools.

Iteration:
- `zpool_iter()` reloads namespace unless already inside a pool iteration. This avoids invalidating parent iterator state during recursive calls.
- It opens each pool silently and passes the handle to the callback.
- Callback ownership follows zpool iterator convention: callbacks receive handles and are expected to close or transfer as appropriate based on callee behavior.
- `zfs_iter_root()` reloads namespace and creates root dataset handles for each pool, passing each to the callback, which must close the handle.

Dependencies:
- ioctl helpers from libzfs internals (`zcmd_alloc_dst_nvlist`, `zcmd_expand_dst_nvlist`, `zcmd_read_dst_nvlist`).
- AVL tree for sorted pool namespace.
- nvlist duplication/free APIs.
