# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_util.h

This header is the shared interface for zpool command helper modules.

Main declarations:
- Memory/error helpers: `safe_malloc()`, `safe_realloc()`, `zpool_no_memory()`.
- Small utility helpers: `num_logs()`, `array64_max()`, `zpool_get_cmd_search_path()`.
- Vdev construction helpers:
  - `make_root_vdev()`
  - `split_mirror_vdev()`
- Pool iteration helpers:
  - `for_each_pool()`
  - opaque `zpool_list_t`
  - `pool_list_get()`, `pool_list_refresh()`, `pool_list_iter()`, `pool_list_free()`, `pool_list_count()`
- Vdev iteration:
  - `for_each_vdev()`
- Script execution result containers:
  - `vdev_cmd_data_t`
  - `vdev_cmd_data_list_t`
  - `all_pools_for_each_vdev_run()`
  - `free_vdev_cmd_data_list()`
- Device/file validation and platform helpers:
  - `check_device()`
  - `check_sector_size_database()`
  - `vdev_error()`
  - `check_file()`
  - `check_file_generic()`
  - `after_zpool_upgrade()`
- Power helpers:
  - `zpool_power()`
  - `zpool_power_current_state()`

Important constants:
- `ZPOOL_SCRIPTS_DIR` is `SYSCONFDIR"/zfs/zpool.d"`, the system script directory for `zpool status/iostat -c`.

Important data contracts:
- `vdev_cmd_data_t` stores script result lines and optional column names for one vdev, plus vdev path, underlying path, pool name, command backpointer, and enclosure sysfs path.
- `vdev_cmd_data_list_t` stores all per-vdev command data, optional selected-vdev filter state, unique column metadata, and display widths.

External state:
- Declares global `libzfs_handle_t *g_zfs`, used throughout zpool command modules.

Dependencies:
- `libnvpair.h`, `libzfs.h`, and `libzutil.h`.
- The header is C++ guarded.
