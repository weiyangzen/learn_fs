# Group Research: group_752_linux_sources_os_linux_linux_fs_f2fs_super_c_sources_os_linux_linux__d5ff6d23bc70

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`. This grouped report covers the requested Linux F2FS superblock/sysfs/verity/xattr files plus FAT Kconfig and build metadata.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/super.c -->
# File Research: sources/os/linux/linux/fs/f2fs/super.c

Implements F2FS filesystem registration, mount/remount option parsing, superblock initialization and teardown, checkpoint state transitions, quota integration, encryption/verity/export hooks, and major superblock operations.

Key behavior:
- Defines the F2FS `file_system_type`, fs-context operations, `super_operations`, export operations, fscrypt operations, and module init/exit paths.
- Parses the full modern `fs_context` mount option set, including GC mode, discard, inline xattr/data/dentry, quota options, allocation/fsync modes, dummy encryption, inline crypto, checkpoint enable/disable/merge, compression, ATGC, discard unit, memory mode, error policy, NAT bits, and lookup mode.
- Tracks parsed option deltas through `f2fs_fs_context::opt_mask`, `spec_mask`, and `qname_mask`, then validates and applies them to `sbi->mount_opt`.
- Validates option consistency against device and on-disk features: readonly feature, zoned devices, discard requirements, device aliasing, quota feature state, dummy encryption, compression support, casefold/Unicode support, inline xattr sizing, LFS/ATGC incompatibility, and flush-merge/read-only constraints.
- Supplies default mount options and runtime defaults, including extent cache, discard defaults, active logs, inline features, checkpoint merge, lazytime, flush merge, fsync mode, compression defaults, memory mode, error policy, and lookup mode.
- Implements fault injection setup when enabled, including named fault types, rate/type/timeout updates, and lock-timeout simulation.
- Creates and destroys global caches/subsystems during module init/exit: inode cache, node/segment/checkpoint/recovery/extent/GC caches, sysfs, shrinker, stats, post-read processing, iostat, bio caches, bioset, compression pools/cache, casefold cache, and xattr cache.
- Provides inode lifecycle helpers:
  - `f2fs_alloc_inode()` initializes F2FS-specific inode state, dirty lists, semaphores, GC locks, xattr lock, compression and writeback counters.
  - `f2fs_drop_inode()` handles checkpoint-disabled meta/node inode dropping and avoids writeback/GC eviction deadlocks.
  - `f2fs_inode_dirtied()` and `f2fs_inode_synced()` maintain dirty inode accounting and atomic-write dirty state.
- Implements `put_super`, `sync_fs`, freeze/unfreeze, statfs, shutdown, and mount option display.
- `f2fs_put_super()` unregisters sysfs/proc entries, disables quota, stops checkpointing, writes unmount checkpoints when needed, drains discards, releases orphan/ino tracking, flushes writes, tears down compression/node/meta/segment managers, destroys stats and internal caches, frees options, unloads Unicode encoding, and invalidates block devices.
- `f2fs_sync_fs()` issues a checkpoint on synchronous sync unless checkpointing is disabled, a checkpoint error exists, or POR recovery is active.
- `f2fs_statfs()` reports block/inode capacity using user block count, valid user blocks, unusable block count, root reservations, and quota project limits when applicable.
- Implements checkpoint disable/enable:
  - Disabling checkpoint may force urgent foreground GC to reduce unusable blocks before writing a pause checkpoint.
  - Enabling checkpoint flushes dirty data/skipped writes, clears CP-disabled state, syncs the filesystem, and flushes pending checkpoint thread work.
- Implements remount through `__f2fs_remount()`, preserving old options for rollback and coordinating GC thread, flush-merge thread, discard thread, checkpoint state, checkpoint thread, quota suspend/resume, read-only transitions, and unsupported dynamic option changes.
- Implements quota support when configured:
  - Handles legacy quota file names and quota feature inodes.
  - Provides quota file read/write using pagecache operations.
  - Enables quota tracking from quota inodes or quota files.
  - Synchronizes, turns on/off, and marks quota repair flags after failures.
  - Provides `dquot_operations` and `quotactl_ops`.
- Registers fscrypt callbacks:
  - Stores encryption context in F2FS xattrs.
  - Rejects encrypting the root directory when lost+found is required.
  - Supplies dummy policy, stable inode, and multi-device lookup hooks.
- Registers fs-verity operations via `f2fs_verityops` when configured.
- Supplies NFS export file-handle translation through generic inode-number based helpers.
- Computes maximum file blocks from F2FS direct, indirect, and double-indirect node fanout, with an fscrypt IV data-unit compatibility cap.
- Reads both raw superblock copies, validates magic, checksum, block/sector geometry, segment layout, device segment totals, extension counts, checkpoint payload limits, reserved inode numbers, and metadata area boundaries.
- Repairs in-memory or on-disk superblock segment alignment when main-area end is smaller than segment-area end and writes are allowed.
- Validates checkpoint contents: metadata sizing, overprovision/reserved segments, user and valid block counts, node count, current segment numbers/offsets, duplicate current segments, SIT/NAT bitmap sizes, checksum layout, NAT bits payload space, and checkpoint error state.
- Initializes `f2fs_sb_info` geometry, counters, locks, intervals, GC and allocation policy, summary layout, node limits, dirty page counters, IO state, and lock-priority defaults.
- Handles zoned block devices by reporting zones, tracking sequential zones, enforcing single zone capacity, checking max open zones, and deriving zone geometry.
- Scans multi-device and zoned-device layouts, opens secondary block devices, maps per-device segment/block ranges, and records logical block-size alignment.
- Sets up casefold Unicode encoding from the superblock when available and rejects casefold filesystems without Unicode support.
- `f2fs_fill_super()` is the central mount path:
  - Allocates and initializes `sbi`.
  - Sets block size and reads/validates the raw superblock.
  - Applies mount options and superblock feature hooks.
  - Initializes IO, iostat, percpu counters, page-array cache, meta inode, checkpoint, device list, post-read workqueue, extent/ino/fsync tracking, checkpoint thread, segment manager, node manager, GC manager, stats, node inode, root inode/dentry, compression inode, sysfs, quota, orphan recovery, fsync recovery, write-pointer repair, in-memory current segments, checkpoint enable/disable, GC thread, and shrinker membership.
  - Has structured cleanup labels for every partially initialized subsystem and retries once after failed fsync recovery.
- Handles critical errors by setting checkpoint error flags, recording error/stop reasons asynchronously, applying `errors=` policy, optionally panicking, and preventing further updates.
- `kill_f2fs_super()` stops GC/discard, writes final checkpoints if needed, truncates compression cache, delegates to `kill_block_super()`, and frees device/sbi state after keyring teardown.

Important interactions:
- Mount option validation is tightly coupled to on-disk feature bits in `raw_super`, runtime state in `sbi`, and Kconfig-dependent support for quota, compression, encryption, zoned block devices, and Unicode.
- Superblock initialization wires together most other F2FS modules: node manager, segment manager, checkpoint, GC, recovery, xattr, verity, compression, iostat, and sysfs.
- Checkpoint-disabled mode affects inode dropping, statfs free-space reporting, remount behavior, quota flushing, and unmount cleanup.
- Error handling records stop reasons in the superblock through deferred work and informs fsck through SBI/CP flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/sysfs.c -->
# File Research: sources/os/linux/linux/fs/f2fs/sysfs.c

Implements F2FS sysfs and procfs visibility/control surfaces.

Key behavior:
- Creates the global `/sys/fs/f2fs` kset, `/sys/fs/f2fs/features`, `/sys/fs/f2fs/tuning`, and `/proc/fs/f2fs`.
- For each mounted F2FS instance, registers:
  - `/sys/fs/f2fs/<sb-id>/`
  - `/sys/fs/f2fs/<sb-id>/stat/`
  - `/sys/fs/f2fs/<sb-id>/feature_list/`
  - `/proc/fs/f2fs/<sb-id>/`
- Defines `struct f2fs_attr` for per-superblock attributes and `struct f2fs_base_attr` for global feature/tuning attributes.
- Uses `__struct_ptr()` plus generated offset/size metadata to read and write fields from GC thread state, segment manager state, discard control, node manager state, `f2fs_sb_info`, fault-injection state, checkpoint request control, and ATGC state.
- Provides read-only show helpers for dirty/free/overprovisioned segments, lifetime writes, checkpoint status, discard state, ATGC state, GC mode, supported on-disk features, reserved/unusable blocks, encoding, lookup mode, mounted time, moved blocks, average valid blocks, defrag blocks, and main block address.
- Implements generic value show/store by field size for 1-, 2-, 4-, and 8-byte fields.
- Special-cases `extension_list` to display and update cold/hot extension lists under `sbi->sb_lock`, committing the superblock and rolling back the in-memory update if the commit fails.
- Special-cases `ckpt_thread_ioprio` to parse `rt,<level>` and `be,<level>`, update checkpoint-thread IO priority, and apply it to the running checkpoint thread when checkpoint merge is enabled.
- Special-cases fault-injection attributes to rebuild fault rate/type/timeout and optionally simulate lock timeout.
- Validates writes for discard controls, migration granularity, GC urgent/idle modes, GC remaining trials, zoned GC thresholds, iostat period, zoned allocation policy, compression counters and thresholds, ATGC ratios, GC segment mode, fragmentation knobs, atomic-write counters, extent age thresholds, read extent count, IPU policy, directory level, reserved pin sections, boosted GC knobs, background-GC IO awareness, allocation-section policy, lock-priority knobs, and critical task priority.
- Uses `s_umount` read locking for GC-related writes to avoid races with unmount.
- Exposes many generated attribute groups:
  - GC thread timings and boosting.
  - Segment manager IPU and reserved segment controls.
  - Discard command controls.
  - Node manager thresholds.
  - Superblock intervals, IO flags, read-ahead, fragmentation, compression, atomic write, extent cache, zoned, reserved pin, allocation, and lock-priority knobs.
  - Fault injection.
  - Checkpoint request control.
  - ATGC controls.
- Exposes global kernel-supported features as `/sys/fs/f2fs/features/*`, with conditional entries for encryption, block zoned, verity, casefold, compression, etc.
- Exposes per-filesystem on-disk feature support under `feature_list`, returning `supported` or `unsupported` for each feature bit.
- Implements `/sys/fs/f2fs/tuning/reclaim_caches_kb` to report donated cache size and trigger cache reclamation.
- Implements procfs single-file reports for:
  - `segment_info`
  - `segment_bits`
  - `victim_bits`
  - `discard_plist_info`
  - `disk_map`
  - `donation_list`
  - `inject_stats` when fault injection is enabled
  - `iostat_info` when iostat is enabled
- Proc reports expose detailed segment validity/type maps, SIT bitmaps/mtime, victim section bitmap, discard pending-list distribution, block address layout, multi-device map, donated-file cache state, and fault injection counts.
- Uses kobject release completions during unregister to ensure per-instance sysfs objects are fully released before teardown continues.

Important interactions:
- `super.c` calls `f2fs_init_sysfs()` at module init, `f2fs_register_sysfs()` during mount, `f2fs_unregister_sysfs()` during unmount/error cleanup, and `f2fs_exit_sysfs()` during module exit.
- Many sysfs writes directly affect runtime GC, discard, checkpoint, compression, iostat, zoned allocation, locking, and allocation behavior, so validation in this file is part of F2FS runtime safety.
- Procfs readers inspect live segment/discard/inode structures and use the mounted superblock as `seq_file` private data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/verity.c -->
# File Research: sources/os/linux/linux/fs/f2fs/verity.c

Implements F2FS-specific `fsverity_operations`.

Key behavior:
- Stores fs-verity metadata past EOF, starting at the first 64 KiB boundary after `i_size`.
- Uses pagecache-level read/write helpers because verity metadata must be read and written beyond `i_size`, and enabling verity may use a read-only file descriptor.
- `pagecache_write()` bounds metadata writes against `max_file_blocks(inode)` and writes through the address-space `write_begin`/`write_end` path.
- Uses a compact F2FS verity xattr containing:
  - format version
  - descriptor size
  - descriptor position in file data
- Stores only the descriptor location in the xattr because verity metadata must be encrypted when the file is encrypted, while F2FS xattrs are not encrypted.
- `f2fs_begin_enable_verity()` rejects concurrent verity enable, rejects atomic files, initializes quota, converts inline data out of the inode, and sets `FI_VERITY_IN_PROGRESS`.
- `f2fs_end_enable_verity()` writes the descriptor after the Merkle tree, flushes all file/verity pages, sets the verity xattr, sets the inode verity flag, persists inode flags, and clears in-progress state.
- On enable failure, truncates cached and on-disk verity metadata beyond `i_size`, takes the inode GC write semaphore to prevent GC from re-instantiating pages, and marks the filesystem for fsck if truncation fails.
- `f2fs_get_verity_descriptor()` reads and validates the descriptor-location xattr, checks bounds and overflow, reports corrupted verity xattrs through `f2fs_handle_error()`, and reads the descriptor from pagecache.
- Merkle tree page read, readahead, and write operations translate fs-verity-relative offsets by the F2FS metadata start position.
- Exports `f2fs_verityops` with begin/end enable, descriptor lookup, Merkle page read, readahead, and Merkle block write callbacks.

Important interactions:
- `super.c` installs `f2fs_verityops` into `sb->s_vop` when `CONFIG_FS_VERITY` is enabled.
- Depends on F2FS xattr APIs for the verity descriptor-location xattr.
- Depends on F2FS quota, inline-data conversion, truncate, inode dirtying, GC locking, and corruption/error reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/verity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/xattr.c -->
# File Research: sources/os/linux/linux/fs/f2fs/xattr.c

Implements F2FS extended attribute handlers, xattr lookup/read/write/list/set operations, security xattr initialization, and the inline xattr slab cache.

Key behavior:
- Defines handlers for `user.*`, `trusted.*`, `security.*`, and F2FS `system.advise`.
- `user.*` xattrs are gated by the `XATTR_USER` mount option.
- `trusted.*` listing requires `CAP_SYS_ADMIN`.
- `system.advise` reads and updates `F2FS_I(inode)->i_advise`, allowing only owner/capable writers and only modifiable advise bits.
- Security xattrs are initialized through `security_inode_init_security()` when `CONFIG_F2FS_FS_SECURITY` is enabled.
- Maintains handler maps for VFS xattr dispatch and prefix filtering in `listxattr`.
- Allocates the common inline-xattr buffer size from `inline_xattr_slab`; larger temporary xattr buffers use `f2fs_kzalloc()`.
- Supports xattrs split across:
  - inline xattr space inside the inode node page
  - one external xattr node block referenced by `F2FS_I(inode)->i_xattr_nid`
- `__find_xattr()` iterates xattr entries with boundary checks against the valid buffer end and can report the last valid address for inline/external searches.
- `lookup_all_xattrs()` reads inline xattrs first, then the xattr node block if present, searches for the requested entry, detects corrupted layouts, marks `SBI_NEED_FSCK`, and calls `f2fs_handle_error(ERROR_CORRUPTED_XATTR)`.
- `read_all_xattrs()` builds a complete temporary xattr image, initializes a missing header with `F2FS_XATTR_MAGIC`, and supports empty xattr state.
- `write_all_xattrs()` writes the temporary xattr image back:
  - Allocates a new xattr node nid if needed.
  - Updates inline xattr space when present.
  - Truncates the xattr node if the new xattr set fits inline.
  - Writes or creates the external xattr node block when needed.
  - Marks affected folios dirty and handles nid allocation success/failure.
- `f2fs_getxattr()` validates name length, takes `i_xattr_sem` unless using a caller-provided inode folio, looks up the entry, validates buffer size and in-buffer bounds, copies the value, and returns the value size.
- `f2fs_listxattr()` reads all xattrs, filters entries by handler/list permissions, emits prefixed names, detects corrupt entry boundaries, and returns required/used buffer size.
- `__f2fs_setxattr()` handles create/replace/delete/update semantics:
  - Validates name and maximum value length.
  - Reads all xattrs and searches for the target entry.
  - Attempts xattr recovery if corruption is found and no xattr node exists.
  - Enforces `XATTR_CREATE`/`XATTR_REPLACE`.
  - Skips rewriting identical values.
  - Checks free space before insertion.
  - Removes old entries with `memmove()`.
  - Writes a new aligned entry and explicit null terminator.
  - Persists with `write_all_xattrs()`.
  - Sets encrypted inode state when the encryption context xattr is written.
  - For directory xattr changes, requests checkpoint or records `XATTR_DIR_INO` depending on fsync mode.
  - Restores ACL mode state when `FI_ACL_MODE` is set.
  - Updates ctime and marks the inode dirty.
- `f2fs_setxattr()` checks checkpoint/error readiness, initializes quota, supports the metadata-initialization fast path with caller-provided folio, otherwise balances FS, takes the global F2FS operation lock and inode xattr write semaphore, calls the internal setter, unlocks, and updates request time.
- Initializes and destroys the `f2fs_xattr_entry` slab cache used for default inline xattr temporary buffers.

Important interactions:
- Used by VFS xattr operations through `f2fs_xattr_handlers`, by fscrypt for encryption contexts, by fs-verity for descriptor-location xattrs, by security initialization, and by inode metadata creation.
- Corruption detection feeds into `SBI_NEED_FSCK` and F2FS critical error handling.
- The inline/external split is defined by `xattr.h` macros and by inode feature layout.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/xattr.h -->
# File Research: sources/os/linux/linux/fs/f2fs/xattr.h

Defines the F2FS on-disk xattr format, xattr namespace constants, layout macros, and exported xattr APIs.

Key behavior:
- Defines `F2FS_XATTR_MAGIC` and `F2FS_XATTR_REFCOUNT_MAX`.
- Defines F2FS xattr indexes:
  - user
  - POSIX ACL access/default
  - trusted
  - Lustre
  - security
  - F2FS advise
  - encryption
  - verity
- Defines compact names for internal encryption and verity xattrs: `"c"` and `"v"`.
- Defines `struct f2fs_xattr_header` with magic, refcount, and reserved fields.
- Defines `struct f2fs_xattr_entry` with name index, name length, little-endian value size, and flexible name/value storage.
- Provides xattr traversal and sizing macros:
  - `XATTR_HDR`, `XATTR_ENTRY`, `XATTR_FIRST_ENTRY`
  - `XATTR_ALIGN`, `ENTRY_SIZE`, `XATTR_NEXT_ENTRY`
  - `IS_XATTR_LAST_ENTRY`, `list_for_each_xattr`
  - `VALID_XATTR_BLOCK_SIZE`, `XATTR_PADDING_SIZE`
  - `XATTR_SIZE`, `MIN_OFFSET`, `MAX_VALUE_LEN`
- Defines inline xattr sizing limits based on inode address space, extra attributes, reserved inline space, and inline dentry minimums.
- Documents the combined layout: inline xattr space plus one xattr block, followed by the node footer.
- Exports xattr handlers and APIs when `CONFIG_F2FS_FS_XATTR` is enabled.
- Provides `-EOPNOTSUPP` stubs and null handler/list definitions when xattrs are disabled.
- Exports `f2fs_init_security()` when `CONFIG_F2FS_FS_SECURITY` is enabled and provides a no-op stub otherwise.

Important interactions:
- `xattr.c` implements the APIs and uses these layout macros for all on-disk parsing/writing.
- `super.c` installs `f2fs_xattr_handlers` into `sb->s_xattr`.
- `verity.c` and fscrypt paths depend on the internal verity/encryption xattr indexes and names.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/Kconfig -->
# File Research: sources/os/linux/linux/fs/fat/Kconfig

Defines Kconfig options for Linux FAT-family filesystem support.

Key behavior:
- `FAT_FS` is the shared base tristate for FAT-family filesystems.
  - Selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`.
  - Provides common FAT support but is not directly sufficient for mounting unless `MSDOS_FS` or `VFAT_FS` is enabled.
  - Builds as module `fat` when modular.
- `MSDOS_FS` enables classic MS-DOS FAT filesystem support.
  - Selects `FAT_FS`.
  - Builds as module `msdos` when modular.
  - Documentation notes that Windows long filenames require VFAT instead.
- `VFAT_FS` enables FAT support with Windows long filenames.
  - Selects `FAT_FS`.
  - Builds as module `vfat` when modular.
  - Points users to `Documentation/filesystems/vfat.rst`.
- `FAT_DEFAULT_CODEPAGE` sets the default FAT codepage.
  - Depends on `FAT_FS`.
  - Defaults to `437`.
  - Can be overridden by the `codepage` mount option.
- `FAT_DEFAULT_IOCHARSET` sets the default VFAT input/output charset.
  - Depends on `VFAT_FS`.
  - Defaults to `iso8859-1`.
  - Can be overridden by the `iocharset` mount option.
  - Explicitly discourages setting this to `utf8` directly.
- `FAT_DEFAULT_UTF8` controls whether the FAT `utf8` mount option is enabled by default.
  - Depends on `VFAT_FS`.
  - Defaults to `n`.
  - Can be overridden per mount with `utf8=0`.
- `FAT_KUNIT_TEST` builds FAT KUnit tests.
  - Depends on `KUNIT && FAT_FS`.
  - Defaults to `KUNIT_ALL_TESTS`.
  - Builds FAT filesystem unit tests when enabled.

Important interactions:
- The Makefile uses these config symbols to include `fat.o`, `vfat.o`, `msdos.o`, and `fat_test.o`.
- FAT charset/codepage defaults are runtime mount-option defaults consumed by FAT/VFAT implementation files outside this group.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fat/Makefile -->
# File Research: sources/os/linux/linux/fs/fat/Makefile

Defines object composition for Linux FAT-family filesystem modules.

Key behavior:
- Builds `fat.o` when `CONFIG_FAT_FS` is enabled.
- Builds `vfat.o` when `CONFIG_VFAT_FS` is enabled.
- Builds `msdos.o` when `CONFIG_MSDOS_FS` is enabled.
- Composes the common FAT object from:
  - `cache.o`
  - `dir.o`
  - `fatent.o`
  - `file.o`
  - `inode.o`
  - `misc.o`
  - `nfs.o`
- Composes VFAT from `namei_vfat.o`.
- Composes MSDOS from `namei_msdos.o`.
- Builds `fat_test.o` when `CONFIG_FAT_KUNIT_TEST` is enabled.

Important interactions:
- Mirrors the Kconfig split between shared FAT infrastructure, VFAT long-name support, MSDOS name lookup, and KUnit tests.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fat/Makefile -->