<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-debugfs.c

Purpose: Implements the debugfs surface for regmap instances. It creates `/sys/kernel/debug/regmap/<map>/` entries for driver name, register dumps, printable register ranges, access flags, and cache controls, giving developers a live inspection path into regmap-backed devices.

Important APIs/types/functions: `struct regmap_debugfs_node` tracks maps registered before the debugfs root exists. `regmap_debugfs_init()`, `regmap_debugfs_exit()`, and `regmap_debugfs_initcall()` own lifecycle. `regmap_read_debugfs()` formats register/value dumps, while `regmap_debugfs_get_dump_start()` and `regmap_next_readable_reg()` map file offsets to sparse printable registers. `regmap_access_show()` exposes readable/writeable/volatile/precious flags. Cache controls are implemented by `regmap_cache_only_write_file()` and `regmap_cache_bypass_write_file()`.

Control flow: initialization defers maps into `regmap_debugfs_early_list` until the root directory is created. For active maps, the code builds a directory name from device/name or a dummy ID, registers debugfs files, adds range-specific files from `map->range_tree`, and delegates to cache backend debugfs hooks. Reads clamp allocation to `PAGE_SIZE << MAX_PAGE_ORDER`, build or reuse an offset cache, skip precious/unreadable/uncached registers, call `regmap_read()`, and copy formatted text to userspace. Cache toggles parse booleans, mutate regmap state under `map->lock`, and may trigger `regcache_sync()`.

State and persistence behavior: Debugfs state is runtime-only. Persistent state lives in `map->debugfs_name`, `map->debugfs_dummy_id`, `map->debugfs_off_cache`, and boolean cache flags. The offset cache persists across debugfs reads until `regmap_debugfs_exit()` frees it. The early list persists only until `regmap_debugfs_initcall()` drains it.

Dependencies and integration points: Depends on debugfs, IDA, list/mutex primitives, uaccess helpers, `regmap_readable()`, `regmap_writeable()`, `regmap_volatile()`, `regmap_precious()`, `regmap_cached()`, and regcache APIs. Integrates with regmap core lifecycle and cache backend-specific debugfs initialization.

Risks: Debugfs reads can perform live hardware reads and affect timing-sensitive devices. Write support and forced field writes are intentionally hidden behind source edits because they can taint the kernel and alter hardware behind drivers. Offset-cache correctness depends on stable readable/cache policy and `debugfs_tot_len`. Cache-only disable can initiate a sync from debugfs and expose device errors. Debugfs is skipped when map locking is disabled to avoid races.

Test signals: No direct test file here, but observable signals include debugfs file creation/removal, sparse register range output, skipped precious registers, cache-only/cache-bypass transitions, dummy ID cleanup, and successful early-list replay after root creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-debugfs.c -->
