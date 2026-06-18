<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.c

## Purpose
`sysfs.c` implements bcache sysfs objects for cached devices, flash volumes, cache sets, cache-set internals, and cache devices. It maps attribute reads to status/statistics and writes to configuration changes, metadata persistence, attach/detach, GC, pruning, writeback tuning, and stop/unregister actions.

## Important APIs, Types, And Functions
Attribute declarations use `sysfs.h` macros. `__bch_cached_dev_show()`, `__cached_dev_store()`, and `bch_cached_dev_store()` handle backing-device cache modes, writeback parameters, labels, I/O disable, running, attach, detach, and stop. `bch_flash_dev_show()` and `__bch_flash_dev_store()` handle flash volume size, label, and unregister. Cache-set helpers compute bset stats, root usage, btree cache size, chain length, used percentage, and average key size. `__bch_cache_set_show/store()` and `__bch_cache_show/store()` expose cache-set controls and per-cache stats/policy.

## Control Flow
Generated show/store methods dispatch by comparing `attr` pointers. Locked variants hold `bch_register_lock`. Reads format values with `sysfs_emit()` and `bch_hprint()`. Writes reject reboot-time access, parse and clamp input, update fields, and persist selected changes with `bch_write_bdev_super()`, `bcache_write_super()`, or `bch_uuid_write()`. Writeback toggles wake the kthread and schedule delayed rate work when the device is attached.

## State And Persistence
Persistent writes include cache mode, cached-device label, synchronous bit, replacement policy, flash volume size/label, and UUID labels. Runtime-only state includes counters, `io_disable`, debug booleans, congestion thresholds, GC/prune controls, and most writeback controller tunables.

## Dependencies, Integration Points, Risks, And Test Signals
It integrates with bcache lifecycle code in `super.c`, writeback scheduling in `writeback.c`, btree statistics, request/accounting/debug helpers, feature printers, GC, and shrinkers. Risks include pointer-dispatch no-ops, metadata write failures, global lock interactions with stop/detach, fixed-size label handling, and threshold clamp ordering. Test all attributes with valid/invalid input, reboot rejection, UUID attach parsing, writeback clamp behavior, flash volume updates, GC/prune actions, error action switching, and kobject default groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.c -->
