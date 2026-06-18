# Group Research: group_987_linux_stable_sources_os_linux_linux_stable_fs_ext4_super_c_sources_o_c15cacb70cfa

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`. All requested files were read completely in manifest order, including the full 7,606-line `super.c`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/super.c

## Purpose

`super.c` is ext4's superblock, mount, remount, journal, quota, sysfs/proc registration, filesystem-type registration, and module lifecycle implementation. It binds ext4 to the VFS through `file_system_type`, `super_operations`, `export_operations`, fs-context parsing, JBD2 journal setup, per-superblock in-memory state, and mount-time validation of on-disk ext4 metadata.

It also supports ext4-as-ext2/ext3 compatibility registration when configured.

## Major Responsibilities

- Register and unregister the ext4 filesystem module, plus optional ext2/ext3 aliases.
- Allocate, initialize, validate, and destroy `struct ext4_sb_info`.
- Read and validate the on-disk ext4 superblock.
- Parse mount/remount options through the modern `fs_context` API.
- Apply default mount policy from the on-disk superblock and explicit user options.
- Validate feature flags, geometry, checksums, group descriptors, inode sizes, cluster sizes, DAX, casefolding, encryption, quota, journaling, and large folio constraints.
- Load internal or external JBD2 journals and configure journal features.
- Manage error reporting, forced read-only state, panic/remount-ro/continue behavior, and superblock error persistence.
- Initialize ext4 subsystems needed per mount: extent status shrinker, multiblock allocator, system zones, orphan tracking, xattr caches, fast commit state, lazy inode-table initialization, per-cpu counters, quota, and proc/sysfs entries.
- Handle freeze/unfreeze, sync, statfs, remount, unmount, and shutdown paths.
- Provide exported helper functions used across ext4 for buffer reads, group descriptor fields, checksums, errors, warnings, quota enablement, and forced commits.

## VFS and Registration Interfaces

- `ext4_fs_type` registers `"ext4"` with `init_fs_context = ext4_init_fs_context`, `parameters = ext4_param_specs`, `kill_sb = ext4_kill_sb`, and flags requiring a block device plus idmapped mounts, multigrain timestamps, and large block size support.
- `ext3_fs_type` is registered as `"ext3"` through the ext4 implementation.
- Optional `ext2_fs_type` is registered when ext4 is configured to handle ext2.
- `ext4_sops` wires inode allocation/free/destruction, writeback, eviction, sync, freeze, unfreeze, statfs, mount-option display, shutdown, and quota I/O into the VFS.
- `ext4_export_ops` supports NFS file handles via generic ino32 encoding and ext4 inode lookup.
- Module init orders subsystem setup carefully: extent-status cache, pending tree, post-read processing, pageio, system zone, sysfs, mballoc, inode cache, fast-commit dentry cache, ext3/ext2 aliases, then ext4 registration.
- Module exit reverses this and stops the lazyinit kthread.

## Mount Context and Option Handling

The file defines `struct ext4_fs_context` as the temporary fs-context state. It stores mount-option bit masks, quota file names, journal device/ioprio, commit interval, stripe, inode readahead, extra inode size, lazyinit multiplier, reserved uid/gid, directory-size limit, debug fast-commit replay limit, and explicit-option markers.

Main option flow:

- `ext4_init_fs_context()` allocates `struct ext4_fs_context`, installs `ext4_context_ops`, and enables `SB_I_VERSION`.
- `ext4_parse_param()` maps fs parameters from `ext4_param_specs` and `ext4_mount_opts` into context masks and scalar fields.
- `parse_options()` handles legacy comma-separated option strings, used for on-disk `s_mount_opts`.
- `parse_apply_sb_mount_options()` applies superblock-stored default mount options before explicit runtime options.
- `ext4_validate_options()` rejects incompatible quota-option combinations.
- `ext4_check_opt_consistency()` enforces ext2/ext3 compatibility restrictions, remount invariants, DAX rules, data journaling immutability on remount, dummy encryption constraints, and quota consistency.
- `ext4_apply_options()` transfers the validated context masks and scalar values into `ext4_sb_info` and `super_block`.
- `_ext4_show_options()` and `ext4_seq_options_show()` emit active options for mountinfo and `/proc/fs/ext4/<dev>/options`.

Important constraints enforced here include no journal device/path changes on remount, no changing data mode on remount, no incompatible DAX transitions on remount, no journal options on no-journal filesystems, and no mixing old quota mount options with journaled quota files.

## Superblock Read and Mount Bring-Up

`ext4_fill_super()` allocates `ext4_sb_info`, sanitizes the device name, selects the superblock block, and calls `__ext4_fill_super()`.

`__ext4_fill_super()` is the main mount pipeline:

1. Set initial defaults such as journal IO priority, inode readahead, write counters, commit/batch intervals, superblock update intervals, and lazyinit multiplier.
2. `ext4_load_super()` reads the ext4 superblock, handles 1 KiB offset alignment, validates magic and block-size fields, and reloads at the actual filesystem block size when needed.
3. `ext4_init_metadata_csum()` validates checksum type, verifies the superblock checksum, sets checksum triggers, and precomputes metadata checksum seed.
4. `ext4_set_def_opts()` applies on-disk default mount options such as ACLs, xattrs, journal checksum, data mode, errors policy, block validity, discard, barrier, delayed allocation, and dioread_nolock.
5. `ext4_inode_info_init()` validates inode size, first inode, timestamp granularity/ranges, and desired extra inode size.
6. Apply superblock-stored mount options, validate user options, apply explicit options, initialize encoding/casefolding, and validate data-journal mode.
7. Validate ext2/ext3/ext4 feature compatibility, DAX, encryption level, descriptor sizes, groups, inode counts, clusters, filesystem geometry, hash seed/version, and group descriptors.
8. Initialize timers, error locks, work items, shrinkers, stripe settings, VFS operations, xattr/encryption/verity/quota operation tables, UUID/sysfs name, orphan list, fast commit state, atomic write support, MMP, and journal.
9. Create xattr caches, calculate overhead clusters, allocate reservation conversion workqueue, load root inode and root dentry, update mount state, reserve clusters, create system-zone metadata, initialize extents, per-cpu counters, mballoc, flex_bg metadata, lazyinit, orphan info, quota tracking, orphan cleanup, recovery completion, discard policy, ratelimits, and sysfs/proc entries.
10. On every failure label, unwind only the initialized subsystems in reverse order.

The mount code is highly defensive: corrupted root inode, bad group descriptors, invalid checksums, unsupported features, inconsistent geometry, unreadable journal, or impossible option combinations abort the mount with explicit cleanup.

## Journal Management

The file supports both internal journal inodes and external journal devices.

Key functions:

- `ext4_get_journal_inode()` validates the internal journal inode exists, is linked, regular, and not encrypted.
- `ext4_open_inode_journal()` initializes a JBD2 journal backed by the journal inode and installs `ext4_journal_bmap()`.
- `ext4_get_journal_blkdev()` opens and validates an external journal block device, including magic, journal-dev incompat flag, checksum, and UUID match.
- `ext4_open_dev_journal()` initializes a JBD2 journal on an external device and rejects external journals with multiple users.
- `ext4_load_journal()` chooses internal or external journal, checks read-only/recovery constraints, wipes or loads JBD2 state, preserves ext4 error fields across journal replay, clears prior journal errors, and updates stored journal dev/inode values if needed.
- `ext4_load_and_init_journal()` sets JBD2 64-bit, checksum, async commit, and fast-commit features, selects default data mode if unspecified, rejects incompatible data/async combinations, sets journal task IO priority, and installs inode data-buffer callbacks.
- `ext4_init_journal_params()` applies commit interval, batch timing, fast commit config, barriers, and cycle recording.
- `ext4_journal_commit_callback()` processes freed data and schedules periodic superblock updates after commits.
- `ext4_force_commit()` exposes a forced JBD2 commit helper.

Data journaling mode has special handling: `data=journal` disables delayed allocation, dioread_nolock, O_DIRECT, and fast commit, and rejects DAX or explicit delalloc conflicts.

## Error Handling and Superblock Updates

The file centralizes ext4 error policy.

Important functions:

- `save_error_info()` records first/last runtime error metadata under `s_error_lock`.
- `ext4_handle_error()` marks `EXT4_ERROR_FS`, aborts the journal unless continuing is allowed, persists error state directly or through deferred work, handles panic policy, and sets emergency read-only state for remount-ro behavior.
- `update_super_work()` writes superblock updates through the journal when possible, or directly as fallback, and notifies sysfs error observers.
- `__ext4_error()`, `__ext4_error_inode()`, `__ext4_error_file()`, `__ext4_std_error()`, `__ext4_warning()`, `__ext4_warning_inode()`, and `__ext4_grp_locked_error()` provide formatted, ratelimited reporting paths for global, inode, file, standard error, warning, and group-locked contexts.
- `ext4_decode_error()` maps kernel errors to human-readable strings.
- `ext4_update_super()` copies in-memory counters, write timestamps, write-kbytes, free blocks/inodes, and accumulated error info into the on-disk superblock buffer and updates its checksum.
- `ext4_commit_super()` writes the superblock synchronously, with optional FUA when barriers are enabled.
- `ext4_mark_recovery_complete()` flushes the journal and clears recovery/orphan feature bits when safe.
- `ext4_clear_journal_err()` transfers prior JBD2 journal error state into the ext4 superblock and clears the journal errno.
- `print_daily_error_info()` periodically logs persistent first/last error details and error counts.

The code treats emergency shutdown/read-only states as early exits in many paths to avoid recursion or unsafe writes.

## Group Descriptor, Geometry, and Checksums

The file owns core superblock-adjacent metadata helpers:

- `ext4_block_bitmap()`, `ext4_inode_bitmap()`, `ext4_inode_table()` and setters combine low/high descriptor fields for 64-bit descriptor support.
- `ext4_free_group_clusters()`, `ext4_free_inodes_count()`, `ext4_used_dirs_count()`, and `ext4_itable_unused_count()` read split descriptor counters.
- `ext4_group_desc_csum()`, `ext4_group_desc_csum_verify()`, and `ext4_group_desc_csum_set()` implement both metadata_csum CRC32C and legacy gdt_csum CRC16 formats.
- `ext4_check_descriptors()` verifies bitmap/inode-table locations, overlap with superblock/GDT areas, group bounds, checksum validity, and tracks the first non-zeroed inode table group.
- `descriptor_loc()` locates group descriptor blocks, including meta_bg and 1 KiB block-size special cases.
- `ext4_block_group_meta_init()` derives descriptor size, blocks/inodes per group, inode-table blocks per group, descriptor counts, max file sizes, and mount state.
- `ext4_handle_clustersize()` validates bigalloc/non-bigalloc cluster geometry and detects standard group size.
- `ext4_check_geometry()` validates reserved GDT size, device addressability, total block count against device size, first data block, group count limit, and inode count consistency.
- `ext4_calculate_overhead()` and `count_overhead()` calculate filesystem overhead clusters, including group metadata and internal journal blocks.
- `ext4_set_resv_clusters()` reserves a small cluster pool for metadata-sensitive operations on extent filesystems.

## Lazy Initialization and Background Work

The file implements global lazy inode-table initialization state:

- `ext4_register_li_request()` registers a per-superblock lazyinit request unless the filesystem is read-only, in emergency state, or has no work.
- `ext4_lazyinit_thread()` runs a global freezable kthread that walks requests, prefetches block bitmaps, zeroes inode tables via `ext4_init_inode_table()`, randomizes retry timing when locks cannot be acquired, and exits when the list is empty.
- `ext4_run_li_request()` switches from bitmap prefetch mode to inode-table initialization mode when appropriate.
- `ext4_unregister_li_request()`, `ext4_remove_li_request()`, `ext4_clear_request_list()`, and `ext4_destroy_lazyinit_thread()` cleanly remove pending work on unmount or module unload.

Lazyinit scheduling is remount-aware and reacts to `init_itable`, read-only state, and `no_prefetch_block_bitmaps`.

## Inode Cache and In-Core Inode Lifecycle

- `init_inodecache()` creates `ext4_inode_cache` with constructor `init_once()`.
- `ext4_alloc_inode()` initializes ext4 inode private state: version, flags, prealloc trees, extent-status tree, reservations, quota fields, JBD2 inode pointer, conversion work, fast-commit tracking, metadata buffer tracking, and locks.
- `ext4_destroy_inode()` warns if an inode is still orphan-tracked or has uncleared reserved data blocks.
- `ext4_free_in_core_inode()` frees fscrypt state and returns the inode to the cache.
- `ext4_clear_inode()` removes fast-commit state, invalidates metadata buffers for no-journal mode, clears VFS inode state, discards preallocations, removes the inode hash before freeing inode bitmap state, clears extents status, drops quotas, releases JBD2 inode state, and frees encryption info.
- `ext4_drop_inode()` delegates to generic drop logic and fscrypt drop rules.

## Remount, Freeze, Sync, and Unmount

- `ext4_sync_fs()` flushes reservation conversion work, writes quota state, starts/waits for JBD2 commits when present, and issues block-device flushes when barriers require it.
- `ext4_freeze()` locks journal updates, flushes the journal, clears recovery/orphan-present bits when safe, and commits the superblock for snapshot consistency.
- `ext4_unfreeze()` restores recovery/orphan-present bits for journaled filesystems and commits the superblock.
- `__ext4_remount()` snapshots old options, validates and applies new options under writeback exclusion where needed, handles read-write to read-only and read-only to read-write transitions, validates group descriptor checksums, rejects unprocessed orphans on rw remount, restarts MMP, adjusts quota state, system-zone state, lazyinit, and abort handling, and rolls back options on failure.
- `ext4_reconfigure()` integrates remount with `fs_context`.
- `ext4_put_super()` unregisters sysfs, stops lazyinit and quotas, destroys workqueues, orphan info, journal, shrinkers, timers, system zones, mballoc, extents, superblock state, group descriptors, flex groups, per-cpu counters, xattr caches, MMP, DAX refs, fscrypt dummy policy, Unicode encoding, kobject state, and `ext4_sb_info`.

Unmount order is deliberate: sysfs is removed before journal destruction and deferred superblock work is flushed only after paths that can enqueue it are disabled.

## Quota Support

When `CONFIG_QUOTA` is enabled, `super.c` defines ext4 quota operations and quotactl hooks.

Covered paths:

- Mount-option parsing for journaled quota file names and formats.
- Consistency checks preventing quota option changes while quotas are loaded and preventing old/new quota mode mixing.
- `ext4_quota_on()` validates same-filesystem quota files, handles journaled quota flags, sets quota inode lockdep class, enables quota, and marks quota files immutable/noatime.
- `ext4_quota_enable()` loads quota tracking from hidden quota inodes used by the quota feature.
- `ext4_enable_quotas()` enables all configured quota types during mount.
- `ext4_quota_off()` forces delayed allocations out, disables quota, and clears quota-file inode flags when possible.
- `ext4_write_dquot()`, `ext4_acquire_dquot()`, `ext4_release_dquot()`, `ext4_mark_dquot_dirty()`, and `ext4_write_info()` wrap quota operations in ext4 journal handles.
- `ext4_quota_read()` and `ext4_quota_write()` provide direct quota file I/O avoiding normal page-cache paths.
- `ext4_statfs_project()` applies project quota limits to statfs results when project inheritance and limits are active.

## Statfs and Reporting

`ext4_statfs()` reports ext4 magic, block size, total blocks minus overhead unless `minixdf` is active, free blocks adjusted for dirty delayed-allocation clusters, available blocks after reserved blocks/clusters, inode counts, name length, and UUID-derived fsid. Project quota limits can cap block and inode availability.

Mount/unmount/remount messages are ratelimited globally, while per-superblock error, warning, and normal messages have independent ratelimit state and counters exposed through sysfs.

## Important Edge Cases and Risks

- Superblock and group-descriptor checksum validation are mount-critical; read-only mounts may tolerate some descriptor overlap/checksum failures that read-write mounts reject.
- Journal recovery requires temporary write access even for read-only mounts; truly read-only devices must use `noload`.
- `data=journal` disables several performance features and conflicts with DAX and explicit delalloc.
- Remount rollback must restore quota names through RCU and restore mount flags under writeback exclusion.
- Error handling avoids taking `s_umount` to set `SB_RDONLY`; it uses ext4 emergency read-only state instead to avoid deadlocks.
- External journals are tightly validated by UUID, superblock feature flags, checksum, block size, and user count.
- Lazyinit must hold mount/write locks opportunistically to avoid racing unmount and freeze.
- Quota operations intentionally start journal transactions before acquiring quota I/O locks to preserve lock ordering.
- Mount cleanup labels are numerous; future edits must preserve reverse-order teardown or risk leaks/use-after-free around journals, sysfs, workqueues, timers, and group descriptors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/symlink.c

## Purpose

`symlink.c` implements ext4 symlink inode operations. Most symlink behavior is handled by generic VFS code; this file supplies ext4-specific link target retrieval for fast symlinks, block-backed symlinks, inline-data leftovers, and encrypted symlinks.

## Main Flows

- `ext4_encrypted_get_link()` returns decrypted symlink targets through `fscrypt_get_symlink()`.
  - For fast symlinks, it reads ciphertext from `EXT4_I(inode)->i_data`.
  - For non-fast symlinks, it reads logical block 0 with `ext4_bread()`.
  - A missing block is reported as ext4 corruption via `EXT4_ERROR_INODE()` and `-EFSCORRUPTED`.
  - It releases the temporary buffer head before returning the fscrypt-managed result.
- `ext4_encrypted_symlink_getattr()` delegates base attributes to `ext4_getattr()` and then adjusts encrypted symlink size through `fscrypt_symlink_getattr()`.
- `ext4_get_link()` handles normal unencrypted symlink targets.
  - If inline data is present, new inline symlink creation is not supported, but old inline symlink data can still be read through `ext4_read_inline_link()`.
  - For RCU pathwalk (`dentry == NULL`), it only returns a cached uptodate block; otherwise it returns `-ECHILD` so lookup can retry in ref-walk mode.
  - For normal lookup, it reads block 0 with `ext4_bread()`, validates it exists, sets delayed cleanup with `ext4_free_link()`, terminates the target with `nd_terminate_link()`, and returns `bh->b_data`.
- `ext4_free_link()` releases buffer heads used as delayed link storage.

## Exported Operation Tables

- `ext4_encrypted_symlink_inode_operations`
  - `.get_link = ext4_encrypted_get_link`
  - `.setattr = ext4_setattr`
  - `.getattr = ext4_encrypted_symlink_getattr`
  - `.listxattr = ext4_listxattr`
- `ext4_symlink_inode_operations`
  - normal block-backed or inline symlink handling through `ext4_get_link()`.
- `ext4_fast_symlink_inode_operations`
  - fast in-inode unencrypted symlinks use `simple_get_link()`.

## Integration Points

This file depends on:

- `ext4_inode_is_fast_symlink()` from inode logic.
- `ext4_bread()` and `ext4_getblk()` for block-backed symlink storage.
- Inline data helpers for legacy inline symlink targets.
- fscrypt for encrypted symlink decoding and encrypted symlink getattr.
- xattr handlers through the inode operation tables.

## Edge Cases

- RCU lookup never performs blocking disk I/O; it returns `-ECHILD` unless the needed block is already cached and uptodate.
- Missing symlink blocks are treated as filesystem corruption.
- Inline symlink creation is intentionally not supported here; only reading existing inline data remains.
- Buffer lifetime is managed with delayed calls so returned link pointers remain valid through VFS path resolution.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/sysfs.c

## Purpose

`sysfs.c` implements ext4's global and per-mounted-filesystem sysfs/procfs interface. It creates `/sys/fs/ext4`, `/sys/fs/ext4/features`, per-superblock sysfs attribute groups, and `/proc/fs/ext4/<dev>/` diagnostic files.

## Attribute Model

The file defines a compact attribute descriptor:

- `struct ext4_attr` wraps `struct attribute`.
- `attr_id_t` identifies custom show/store behavior or primitive pointer formatting.
- `attr_ptr_t` says whether the attribute points to an explicit global, an offset in `struct ext4_sb_info`, or an offset in `struct ext4_super_block`.
- Macros such as `EXT4_ATTR_FUNC`, `EXT4_ATTR_OFFSET`, `EXT4_RO_ATTR_ES_UI`, `EXT4_RW_ATTR_SBI_UI`, and `EXT4_ATTR_FEATURE` declare most attributes.

Pointer-backed attributes are resolved by `calc_ptr()` and displayed or updated by generic show/store helpers.

## Per-Mount Sysfs Attributes

The per-superblock `ext4_attrs` group exposes operational counters and tunables, including:

- Delayed allocation blocks.
- Session and lifetime write kilobytes.
- Reserved clusters.
- SRA retry-limit counter.
- Inode readahead blocks.
- Mballoc tunables such as `mb_stats`, scan limits, stream/group preallocation, prefetch, prefetch limit, and trim settings.
- Extent zeroout limit.
- Error injection through `trigger_fs_error`.
- Error, warning, and normal-message ratelimit interval/burst tunables.
- Error counters and first/last error metadata from the on-disk superblock.
- Journal task pid.
- Superblock update cadence through `sb_update_sec` and `sb_update_kb`.
- Daily error-reporting interval through `err_report_sec`.
- Debug-only `simulate_fail` when `CONFIG_EXT4_DEBUG` is enabled.

## Feature Sysfs Attributes

The global `/sys/fs/ext4/features` group reports supported ext4 features as `"supported\n"`:

- `lazy_itable_init`
- `batched_discard`
- `meta_bg_resize`
- `metadata_csum_seed`
- `fast_commit`
- Optional encryption, dummy encryption v2, casefold, verity, encrypted casefold, and blocksize greater than page size depending on kernel config.

## Show/Store Behavior

Important helpers:

- `session_write_kbytes_show()` reports sectors written since mount.
- `lifetime_write_kbytes_show()` combines persisted lifetime write kbytes with current-session device writes.
- `inode_readahead_blks_store()` accepts zero or a power of two up to `0x40000000`.
- `reserved_clusters_store()` validates the value is less than total clusters and stores it in `s_resv_clusters`.
- `trigger_test_error()` requires `CAP_SYS_ADMIN` and injects an ext4 error using the written string.
- `err_report_sec_store()` validates interval up to one year, starts/stops/reprograms the error-report timer, and returns the write count.
- `journal_task_show()` reports `<none>` without a journal or the JBD2 task pid otherwise.
- `ext4_generic_attr_show()` formats integer, string, atomic, little-endian superblock, and pointer-backed values.
- `ext4_generic_attr_store()` parses and validates writable pointer-backed integer attributes.
- `ext4_attr_show()` dispatches special attributes and feature attributes.
- `ext4_attr_store()` dispatches special stores and falls back to generic stores.

## Kobject and Proc Lifecycle

- `ext4_init_sysfs()` creates the global `ext4_root` kobject under `fs_kobj`, allocates and registers the `features` kobject, and creates the `/proc/fs/ext4` root.
- `ext4_register_sysfs()` initializes the per-superblock kobject under `/sys/fs/ext4/<sb-id>` and creates proc entries under `/proc/fs/ext4/<sb-id>/`.
- Per-mount proc entries include:
  - `options`
  - `es_shrinker_info`
  - `fc_info`
  - `mb_groups`
  - `mb_stats`
  - `mb_structs_summary`
- `ext4_unregister_sysfs()` removes the proc subtree and deletes the per-superblock kobject.
- `ext4_exit_sysfs()` drops global kobjects and removes `/proc/fs/ext4`.
- `ext4_sb_release()` completes `s_kobj_unregister`, which unmount waits on before freeing `ext4_sb_info`.
- `ext4_feat_release()` frees the dynamically allocated feature kobject.
- `ext4_notify_error_sysfs()` notifies the `errors_count` sysfs file when new errors are committed, protected by `s_error_notify_mutex`.

## Integration Points

This file is called from `super.c` during ext4 module init/exit, mount completion, unmount, and deferred superblock error update work. It depends on mballoc, fast commit, extent-status shrinker, and option display functions to populate proc diagnostics.

## Edge Cases

- Per-superblock kobject registration is synchronized with error notifications through `s_error_notify_mutex`.
- On registration failure, the code calls `kobject_put()` and waits for completion before returning.
- `journal_task_show()` tolerates filesystems without a journal.
- `err_report_sec_store()` handles enable, disable, and interval update paths without leaving stale timers active.
- Attribute stores validate ranges for tunables that feed allocator or timer behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/truncate.h -->
# File Research: sources/os/linux/linux-stable/fs/ext4/truncate.h

## Purpose

`truncate.h` contains two small inline helpers shared by ext4 truncate/write-failure paths.

## Functions

- `ext4_truncate_failed_write(struct inode *inode)`
  - Handles cleanup after a write allocated blocks that were not ultimately used.
  - Takes the file mapping invalidate lock.
  - Truncates page cache back to `inode->i_size`.
  - Calls `ext4_truncate()` to remove blocks beyond the current size.
  - Releases the invalidate lock.
  - It intentionally skips `ext4_break_layouts()` because the blocks being removed were never visible to userspace.

- `ext4_blocks_for_truncate(struct inode *inode)`
  - Estimates journal transaction credits needed for the next truncate chunk.
  - Starts from `inode->i_blocks` converted from 512-byte sectors to filesystem blocks.
  - Floors the estimate at 2 blocks to survive corrupt but regular-looking inodes with nonsensical `i_blocks`.
  - Caps the chunk at `EXT4_MAX_TRANS_DATA` to avoid overflowing the journal.
  - Returns `EXT4_DATA_TRANS_BLOCKS(inode->i_sb) + needed`.

## Integration Points

These helpers are used by ext4 write and truncate paths that need to clean up partially allocated blocks or bound truncate transaction size. They depend on VFS page-cache invalidation, ext4 block truncation, and ext4 journal credit macros.

## Edge Cases

- The transaction sizing helper is corruption-tolerant: it tries to avoid kernel panics when on-disk `i_blocks` is bad.
- The failed-write cleanup assumes the discarded allocations were not user-visible, allowing a narrower cleanup path than normal truncate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/truncate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/verity.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/verity.c

## Purpose

`verity.c` implements `fsverity_operations` for ext4. It stores fs-verity metadata, including the Merkle tree and fsverity descriptor, beyond the visible end of the file, beginning at the first 64 KiB boundary after `i_size`.

This design keeps verity metadata encrypted when file contents are encrypted, because metadata is stored as file data beyond EOF rather than as xattrs.

## Metadata Layout

- `ext4_verity_metadata_pos(inode)` returns `round_up(inode->i_size, 65536)`.
- The Merkle tree starts at that position.
- The verity descriptor starts at the next filesystem block boundary after the Merkle tree.
- The descriptor size is stored as a little-endian 32-bit value in the last 4 bytes of the last allocated filesystem block, either in the descriptor-ending block or a following block if needed.
- Ext4 later finds the descriptor by finding the last extent and reading those last 4 bytes.

## Page-Cache I/O Helpers

- `pagecache_read()` reads arbitrary bytes, including beyond `i_size`, using `read_mapping_folio()` and `memcpy_from_file_folio()`.
- `pagecache_write()` writes arbitrary bytes beyond `i_size` using the mapping's `write_begin` and `write_end` operations. It rejects writes beyond `s_maxbytes` and requires full write completion.

These helpers avoid normal VFS read/write interfaces because verity enabling may write through a read-only file descriptor and must access beyond EOF.

## Enabling Verity

`ext4_begin_enable_verity()` prepares a file for verity metadata creation:

- Rejects DAX files and inodes with DAX flag.
- Rejects concurrent verity enablement via `EXT4_STATE_VERITY_IN_PROGRESS`.
- Attaches a JBD2 inode and initializes quotas because the file was opened read-only.
- Converts inline data to normal storage.
- Requires extent-based files.
- Truncates any blocks beyond EOF so descriptor lookup cannot be confused by old post-EOF allocations.
- Adds the inode to the orphan list in a small transaction.
- Sets `EXT4_STATE_VERITY_IN_PROGRESS`.

`ext4_end_enable_verity()` completes or rolls back verity enablement:

- If `desc == NULL`, it skips straight to cleanup.
- Writes the verity descriptor using `ext4_write_verity_descriptor()`.
- Calls `filemap_write_and_wait()` to flush both normal data and verity metadata while `EXT4_STATE_VERITY_IN_PROGRESS` is still set.
- Starts a transaction, marks fast commit ineligible for verity, removes the inode from the orphan list, reserves inode write access, sets `EXT4_INODE_VERITY`, syncs inode flags, marks the inode dirty, clears the in-progress state, and returns success.
- On any error, truncates page cache back to `i_size`, truncates allocated metadata blocks, removes the orphan record if present, clears the in-progress state, and returns the error.

The orphan-list protocol protects crash consistency: incomplete verity enablement leaves cleanup work discoverable.

## Descriptor Lookup and Reads

- `ext4_get_verity_descriptor_location()` requires extent-based storage, finds the last extent with `ext4_find_extent()`, derives the last allocated logical block, reads the trailing descriptor-size field, validates size and position, and returns descriptor size and offset.
- It reports corruption when the file lacks extents, has no extents, has an impossible descriptor size, or points before the verity metadata area.
- `ext4_get_verity_descriptor()` returns descriptor size when `buf_size == 0`, or reads the descriptor into the supplied buffer after checking capacity.

## Merkle Tree Operations

- `ext4_read_merkle_tree_page()` offsets the requested page index by `ext4_verity_metadata_pos() >> PAGE_SHIFT` and calls `generic_read_merkle_tree_page()`.
- `ext4_readahead_merkle_tree()` applies the same offset and calls `generic_readahead_merkle_tree()`.
- `ext4_write_merkle_tree_block()` offsets the provided position by the metadata base and writes through `pagecache_write()`.

## Exported Operation Table

`ext4_verityops` provides:

- `.begin_enable_verity = ext4_begin_enable_verity`
- `.end_enable_verity = ext4_end_enable_verity`
- `.get_verity_descriptor = ext4_get_verity_descriptor`
- `.read_merkle_tree_page = ext4_read_merkle_tree_page`
- `.readahead_merkle_tree = ext4_readahead_merkle_tree`
- `.write_merkle_tree_block = ext4_write_merkle_tree_block`

This table is assigned to `sb->s_vop` during mount when `CONFIG_FS_VERITY` is enabled.

## Edge Cases

- DAX is rejected because fs-verity metadata is managed through page-cache paths.
- Inline data is converted before enabling verity.
- Non-extent files are rejected for verity enablement and treated as corruption if already marked verity.
- Existing post-EOF blocks are truncated before writing verity metadata to keep descriptor discovery unambiguous.
- Cleanup must remove both cached and allocated metadata beyond `i_size`.
- Descriptor location is inferred from the last allocated block, so corrupt extents or unexpected post-EOF allocations can make verity metadata unreadable and trigger ext4 corruption reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/verity.c -->