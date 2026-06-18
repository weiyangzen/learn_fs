# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/sysfs.h

Declares the sysfs attribute lists and operation tables implemented by `debug/sysfs.c`.

Key declarations:
- Attribute arrays: `bch2_fs_files`, `bch2_fs_counters_files`, `bch2_fs_internal_files`, `bch2_fs_opts_dir_files`, `bch2_fs_time_stats_files`, `bch2_fs_time_stats_json_files`, and `bch2_dev_files`.
- Sysfs ops: `bch2_fs_sysfs_ops`, counter/internal/options/time-stats variants, and `bch2_dev_sysfs_ops`.
- Binary attribute: `bin_attr_btree_trans_stats_json`.
- Helper: `bch2_opts_create_sysfs_files(struct kobject *, unsigned)`.

Core mechanics:
- The header exposes only Linux sysfs-facing objects, not implementation details.
- Consumers can attach the correct attribute arrays and `sysfs_ops` to kobjects for fs, internal, options, time stats, and device directories.

Filesystem relevance:
- This is the public registration contract for bcachefs sysfs debug/control files.
