# Group Research: group_745_linux_sources_os_linux_linux_fs_ext4_super_c_sources_os_linux_linux__e3a46a71c572

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/super.c -->
# File Research: sources/os/linux/linux/fs/ext4/super.c

## Purpose
Implements ext4 superblock, mount, remount, unmount, journal, quota, error-reporting, lazy-init, statfs, and filesystem registration logic. This is the main VFS integration file for mounting ext4, and conditionally for ext2/ext3 compatibility.

## Main Elements
- Filesystem types and context operations: `ext4_fs_type`, optional `ext2_fs_type`, `ext3_fs_type`, `ext4_context_ops`, `ext4_init_fs_context()`, `ext4_get_tree()`, `ext4_reconfigure()`, `ext4_kill_sb()`.
- Buffer/superblock I/O helpers: `ext4_read_bh*()`, `ext4_sb_bread*()`, `ext4_sb_breadahead_unmovable()`, `ext4_load_super()`, `ext4_update_super()`, `ext4_commit_super()`.
- Metadata checksum helpers: `ext4_superblock_csum*()`, `ext4_group_desc_csum*()`, checksum seed setup, checksum journal trigger setup.
- Group descriptor accessors: block bitmap, inode bitmap, inode table, free inode/block counters, directory counts, itable-unused getters/setters.
- Error handling: `__ext4_error*()`, `__ext4_std_error()`, `ext4_handle_error()`, `save_error_info()`, `update_super_work()`, ratelimited warnings/messages, emergency read-only handling, journal abort propagation.
- Inode lifecycle: inode slab creation/destruction, `ext4_alloc_inode()`, `ext4_destroy_inode()`, `ext4_clear_inode()`, orphan-list debugging, NFS export inode lookup/metadata commit hooks.
- Mount option handling: `ext4_param_specs`, option token tables, `ext4_parse_param()`, `parse_options()`, superblock-stored option parsing, quota option reconciliation, dummy encryption checks, `ext4_apply_options()`, option display.
- Mount validation and setup: feature compatibility checks, geometry checks, block group descriptor loading, cluster/bigalloc checks, inode-size/time-range setup, casefold encoding init, journal data-mode checks, large folio constraints, DAX checks.
- Journal integration: internal/external journal open, journal bmap, journal load/recovery, checksum/fast-commit feature setup, commit callbacks, recovery completion, journal error clearing, freeze/unfreeze, sync.
- Lazy initialization: global `ext4lazyinit` thread, per-superblock lazy inode table and block bitmap prefetch requests, registration/unregistration, randomized scheduling.
- Capacity/accounting: overhead calculation, reserved cluster defaults, percpu counters, flex_bg summary initialization, statfs and project-quota-limited statfs.
- Quota support under `CONFIG_QUOTA`: quota operations, quotactl operations, system quota file enablement, journaled quota file flagging, quota read/write helpers.
- Module lifecycle: `ext4_init_fs()` initializes extents status, pending reservations, post-read processing, pageio, system zones, sysfs, mballoc, inode cache, fast-commit dentry cache, and registers filesystems; `ext4_exit_fs()` unwinds them.

## Control Flow
Initial mount enters `ext4_fill_super()`, allocates `ext4_sb_info`, normalizes the superblock id, selects the superblock block, then calls `__ext4_fill_super()`. That routine reads the on-disk superblock, verifies metadata checksums, establishes default options, parses superblock and user mount options, validates options/features/geometry, loads group descriptors, initializes journal or no-journal mode, builds xattr caches and overhead accounting, creates the reservation workqueue, reads the root inode, commits mount-state changes, initializes extents, percpu counters, mballoc, flex groups, lazy-init, orphan info, quotas, orphan cleanup, recovery completion, discard checks, error-report timers, ratelimits, and sysfs/proc registration.

Remount stores old options, applies the new context under writeback coordination, rejects unsupported data/journal/cache/delalloc changes, handles read-only transitions with sync/quota suspension/recovery flag cleanup, handles read-write transitions with feature and descriptor checksum checks, restarts MMP and quota as needed, updates system-zone and lazy-init state, and restores old options on failure.

Unmount unregisters sysfs/proc early, removes lazy-init and quotas, destroys workqueues and orphan info, tears down the journal or flushes superblock work, releases shrinkers/system-zone/mballoc/extents, commits clean state when possible, frees descriptors/flex groups/percpu counters/quota names/caches/MMP/DAX/encryption/encoding resources, invalidates block devices, and releases the superblock kobject.

## Dependencies And Integration
Depends heavily on Linux VFS, fs_context/fs_parser, block device APIs, buffer heads, jbd2, quota, fscrypt, fs-verity, Unicode casefolding, DAX, procfs/sysfs, percpu counters, workqueues, timers, and ext4 subsystems such as extents, mballoc, xattrs, fast commit, orphan handling, system zones, and fsmap. It exports core helpers used throughout ext4 for error reporting, metadata reads, descriptor accounting, sync, commit, and feature validation.

## Behavioral Notes
The file centralizes ext4’s safety gates: unsupported feature refusal, descriptor checksum validation, MMP protection, journal recovery requirements, journal/no-journal option compatibility, quota consistency, DAX restrictions, encryption/casefold requirements, and forced read-only behavior after serious errors. It writes superblock error state either through the journal or directly depending on journal state, and schedules deferred superblock updates to avoid unsafe lock ordering.

## Risk Notes
This file has a large blast radius. Bugs can lead to unsafe mounts, missed journal recovery, incorrect read-only/read-write transitions, stale or corrupt free-space accounting, orphan leakage, quota corruption, or lost error diagnostics. The most delicate areas are mount failure unwinding, remount rollback, journal recovery state transitions, group descriptor checksum handling, quota option changes, and direct versus journaled superblock writes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/symlink.c -->
# File Research: sources/os/linux/linux/fs/ext4/symlink.c

## Purpose
Provides ext4 symlink inode operations, including fast symlinks, block-backed symlinks, inline-data symlink remnants, and encrypted symlink decoding.

## Main Elements
- `ext4_encrypted_get_link()`: fetches symlink bytes from fast symlink inode data or block 0, then delegates decoding to `fscrypt_get_symlink()`.
- `ext4_encrypted_symlink_getattr()`: combines normal ext4 getattr with fscrypt symlink size adjustment.
- `ext4_get_link()`: reads normal symlink targets from inline data or block 0, supports RCU-walk fallback with `-ECHILD`, terminates the link buffer, and arranges delayed buffer release.
- `ext4_free_link()`: delayed-call buffer release helper.
- Inode operation tables: `ext4_encrypted_symlink_inode_operations`, `ext4_symlink_inode_operations`, and `ext4_fast_symlink_inode_operations`.

## Dependencies And Integration
Uses VFS namei delayed-call link handling, buffer heads through `ext4_bread()`/`ext4_getblk()`, ext4 inline-data helpers, and fscrypt symlink helpers. The operation tables are selected when ext4 instantiates symlink inodes.

## Behavioral Notes
Fast unencrypted symlinks use `simple_get_link()` because their target is stored directly in inode data. Encrypted symlinks must decode ciphertext from either inline inode data or an external block. Non-encrypted block symlinks use cached-nowait lookup during RCU-walk and force pathwalk retry when the buffer is unavailable or not uptodate.

## Risk Notes
Correctness depends on rejecting bad symlink block mappings and returning `-EFSCORRUPTED` for missing block-backed symlink data. The inline-data path is read-only compatibility support: new inline symlinks are not created here, but old leftovers can still be read.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/sysfs.c -->
# File Research: sources/os/linux/linux/fs/ext4/sysfs.c

## Purpose
Implements ext4’s sysfs and procfs surface for per-mounted-filesystem tunables/statistics, supported feature advertisement, and error notification.

## Main Elements
- Attribute model: `struct ext4_attr`, `attr_id_t`, `attr_ptr_t`, macros for explicit, `ext4_sb_info`, and on-disk superblock-backed attributes.
- Read-only counters/status: delayed allocation blocks, session/lifetime write kbytes, exceeded retry count, warning/message/error counters, first/last error metadata, journal task pid.
- Writable tunables: reserved clusters, inode readahead blocks, mballoc scan/prealloc parameters, extent zeroout limit, ratelimit settings, prefetch settings, trim threshold, superblock update interval/size, and error report interval.
- Test/debug hooks: `trigger_fs_error` requires `CAP_SYS_ADMIN`; `simulate_fail` exists under `CONFIG_EXT4_DEBUG`.
- Feature directory: advertises supported features such as lazy inode-table init, batched discard, meta_bg resize, encryption, casefold, verity, metadata checksum seed, fast commit, encrypted casefold, and blocksize greater than page size when configured.
- Procfs registration: creates `/proc/fs/ext4/<dev>/options`, `es_shrinker_info`, `fc_info`, `mb_groups`, `mb_stats`, and `mb_structs_summary`.
- Lifecycle: `ext4_init_sysfs()`, `ext4_exit_sysfs()`, `ext4_register_sysfs()`, `ext4_unregister_sysfs()`, and `ext4_notify_error_sysfs()`.

## Dependencies And Integration
Hooks into kobject/sysfs, procfs, block statistics, ext4 mballoc and fast-commit seq interfaces, and error-reporting state maintained in `super.c`. Per-superblock registration occurs late in mount after core initialization and is unregistered early during unmount.

## Behavioral Notes
Generic show/store paths compute pointers from either `ext4_sb_info`, `ext4_super_block`, or explicit storage. Stores validate bounds for power-of-two readahead, reserved-cluster count, mballoc order/group limits, and error-report intervals. Error sysfs notification is serialized with `s_error_notify_mutex` to avoid races with kobject deletion.

## Risk Notes
Writable sysfs attributes directly mutate live allocator and reporting tunables, so validation is the main safety boundary. Attributes backed by on-disk superblock fields must handle endianness correctly. Registration order matters because proc/sysfs readers can race with unmount and journal teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/truncate.h -->
# File Research: sources/os/linux/linux/fs/ext4/truncate.h

## Purpose
Defines small inline helpers shared by ext4 truncate paths.

## Main Elements
- `ext4_truncate_failed_write()`: invalidates pagecache beyond the current inode size and calls `ext4_truncate()` after a failed write allocation path.
- `ext4_blocks_for_truncate()`: estimates transaction credits needed for a truncate chunk from `i_blocks`, clamps suspiciously small values upward, and caps the transaction at `EXT4_MAX_TRANS_DATA`.

## Dependencies And Integration
Uses the inode mapping invalidate lock, pagecache truncation helpers, `ext4_truncate()`, and ext4 transaction credit macros. Included by truncate/write paths that need common cleanup and credit sizing.

## Behavioral Notes
Failed-write truncation skips `ext4_break_layouts()` because the blocks being discarded were never visible to userspace. Credit sizing is intentionally defensive against corrupt inodes whose `i_blocks` value is nonsensical.

## Risk Notes
The helpers protect against both stale buffer mappings after failed writes and oversized journal transactions during truncation. Incorrect credit estimates here could cause journal credit exhaustion or unnecessary transaction splitting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/truncate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/verity.c -->
# File Research: sources/os/linux/linux/fs/ext4/verity.c

## Purpose
Implements ext4’s `fsverity_operations`, storing fs-verity Merkle tree and descriptor metadata beyond EOF while preserving encryption and crash-consistency requirements.

## Main Elements
- `ext4_verity_metadata_pos()`: places verity metadata at the first 64 KiB boundary after `i_size`.
- `pagecache_read()` / `pagecache_write()`: internal reads/writes that can access metadata beyond `i_size`, unlike normal VFS file reads/writes.
- `ext4_begin_enable_verity()`: rejects DAX and concurrent verity enablement, attaches jbd2 inode/quota state, converts inline data, requires extent-based files, truncates post-EOF blocks, and adds the inode to the orphan list.
- `ext4_write_verity_descriptor()`: writes the descriptor after the Merkle tree on a filesystem block boundary and stores descriptor size in the last four bytes of the last allocated block.
- `ext4_end_enable_verity()`: writes descriptor, waits for all data and metadata writeback, marks fast commit ineligible, removes the orphan entry, sets `EXT4_INODE_VERITY`, and cleans up on failure.
- Descriptor lookup: `ext4_get_verity_descriptor_location()` finds the last extent, reads descriptor size, validates descriptor position, and reports corruption when layout is invalid.
- Merkle tree operations: offset fs-verity page/block indexes by the metadata start before delegating to generic read/readahead or internal write.
- `ext4_verityops`: operation table wired into `super.c` when `CONFIG_FS_VERITY` is enabled.

## Dependencies And Integration
Uses ext4 extents, journaling, orphan handling, quota initialization, inline-data conversion, filemap writeback, and generic fs-verity Merkle tree helpers. It is registered through `sb->s_vop` during mount.

## Behavioral Notes
Ext4 stores verity metadata beyond EOF so userspace cannot see it through normal file reads, while encrypted files still encrypt the metadata because it lives in file contents rather than xattrs. Orphan-list tracking makes interrupted enablement recoverable: unfinished metadata past EOF can be truncated during cleanup.

## Risk Notes
Descriptor discovery depends on the last allocated extent, so `ext4_begin_enable_verity()` first removes unrelated post-EOF blocks. Crash consistency depends on writing all pages before clearing the in-progress state and before persisting the verity inode flag. Corrupt extent layout or descriptor-size data is treated as filesystem corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/verity.c -->