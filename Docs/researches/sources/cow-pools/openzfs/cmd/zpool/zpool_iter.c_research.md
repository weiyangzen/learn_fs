# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_iter.c

This file implements command-side iteration helpers for pools and vdevs, plus the `zpool status/iostat -c` script execution framework.

Primary responsibilities:
- Maintains `zpool_list_t`, an AVL-backed ordered set of `zpool_handle_t` objects keyed by pool name.
- Provides high-level pool traversal via `for_each_pool()`.
- Provides vdev traversal via `for_each_vdev()`.
- Gathers per-vdev script output for `zpool status -c` / `zpool iostat -c`.

Important structures:
- `zpool_node_t`: wraps a pool handle, AVL node, and last-refresh timestamp.
- `zpool_list`: stores whether the list tracks all pools, whether property values are literal, an AVL tree, property-list expansion state, type, and refresh timestamp.
- `vdev_cmd_data_t` and `vdev_cmd_data_list_t` are declared in `zpool_util.h` and populated here.

Pool-list behavior:
- `pool_list_get()` creates the AVL tree and either:
  - iterates all pools with `zpool_iter()` when no CLI pool args are supplied, or
  - opens each named pool with `zpool_open_canfail()`.
- `add_pool()` inserts a pool into the AVL tree, expands properties with `zpool_expand_proplist()` when requested, and refreshes an existing node from a duplicate handle via `zpool_refresh_stats_from_handle()`.
- `pool_list_refresh()` supports two modes:
  - fixed explicit pool list: refreshes stats for existing handles only;
  - dynamic all-pools list: reruns `zpool_iter()`, adds new pools, refreshes old unavailable pools, and removes missing pools.
- `pool_list_iter()` skips unavailable pools unless the caller requests `unavail`.
- `for_each_pool()` is the simple wrapper used by most zpool subcommands.

Vdev iteration:
- `for_each_vdev()` fetches the pool config, looks up `ZPOOL_CONFIG_VDEV_TREE`, then delegates traversal to `for_each_vdev_cb()`.
- It intentionally ignores root vdevs and holes through the lower-level traversal helper.

Script execution path:
- `zpool_get_cmd_search_path()` uses `ZPOOL_SCRIPTS_PATH` if set, otherwise `$HOME/.zpool.d:<SYSCONFDIR>/zfs/zpool.d`, falling back to the system directory.
- `all_pools_for_each_vdev_run()` gathers vdevs across selected pools, runs requested comma-separated commands in parallel with a taskq, then builds a unique column list for display.
- `for_each_vdev_run_cb()` skips duplicate spare paths within the same pool, supports selected-vdev filtering by rendered vdev name, captures path, underlying path, pool name, command pointer, and enclosure sysfs path.
- `vdev_run_cmd_thread()` ignores command names containing `/`, searches executable scripts in the allowed search path, and runs the first match.
- `vdev_run_cmd()` constructs the script environment with `zpool_vdev_script_alloc_env()` and invokes `libzfs_run_process_get_stdout_nopath()`.
- `vdev_process_cmd_output()` accepts either `column=value` lines or a single unlabelled value. Duplicate column names are ignored. A line without a column terminates processing after adding the value.
- `process_unique_cmd_columns()` derives all unique script output columns and their display widths across all vdevs.
- `free_vdev_cmd_data_list()` frees all gathered strings, arrays, and per-vdev state.

Notable implementation details:
- AVL ordering uses `TREE_ISIGN(strcmp(pool-name))`.
- `add_pool_cb()` always returns 0 so `zpool_iter()` continues even on duplicate pools or property expansion failure.
- Dynamic refresh uses `zn_last_refresh` timestamps to distinguish newly refreshed handles from stale entries.
- Script dispatch parallelism scales to `5 * sysconf(_SC_NPROCESSORS_ONLN)`.
- Memory ownership is explicit: pool handles are closed by `pool_list_free()`, while script output strings are freed by `free_vdev_cmd_data_list()`.

Dependencies:
- `libzfs` for pool handles, configs, stats, and process execution helpers.
- `libzutil` / ZFS utility helpers for vdev script environment and path resolution.
- SPL-style AVL and taskq APIs.
- `zpool_util.h` for shared declarations.
