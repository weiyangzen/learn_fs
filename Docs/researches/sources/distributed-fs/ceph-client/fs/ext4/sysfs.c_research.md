# sources/distributed-fs/ceph-client/fs/ext4/sysfs.c

## Purpose
`sysfs.c` exposes ext4 per-filesystem runtime controls and counters under `/sys/fs/ext4/<sb-id>/`, exposes supported feature flags under `/sys/fs/ext4/features/`, and creates procfs diagnostic files under `/proc/fs/ext4/<sb-id>/`. It is the observability and live-tuning companion to the superblock state initialized in `super.c`.

## Important APIs, Types, And Functions
`struct ext4_attr` wraps a sysfs `attribute` with an `attr_id_t`, pointer mode, size, and either an explicit pointer or offset into `struct ext4_sb_info` / `struct ext4_super_block`. The macro family `EXT4_ATTR*`, `EXT4_RO_ATTR_ES_*`, and `EXT4_RW_ATTR_SBI_*` defines attributes compactly. `calc_ptr()` resolves offset-based attributes.

Read paths use `ext4_attr_show()` and `ext4_generic_attr_show()`. Write paths use `ext4_attr_store()` and `ext4_generic_attr_store()`. Specialized stores include `inode_readahead_blks_store()`, `reserved_clusters_store()`, `trigger_test_error()`, and `err_report_sec_store()`. Registration functions are `ext4_init_sysfs()`, `ext4_exit_sysfs()`, `ext4_register_sysfs()`, `ext4_unregister_sysfs()`, and `ext4_notify_error_sysfs()`.

## Control Flow
Module init calls `ext4_init_sysfs()`, which creates `/sys/fs/ext4`, allocates and registers the global `features` kobject, and creates `/proc/fs/ext4`. After a filesystem mount is fully initialized, `ext4_register_sysfs()` initializes the per-superblock completion, adds the superblock kobject under the ext4 root, and creates proc entries for options, extent-status shrinker info, fast-commit info, mballoc group data, and mballoc stats. Unmount calls `ext4_unregister_sysfs()` before journal destruction and before flushing delayed superblock update work.

Sysfs reads switch on `attr_id`. Some values are live counters from per-cpu or atomic state, some derive from block-device write statistics, some read little-endian on-disk superblock fields, and feature attributes simply report support. Writes parse integer text with `kstrto*`, validate bounds, and update in-memory fields or trigger controlled side effects.

## State And Persistence Behavior
Most writable attributes mutate only in-memory `ext4_sb_info` tuning knobs such as allocator scan limits, inode readahead, reserved clusters, ratelimit settings, trim minimums, and superblock update intervals. Attributes pointing into `struct ext4_super_block` display persisted error metadata and identifiers but are generally read-only in this file. `err_report_sec` controls a timer in `sbi` and can start, reschedule, or delete periodic error reporting. `trigger_fs_error` deliberately injects an ext4 error and can update persistent error state through the normal error pipeline.

## Dependencies And Integration Points
The file depends on Linux kobjects/sysfs, procfs, seq_file, block partition statistics, ext4 mballoc proc seq ops, fast-commit proc output, extent-status shrinker diagnostics, error reporting from `super.c`, and timer callback `print_daily_error_info()`. It uses `s_error_notify_mutex` to coordinate `sysfs_notify()` with kobject add/delete.

## Risks And Edge Cases
Pointer-offset attributes require exact type matching; a wrong `attr_id` or offset would cause malformed reads/writes. Writable allocator and ratelimit knobs can affect performance or error visibility immediately. `trigger_fs_error` is gated by `CAP_SYS_ADMIN`, but it intentionally drives filesystem error handling and can force read-only behavior depending on mount options. `reserved_clusters_store()` rejects values greater than or equal to total clusters and negative signed interpretations. `err_report_sec_store()` caps intervals to one year and must avoid timer races during unmount.

## Test Signals
Tests should verify sysfs and proc entries appear after mount and disappear safely on unmount, including concurrent reads of `journal_task` during journal teardown. Attribute tests should cover parsing, invalid bounds, feature presence under different kernel configs, error counter notification, timer enable/disable/reschedule, reserved cluster changes reflected in `statfs`, and proc outputs for options, mballoc, extent-status, and fast-commit state.
