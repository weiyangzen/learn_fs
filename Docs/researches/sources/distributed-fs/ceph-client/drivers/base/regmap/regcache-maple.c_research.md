# sources/distributed-fs/ceph-client/drivers/base/regmap/regcache-maple.c

## Purpose
This file implements a maple-tree based regcache backend. It stores contiguous cached register ranges as dynamically allocated arrays indexed by maple tree ranges, improving sparse/fragmented cache behavior while supporting range sync and drop.

## Important APIs, Types, And Functions
Backend hooks include `regcache_maple_init()`, `regcache_maple_exit()`, `regcache_maple_populate()`, `regcache_maple_read()`, `regcache_maple_write()`, `regcache_maple_drop()`, and `regcache_maple_sync()`. Helper functions include `regcache_maple_insert_block()` and `regcache_maple_sync_block()`. The backend descriptor is `regcache_maple_ops`.

## Control Flow And State
Reads use an RCU read-side maple lookup and return `-ENOENT` when no range contains the register. Writes update an existing range or search adjacent lower/upper ranges, allocate a merged array spanning `index..last`, store the range under maple-tree lock, and free replaced arrays. Drops iterate intersecting entries, optionally preserve lower/upper fragments outside the drop interval, erase the old node, and store preserved fragments. Population groups contiguous default registers into one maple range per block. Sync scans cached ranges and emits only contiguous subranges whose values need sync, using raw writes when beneficial.

## Dependencies And Integration Points
The backend depends on `linux/maple_tree.h`, RCU read sections, regmap locking as the outer serializer, `_regmap_write()`, `_regmap_raw_write()`, `regcache_reg_needs_sync()`, and value formatting helpers.

## Risks And Test Signals
Risks include off-by-one range lengths, RCU/lifetime mistakes when freeing replaced arrays, false sharing between maple locks and regmap locks, raw-write length errors, and fragmentation during repeated drop/write cycles. Test signals include sparse write/read/merge/drop tests, lockdep with maple tree locking, raw vs single sync behavior, allocation-failure injection, and cache sync after reset with default skipping.
