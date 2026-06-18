# sources/distributed-fs/ceph-client/mm/damon/sysfs-common.c

Purpose: Provides shared sysfs support for DAMON, currently the reusable unsigned-long range kobject and global DAMON sysfs mutex.

Important APIs, types, and functions: Defines `damon_sysfs_lock`. `damon_sysfs_ul_range_alloc()` allocates and initializes a `struct damon_sysfs_ul_range`. `min_show()/min_store()` and `max_show()/max_store()` expose writable range endpoints. `damon_sysfs_ul_range_release()` frees the object. `damon_sysfs_ul_range_ktype` wires release, sysfs ops, and default attributes.

Control flow: Higher-level sysfs code allocates a range, registers its kobject with `damon_sysfs_ul_range_ktype`, and userspace reads/writes `min` and `max`. Store handlers parse unsigned longs with `kstrtoul()` and update the object directly.

State and persistence: Each range object stores `min` and `max` in memory; values persist only while the sysfs object exists. `damon_sysfs_lock` is global coordination state used across the sysfs DAMON implementation.

Dependencies and integration: Depends on `sysfs-common.h`, kobject/sysfs APIs, and slab allocation. Other DAMON sysfs files reference additional declarations in the header for schemes and stats.

Risks: This common range object does not enforce `min <= max`; callers must validate semantics before committing to DAMON contexts. Store updates are simple assignments and rely on external locking/serialization when needed.

Test signals: Create range kobjects through DAMON sysfs paths, read/write numeric endpoints, verify parse failures return errors, and check object release with kobject lifetime tests.
