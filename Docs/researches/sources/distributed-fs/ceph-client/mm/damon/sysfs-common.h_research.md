# sources/distributed-fs/ceph-client/mm/damon/sysfs-common.h

Purpose: Declares shared types and entry points used by DAMON sysfs implementation files.

Important APIs and types: Declares global `damon_sysfs_lock`, `struct damon_sysfs_ul_range`, allocation/release functions, and `damon_sysfs_ul_range_ktype`. Declares `struct damon_sysfs_schemes` and scheme-management APIs such as `damon_sysfs_schemes_alloc()`, `damon_sysfs_add_schemes()`, stats updates, region population, region clearing, quota-score setting, and effective-quota updates.

Control flow: This header lets `sysfs.c`, `sysfs-schemes.c`, and common helpers share kobject types and convert sysfs model objects into DAMON runtime schemes.

State and persistence: No direct state, but declared structs own sysfs kobjects and arrays of scheme objects while the sysfs tree exists.

Dependencies and integration: Includes `linux/damon.h` and `linux/kobject.h`. Integrates common sysfs pieces with DAMON core contexts and scheme stats.

Risks: The header exposes cross-file contracts for sysfs scheme arrays and kobject lifetime. Mismatched ownership between allocation, directory removal, and kobject release can cause leaks or use-after-free in sysfs code.

Test signals: Compile full `DAMON_SYSFS`, run sysfs KUnit tests, exercise scheme creation/removal, stats update, quota score updates, and region-population paths.
