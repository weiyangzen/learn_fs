# File Research: sources/cow-pools/bcachefs-tools/fs/debug/sysfs.c

## Purpose

Implements bcachefs sysfs attribute handlers for filesystem-wide state, internal debug state, counters, time stats, filesystem options, per-device state, and debug/test triggers. It is a glue layer: most attributes dispatch into allocator, btree, journal, recovery, compression, counter, device, and dirent helpers.

## Main Interfaces

- `bch2_fs_sysfs_ops`, `bch2_fs_counters_sysfs_ops`, `bch2_fs_internal_sysfs_ops`, `bch2_fs_opts_dir_sysfs_ops`, `bch2_fs_time_stats_sysfs_ops`, `bch2_fs_time_stats_json_sysfs_ops`, `bch2_dev_sysfs_ops`.
- Attribute arrays exported for kobject setup: `bch2_fs_files`, `bch2_fs_counters_files`, `bch2_fs_internal_files`, `bch2_fs_opts_dir_files`, `bch2_fs_time_stats_files`, `bch2_fs_time_stats_json_files`, `bch2_dev_files`.
- Binary sysfs attribute `bin_attr_btree_trans_stats_json`.
- `bch2_opts_create_sysfs_files()` dynamically creates option attributes for filesystem or device scopes.

## Behavior

`SHOW()` and `STORE()` macros wrap text conversion and parsing into sysfs-compatible callbacks, normalize errors through `bch2_err_class()`, and cap show output to a page. The filesystem show path exposes selected public attributes plus internal diagnostics such as journal state, btree caches, open buckets, discards, replicas, disk groups, moving contexts, recent counters, and filldir64 specialization.

The filesystem store path handles debug triggers: GC, discards, invalidates, journal commits/flushes/writes, btree cache shrinkers, write buffer flush, freelist wakeup, capacity recalculation, reconcile wakeups, snapshot deletion, emergency read-only, and optional `perf_test`. Most write actions require the filesystem to be started; mutating triggers use `enumerated_ref_tryget(&c->writes, BCH_WRITE_REF_sysfs)` to reject read-only state.

Option show/store maps sysfs filenames to `bch2_opt_table` entries. Device-backed options are intentionally not duplicated at FS scope when an FS/device option would alias ambiguously. Option writes parse text, take write refs and option-change locking, update superblock/member-backed or runtime options, and run pre/post hooks.

The JSON btree transaction stats bin attribute caches multi-page JSON under a mutex and regenerates only at offset zero to avoid inconsistent reads across kernfs chunks.

## State And Side Effects

This file mutates global filesystem/device runtime state through sysfs writes: journal flushing, GC scheduling, discard/invalidate work, counters, time-stat resets, device labels, IO error resets, and mount/device options. Per-device show handlers expose UUIDs, bucket ranges, group labels, device data types, IO counters/errors, latency stats, congestion, alloc debug, open buckets, discard state, and read/write refs.

## Dependencies

Depends broadly on bcachefs core modules: alloc, btree, data movement/compression/reconcile, fs dirent/inode, journal, init/recovery, superblock counters/errors/io, enumerated refs, Linux sysfs, blockdev, sorting, and scheduler clock. `CONFIG_BCACHEFS_TESTS` adds the `perf_test` attribute, and latency accounting gates `congested`.

## Risks And Notes

The file is intentionally privileged and sharp-edged: sysfs writes can force major maintenance work or emergency read-only. Error class conversion matters because many internal bcachefs errors have custom classes. The option scope filtering for mixed FS/device options prevents silent no-op writes and ambiguous reads. The transaction stats JSON cache is important for correctness with multi-page sysfs bin reads.
