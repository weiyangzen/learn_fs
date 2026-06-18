# sources/distributed-fs/lustre-release/lustre/llite/lproc_llite.c

## Purpose

`lproc_llite.c` implements the Lustre llite client's sysfs and debugfs observability and tuning surface. It creates the global `llite` kobject/debugfs root, registers one kset/debugfs directory per mounted Lustre client, exposes read-only capacity attributes, exposes writable runtime tunables, wires `lprocfs` counters for VFS/client operations, and implements optional read/write histogram collection for I/O extents and offsets.

The file is not on the data path in the same way as `file.c` or `namei.c`, but many attributes directly affect data-path behavior through `struct ll_sb_info`, `struct cl_client_cache`, readahead state, PCC settings, root-squash policy, statfs caching, xattr caching, encryption-name compatibility, and open-cache thresholds.

## Important APIs, types, and functions

Global registration:

- `llite_tunables_register()` allocates `llite_kobj`, adds `/sys/fs/lustre/llite` under `lustre_kset`, and creates `<debugfs>/lustre/llite`.
- `llite_tunables_unregister()` drops the global kobject; `llite_kobj_release()` removes `llite_root` and frees the kobject.
- `ll_debugfs_register_super(struct super_block *sb, const char *name)` registers a per-mount kset under the global llite kobject, creates the mount debugfs directory, installs debugfs files, allocates operation and readahead stats, and initializes all counters.
- `ll_debugfs_unregister_super(struct super_block *sb)` removes debugfs entries, removes sysfs links to MDT/OST OBDs when present, unregisters the kset, waits for `ll_kobj_unregister`, and frees stats.

Sysfs/debugfs attribute helpers:

- `ll_stats_pid_write()` parses enable/disable writes for stats files. Numeric strings return their value; `0` or `disable` disables; other nonzero writes enable.
- `LUSTRE_RO_ATTR`, `LUSTRE_RW_ATTR`, `LUSTRE_WO_ATTR`, `LUSTRE_ATTR`, and `LDEBUGFS_SEQ_FOPS*` bind show/store or seq handlers into Lustre's sysfs/debugfs operation tables.
- `llite_attrs[]` is the authoritative per-mount sysfs attribute list; `lprocfs_llite_obd_vars[]` is the debugfs variable list.

Capacity and identity attributes:

- `blocksize_show`, `kbytestotal_show`, `kbytesfree_show`, `kbytesavail_show`, `filestotal_show`, `filesfree_show`, `maxbytes_show`, and `statfs_state_show` call `ll_statfs_internal(..., OBD_STATFS_NODELAY)` and format values for sysfs.
- `stat_blocksize_show/store` reads or sets `sbi->ll_stat_blksize`, validating that nonzero values are powers of two and at least `PAGE_SIZE`.
- `namelen_max_show/store` exposes `sbi->ll_namelen`, checks the value against a local minimum, `NAME_MAX`, and the MDT-provided `osfs.os_namelen`.
- `client_type_show`, `fstype_show`, and `uuid_show` report static or mount identity information.

Readahead and page cache tunables:

- `max_read_ahead_mb_show/store`, `max_read_ahead_per_file_mb_show/store`, and `max_read_ahead_whole_mb_show/store` adjust `sbi->ll_ra_info` limits using memory parsers and total-RAM caps.
- `max_read_ahead_async_active_show/store`, `read_ahead_async_file_threshold_mb_show/store`, and `read_ahead_range_kb_show/store` control async and mmap-range readahead behavior.
- `ll_max_cached_mb_seq_show/write` exposes and changes `cl_client_cache.ccc_lru_max`, using `ccc_lru_left` when growing or asking OSCs to shrink cache via `obd_set_info_async(KEY_CACHE_LRU_SHRINK)` when shrinking.
- `ll_unevict_cached_mb_seq_show/write` reports unevictable cache use and accepts only `clear`, forwarding `KEY_UNEVICT_CACHE_SHRINK` to OSCs.
- `ll_enable_mlock_pages_seq_show/write` toggles `ccc_mlock_pages_enable`.

Feature toggles and per-mount policy:

- `checksums_show/store` toggles `LL_SBI_CHECKSUM` and propagates `KEY_CHECKSUM` to the data export.
- `lazystatfs_show/store`, `statfs_max_age_show/store`, and `statfs_project_show/store` tune statfs behavior.
- `xattr_cache_show/store`, `intent_mkdir_show/store`, `tiny_write_show/store`, `enable_erasure_coding_show/store`, `unaligned_dio_show/store`, `parallel_dio_show/store`, `hybrid_io_show/store`, `fast_read_show/store`, `file_heat_show/store`, `inode_cache_show/store`, and `dir_read_on_open_show/store` expose booleans or numeric knobs mapped into `ll_sb_info` fields or `ll_flags`.
- `enable_setstripe_gid_show/store` controls the GID allowed to use setstripe behavior, with `MDT_INVALID_GID` shown as `-1`.
- `hybrid_io_write_threshold_bytes_show/store` and `hybrid_io_read_threshold_bytes_show/store` parse byte-sized thresholds and cap them at `HYBRID_IO_THRESHOLD_BYTES_MAX`.
- `opencache_threshold_count_show/store`, `opencache_threshold_ms_show/store`, and `opencache_max_ms_show/store` tune open-cache thresholds used by name/open paths.

Statahead and AGL:

- `enable_statahead_fname_show/store`, `statahead_running_max_show/store`, `statahead_batch_max_show/store`, `statahead_max_show/store`, `statahead_min_show/store`, `statahead_timeout_show/store`, `statahead_fname_predict_hit_show/store`, `statahead_fname_match_hit_show/store`, and `statahead_agl_show/store` tune filename statahead and AGL limits/counters.
- `ll_statahead_stats_seq_show/write` prints and resets atomic statahead counters.

PCC and foreign symlink integration:

- `pcc_async_threshold_show/store`, `pcc_async_affinity_show/store`, and `pcc_mode_show/store` expose `struct pcc_super` policy.
- `ll_pcc_seq_show/write` dumps PCC state or passes commands into `pcc_cmd_handle()` after checking `OBD_CONNECT2_PCC`.
- `foreign_symlink_enable`, `foreign_symlink_prefix`, `foreign_symlink_upcall`, and `foreign_symlink_upcall_info` are declared as Lustre attributes here and implemented through the common attribute plumbing.

Security, rootsquash, and encryption compatibility:

- `ll_root_squash_seq_show/write` exposes the root squash UID/GID and delegates parsing to `lprocfs_wr_root_squash()`.
- `ll_nosquash_nids_seq_show/write` shows and updates no-squash NID lists, then recomputes root-squash state.
- `enable_filename_encryption_show/store` toggles `LSI_FILENAME_ENC` when built with `CONFIG_LL_ENCRYPTION`, refusing enable if the server lacks name-encryption support.
- `filename_enc_use_old_base64_show/store` toggles old base64 filename encoding compatibility when encryption support is compiled in.

Stats and histograms:

- `llite_opcode_table[]` maps every `LPROC_LL_*` counter to a name and counter type. It covers byte counters, latency counters, request counters, PCC counters, hybrid-IO counters, and VFS metadata operation counters.
- `ll_stats_ops_tally()` is exported and conditionally increments `sbi->ll_stats` depending on `ll_stats_track_type` and `ll_stats_track_id`.
- `ra_stat_string[]` names readahead counters allocated in `ll_debugfs_register_super()`.
- `alloc_rw_stats_info()` lazily allocates `ll_rw_extents_info`, `ll_rw_process_info`, and `ll_rw_offset_info`.
- `ll_free_rw_stats_info()` releases those optional histogram structures.
- `ll_rw_extents_stats_seq_show/write`, `ll_rw_extents_stats_pp_seq_show/write`, `ll_rw_offset_stats_seq_show/write`, `ll_display_extents_info()`, and `ll_rw_stats_tally()` implement the optional I/O extent and offset tracing files.

## Control flow

Module-level setup begins when `llite_tunables_register()` is called. It creates the global sysfs and debugfs anchors. Per-mount setup then calls `ll_debugfs_register_super()`, which first registers the sysfs kset so `llite_attrs[]` becomes visible under the mount name. If debugfs is unavailable, registration returns successfully after sysfs. Otherwise it creates the debugfs mount directory, installs manual seq files, allocates `ll_stats`, initializes every opcode counter from `llite_opcode_table`, allocates `ll_ra_stats`, initializes all readahead counters, and creates `read_ahead_stats`.

Attribute reads generally follow a short pattern: recover `struct ll_sb_info *sbi` with `container_of(kobj, struct ll_sb_info, ll_kset.kobj)`, read current state or issue `ll_statfs_internal()`, then format into `buf`. Attribute writes parse with kernel helpers (`kstrtobool`, `kstrtouint`, `kstrtoul`, `sysfs_memparse`, `sysfs_memparse_total`), validate bounds, then update `sbi`, `sbi->ll_flags`, cache state, PCC state, or `lsi->lsi_flags`. Some writes take `sbi->ll_lock`, `ccc_max_cache_mb_lock`, `ccc_lru_lock`, `ll_pp_extent_lock`, `ll_process_lock`, or root-squash locks where the underlying state is shared with active I/O paths.

Cache resizing in `ll_max_cached_mb_seq_write()` has the richest control flow. It copies a bounded user buffer, finds `max_cached_mb:`, parses a memory size, floors the value at `PTLRPC_MAX_BRW_PAGES`, and locks `ccc_max_cache_mb_lock`. If the new size is larger, it adds the difference to `ccc_lru_left`. If smaller, it first consumes unused LRU slots through an atomic compare-exchange loop, then repeatedly asks the data export to shrink OSC-side LRU slots with `KEY_CACHE_LRU_SHRINK`. On error it restores locally consumed slots before unlocking.

Stats activation is lazy. Writes to `extents_stats`, `extents_stats_per_process`, or `offset_stats` call `ll_stats_pid_write()`. A zero value disables collection. Nonzero values allocate missing structures if needed, enable `sbi->ll_rw_stats_on`, and clear the relevant histograms under the appropriate locks. Runtime I/O paths later call `ll_rw_stats_tally()`; it records per-PID extent bucket counts, aggregate bucket counts, current contiguous ranges, and discontiguous offset history.

Unmount cleanup reverses registration. `ll_debugfs_unregister_super()` removes recursive debugfs entries, removes OBD sysfs links, unregisters the mount kset, waits for the release completion, then frees stats. The release completion is signaled by `sbi_kobj_release()`.

## State and persistence behavior

The file persists no on-disk metadata directly. Its writes are runtime mount policy and diagnostics state. Most settings live in memory in:

- `struct ll_sb_info`: `ll_flags`, `ll_ra_info`, `ll_namelen`, `ll_stat_blksize`, `ll_statfs_max_age`, `ll_enable_erasure_coding`, `ll_intent_mkdir_enabled`, `ll_xattr_cache_enabled`, `ll_oc_*`, `ll_inode_cache_enabled`, `ll_dir_open_read`, file-heat fields, hybrid-IO thresholds, root-squash state, and stats pointers.
- `struct cl_client_cache`: LRU maxima/free slots, unevictable and unstable-page counters, and mlock policy.
- `struct pcc_super`: PCC mode, async threshold, affinity, and command-controlled state.
- `struct lustre_sb_info`: encryption filename flags.

Some sysfs writes propagate state below llite. `checksums_store()` sends `KEY_CHECKSUM` to `ll_dt_exp`; cache shrink operations send `KEY_CACHE_LRU_SHRINK` or `KEY_UNEVICT_CACHE_SHRINK`. Those are still runtime effects rather than durable local files. Capacity attributes observe server state by issuing statfs-style requests; they do not cache new values here except where `ll_statfs_internal()` may use shared statfs cache policy controlled elsewhere.

Stats and histograms are resettable in-memory ledgers. `ll_stats_ops_tally()` accumulates operation counters until cleared by lprocfs stats mechanisms or tracking changes. `ll_rw_stats_tally()` only records while `ll_rw_stats_on` is set and its structures exist. `ll_free_rw_stats_info()` drops optional histogram memory.

## Dependencies and integration points

This code depends on Lustre infrastructure:

- `lustre_kset`, `lustre_sysfs_ops`, `debugfs_lustre_root`, and `lprocfs`/`ldebugfs` helpers provide the external control surface.
- `llite_internal.h` and `vvp_internal.h` provide `ll_sb_info`, readahead/cache structures, PCC integration, and page-cache dump operations.
- `ll_statfs_internal()`, `ll_get_max_mdsize()`, `ll_get_default_mdsize()`, and `ll_set_default_mdsize()` connect tunables to llite/MDC metadata behavior.
- `obd_set_info_async()` sends control messages to lower data exports.
- `pcc_super_dump()` and `pcc_cmd_handle()` integrate with PCC.
- `lprocfs_wr_root_squash()`, `lprocfs_wr_nosquash_nids()`, and `ll_compute_rootsquash_state()` integrate with security policy.
- `lprocfs_counter_init()`, `lprocfs_counter_add()`, and `lprocfs_stats_alloc/free()` integrate with Lustre statistics.

The exported `ll_stats_ops_tally()` is consumed by VFS operation implementations such as lookup/create/link/unlink/mkdir/rename paths in `namei.c` and file I/O paths elsewhere. `ll_rw_stats_tally()` is called by read/write paths to feed debugfs histograms. Readahead settings directly influence readahead logic in other llite files.

## Risks and edge cases

- Several store functions update shared fields without uniform locking. Some booleans and thresholds are lockless, while others use `ll_lock`; readers in data paths must tolerate racing changes.
- `read_ahead_async_file_threshold_mb_store()` parses into an unsigned long and checks `pages_number < 0`, which is dead code; the real guard is upper-bound validation.
- `ll_max_cached_mb_seq_write()` depends on careful restoration of `ccc_lru_left` if OSC shrink fails. Bugs here can overcommit or underreport cache capacity.
- Debugfs files copy bounded user buffers, but command parsers still rely on exact strings or named values. Invalid writes should be tested for correct `-EINVAL`, `-ERANGE`, `-EFAULT`, and `-EOPNOTSUPP` returns.
- `ll_stats_ops_tally()` reads `current->real_parent->pid` and `current_gid()` for filtering; these are snapshots and can race with process lifecycle semantics, which is acceptable for diagnostics but not for policy.
- `ll_rw_stats_tally()` keeps fixed-size ring-like process and offset arrays. High PID churn overwrites older entries by design.
- Feature toggles such as encryption-name compatibility, xattr cache, PCC, checksum, and rootsquash rely on server capability bits. Incorrect capability checks can expose knobs that appear writable but are ineffective or unsafe.
- Per-mount debugfs registration returns success if the global debugfs root is absent, but sysfs has already been registered; callers must still call unregister to avoid leaks.

## Test signals

Useful tests and validation signals include:

- Mount/unmount a Lustre client and verify `/sys/fs/lustre/llite/<mount>` and `<debugfs>/lustre/llite/<mount>` appear and disappear without kobject or debugfs warnings.
- Read capacity attributes and compare against `lfs df`, `statfs(2)`, and MDT name-length limits.
- Write invalid and boundary values to `stat_blocksize`, `namelen_max`, readahead limits, `statfs_max_age`, hybrid thresholds, and PCC mode; assert exact errno behavior and no partial state mutation.
- Toggle `checksums` and verify `KEY_CHECKSUM` reaches OSCs, with warnings only on lower-layer failure.
- Exercise cache shrink/grow through `max_cached_mb` while active I/O is using the cache; verify LRU counters remain consistent and no negative free-slot accounting appears.
- Enable `extents_stats`, `extents_stats_per_process`, and `offset_stats`, run known sequential and nonsequential read/write patterns, and confirm bucket, per-PID, and offset records update and reset correctly.
- Change `stats_track_pid`, `stats_track_ppid`, `stats_track_gid`, and `0` tracking modes, then run metadata/data operations to confirm only expected counters increment.
- Toggle `intent_mkdir`, `dir_read_on_open`, open-cache thresholds, statahead knobs, and readahead knobs and verify behavior through corresponding llite paths and counters.
- For encryption builds, test enabling filename encryption against capable and incapable servers, plus old-base64 compatibility toggles.
