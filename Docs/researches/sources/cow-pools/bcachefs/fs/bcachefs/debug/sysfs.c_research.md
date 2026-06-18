# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/sysfs.c

Implements bcachefs sysfs/debug interfaces for filesystem objects, internal debug state, counters, options, time stats, transaction stats JSON, and per-device status/settings.

Key entry points:
- `bch2_fs_show()` / `bch2_fs_store()` expose top-level filesystem attributes and trigger manual maintenance/debug actions.
- `bch2_fs_counters_show()` reports persistent counters since mount and since filesystem creation.
- `bch2_fs_internal_show()` / `bch2_fs_internal_store()` wrap the main fs handlers for the internal sysfs directory.
- `bch2_btree_trans_stats_json_read()` / `bch2_btree_trans_stats_json_write()` expose/reset btree transaction timing and memory stats as a binary JSON attribute.
- `sysfs_opt_show()` / `sysfs_opt_store()` implement generic fs/device option read/write handling through `bch2_opt_table`.
- `bch2_opts_create_sysfs_files()` creates sysfs files for visible options by option type.
- `bch2_fs_time_stats_show()` / JSON variant expose/reset `BCH_TIME_STATS()`.
- `bch2_dev_show()` / `bch2_dev_store()` expose per-device UUID, bucket ranges, labels, data classes, IO counters/errors, latency stats, allocation debug, discards, refs, and device options.

Core mechanics:
- Local macros generate sysfs attributes and `sysfs_ops`, normalize show output through `printbuf`, and map bcachefs-specific errors back to class errno values with `bch2_err_class()`.
- Write-only trigger attributes call GC, discard, invalidate, journal, btree cache shrink, write-buffer flush, reconcile, snapshot cleanup, capacity recalculation, and emergency read-only paths.
- Mutating fs triggers acquire `BCH_WRITE_REF_sysfs` to reject read-only state cleanly.
- Option writes parse text, take option-change locking, run pre/post hooks, update superblock-backed or runtime fs options, and clear mount-option override bits when appropriate.
- Transaction stats JSON is cached across kernfs chunked reads so one user read sees consistent JSON even when output exceeds one page.
- Device sysfs paths reuse the same option helpers with a `struct bch_dev *` when an option is per-device.

Important invariants:
- Sysfs show handlers must fit the copied result to `PAGE_SIZE - 1`.
- Internal trigger writes require the filesystem to be started.
- FS-level sysfs files skip options that are also device/member options to avoid ambiguous or no-op FS writes.
- Option changes must run under `PF_MEMALLOC_NOFS`, option-change locking, and opt-change hook scope.
- JSON transaction stats reads regenerate only at offset zero.

Filesystem relevance:
- This is the operator-facing diagnostics and control surface for bcachefs runtime state. It bridges core allocator, btree, journal, GC, counters, latency, and device subsystems into sysfs.

Notable risks:
- Several sysfs writes invoke powerful maintenance or emergency paths and rely on sysfs permissions plus started/read-only checks.
- Generic option exposure must keep option flags correct, or a device-only option could be exposed at the wrong scope.
- Cached JSON output correctness depends on offset-zero read sequencing and the shared stats lock.
