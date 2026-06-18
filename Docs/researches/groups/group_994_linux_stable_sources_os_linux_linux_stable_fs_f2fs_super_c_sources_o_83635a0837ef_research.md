# Group Research: group_994_linux_stable_sources_os_linux_linux_stable_fs_f2fs_super_c_sources_o_83635a0837ef

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/super.c

## Purpose
`super.c` is the F2FS superblock, mount, remount, module lifecycle, and filesystem-wide policy implementation. It wires F2FS into the VFS via `file_system_type`, `super_operations`, fscrypt, fsverity, export/NFS, quota, sysfs, shrinker, and mount option handling.

## Main Responsibilities
- Defines and parses all F2FS mount parameters through `fs_context` (`f2fs_parse_param`, `f2fs_context_ops`).
- Applies and validates mount options for GC, discard, quotas, compression, encryption, inline xattrs/data/dentries, checkpoint disable/merge, zoned devices, memory mode, error policy, lookup mode, NAT bits, and fault injection.
- Implements mount and remount flow through `f2fs_fill_super`, `f2fs_get_tree`, and `__f2fs_remount`.
- Reads, validates, repairs, and commits F2FS superblocks and checkpoints.
- Owns module initialization/exit ordering for all global F2FS caches and subsystems.
- Handles unmount teardown through `f2fs_put_super` and `kill_f2fs_super`.
- Implements quota integration, fscrypt callbacks, export operations, statfs, sync, freeze/unfreeze, shutdown, inode allocation/free/drop/dirty tracking, and critical error handling.

## Key Data and Interfaces
- `struct f2fs_fs_context` carries parsed mount options, changed option masks, spec masks, and quota-name changes before applying them to `struct f2fs_sb_info`.
- `f2fs_param_specs[]` defines the supported mount option grammar.
- `f2fs_sops` provides VFS superblock operations.
- `f2fs_cryptops` provides fscrypt integration when encryption is enabled.
- `f2fs_export_ops` enables file-handle based NFS export support.
- `f2fs_fs_type` registers the filesystem as `"f2fs"`.
- `f2fs_inode_cachep`, `f2fs_shrinker_info`, and the casefold slab are global resources created and destroyed at module load/unload.

## Mount Flow
`f2fs_fill_super` performs the full mount sequence:
1. Allocates `f2fs_sb_info`, initializes locks and inode lists.
2. Sets block size and reads both raw superblock copies.
3. Applies default and user-specified options, then validates consistency.
4. Sets VFS callbacks, flags, UUID, sysfs block-device name, and fscrypt/fsverity/xattr hooks.
5. Initializes write IO, `sbi` geometry, iostat, percpu counters, page-array cache, meta inode, checkpoint, devices, post-read workqueue, extent/ino/fsync tracking, checkpoint request control, segment manager, node manager, GC manager, stats, node inode, root inode, compression inode, and sysfs/procfs entries.
6. Enables quotas when needed, recovers orphan inodes and fsync data, resolves checkpoint-disabled state, starts background GC, joins the global shrinker, applies tuning, and announces the mounted checkpoint version.
7. Uses detailed unwind labels to destroy partially initialized state on failure.

## Validation and Recovery
- `sanity_check_raw_super` checks magic, checksum, block/sector geometry, segment counts, area boundaries, device layout, extension counts, checkpoint payload, and reserved inode numbers.
- `f2fs_sanity_check_ckpt` validates checkpoint metadata, current segment ranges, duplicate curseg usage, SIT/NAT bitmap sizes, NAT bits layout, and CP error state.
- `read_raw_super_block` accepts the first valid copy and marks recovery if either copy is bad.
- `f2fs_commit_super` writes backup then primary superblock, updating superblock CRC when appropriate.
- `f2fs_handle_error`, `f2fs_stop_checkpoint`, and `f2fs_handle_critical_error` record persistent error/stop reasons and enforce `errors=` policy.

## Remount and Checkpoint Policy
`__f2fs_remount` snapshots old mount options, validates new options, applies changes, manages RW/RO transition, quota suspend/resume, GC/flush/discard/checkpoint threads, checkpoint enable/disable, and restores old state on failure. Some options cannot be switched dynamically, including ATGC, extent caches, compression cache, discard unit class, and NAT bits.

`f2fs_disable_checkpoint` runs foreground GC until unusable blocks are under the configured cap, writes a pause checkpoint, and records disabled state. `f2fs_enable_checkpoint` flushes dirty/skipped data, moves dirty blocks to prefree, clears disabled state, and syncs.

## Quota Integration
With `CONFIG_QUOTA`, this file implements quota read/write, quota-on/off/sync, quota sysfile loading, project quota statfs limiting, dquot operations, and quotactl operations. It detects corrupted quota flags, marks repair-needed state, and handles quota recovery around orphan/fsync recovery.

## Dependencies
- Internal F2FS modules: `f2fs.h`, `node.h`, `segment.h`, `xattr.h`, `gc.h`, `iostat.h`.
- Closely coupled files in this group:
  - Uses `f2fs_xattr_handlers`, `f2fs_getxattr`, and `f2fs_setxattr` from `xattr.c`/`xattr.h`.
  - Installs `f2fs_verityops` from `verity.c` into `sb->s_vop`.
  - Calls `f2fs_init_sysfs`, `f2fs_register_sysfs`, and unregister/exit functions from `sysfs.c`.
- Kernel subsystems: VFS, fs_context, block layer, quota, fscrypt, fsverity, Unicode/casefolding, sysfs/procfs, shrinkers, workqueues, zoned block devices.

## Notable Edge Cases
- Zoned devices force discard and LFS-oriented constraints.
- Read-only hardware can allow mount only if no write recovery is required.
- `checkpoint=disable` is rejected on read-only mounts.
- Root-reserved block/node settings are capped to 12.5%.
- Casefold filesystems require `CONFIG_UNICODE`.
- Filesystems with readonly feature can only mount read-only.
- Superblock alignment may be fixed in memory and committed if writable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/sysfs.c

## Purpose
`sysfs.c` implements F2FS runtime observability and tuning through `/sys/fs/f2fs` and `/proc/fs/f2fs`.

## Main Responsibilities
- Creates the global `/sys/fs/f2fs` kset plus `features` and `tuning` kobjects.
- Creates per-mounted-filesystem kobjects for the mount, `stat`, and `feature_list`.
- Exposes many per-filesystem tunables and counters through generated `f2fs_attr` objects.
- Registers procfs diagnostic files under `/proc/fs/f2fs/<device>`.
- Cleans up all kobjects and procfs entries on unmount and module exit.

## Key Data and Interfaces
- `struct f2fs_attr` represents per-superblock sysfs entries, with target struct type, offset, size, show/store callbacks, and optional feature id.
- `struct f2fs_base_attr` represents global feature/tuning entries.
- `__struct_ptr` maps an attribute’s target enum to `f2fs_sb_info`, GC thread, segment manager, discard controller, node manager, stat info, checkpoint request controller, ATGC state, or fault injection state.
- Exported lifecycle functions:
  - `f2fs_init_sysfs`
  - `f2fs_exit_sysfs`
  - `f2fs_register_sysfs`
  - `f2fs_unregister_sysfs`

## Sysfs Coverage
The file exposes:
- Segment and space counters: dirty/free/overprovisioned segments, unusable blocks, reserved blocks, lifetime written KB.
- GC controls: urgent/idle modes, sleep times, migration granularity, victim search, pin thresholds, reclaimed segments, zoned GC tuning.
- Discard controls: request limits, issue timings, granularity, IO awareness, urgent utilization, pending/issued/queued discard counters.
- Node/segment manager tuning: IPU policy, NID read-ahead, dirty NAT ratio, SSR thresholds, reserved segments.
- Checkpoint controls: checkpoint interval and checkpoint thread IO priority.
- Compression counters and thresholds when configured.
- Atomic write counters.
- Extent cache age thresholds and read extent limits.
- Casefold encoding and effective lookup mode.
- Feature reporting for runtime-supported features and on-disk per-instance features.
- Fault injection rate/type/timeout when configured.
- Global cache donation tuning via `reclaim_caches_kb`.

## Store Validation
`__sbi_store` contains per-attribute validation rather than blindly writing offsets. It bounds discard, GC, compression, ATGC, fragmentation, extent, allocation, task-priority, and zoned-device values; wakes GC/discard threads for urgent modes; updates checkpoint thread IO priority; resets selected counters only when writing zero; and requires `CAP_SYS_NICE` for critical task priority changes.

## Procfs Diagnostics
Per-mount proc files include:
- `segment_info`
- `segment_bits`
- `victim_bits`
- `discard_plist_info`
- `disk_map`
- `donation_list`
- `inject_stats` when fault injection is enabled
- `iostat_info` when iostat is enabled elsewhere

These seq_file handlers dump segment state, victim section maps, discard pending-list distribution, on-disk layout, multi-device mappings, donated cache file state, and injected fault counters.

## Dependencies
- Uses F2FS core structures from `f2fs.h`, `segment.h`, `gc.h`, and `iostat.h`.
- Called from `super.c` during module init/exit and mount/unmount.
- Reads and mutates live `f2fs_sb_info`, segment manager, discard controller, GC thread, ATGC, checkpoint, and stat state.

## Notable Edge Cases
- GC-related stores take `s_umount` read lock using trylock and may return `-EAGAIN`.
- Several attributes are only present under Kconfig guards.
- Unregistration waits for kobject release completions to avoid use-after-free during unmount.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/verity.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/verity.c

## Purpose
`verity.c` implements F2FS `fsverity_operations`, enabling fs-verity metadata storage, descriptor lookup, Merkle tree IO, and enable/cleanup flow.

## Main Responsibilities
- Stores verity metadata beyond normal file size, starting at the first 64 KiB boundary after `i_size`.
- Reads and writes metadata through pagecache helpers that can access pages beyond `i_size`.
- Records descriptor location in a small F2FS verity xattr rather than storing the descriptor itself in xattrs.
- Hooks F2FS into the generic fs-verity layer through `f2fs_verityops`.

## Key Data and Interfaces
- `f2fs_verity_metadata_pos(inode)` returns `round_up(i_size, 65536)`.
- `struct fsverity_descriptor_location` stores version, descriptor size, and descriptor position.
- `f2fs_begin_enable_verity` rejects concurrent verity enable and atomic files, initializes quotas, converts inline data, and marks `FI_VERITY_IN_PROGRESS`.
- `f2fs_end_enable_verity` writes the descriptor, flushes file metadata, sets the verity xattr, sets the inode verity flag, and marks inode dirty.
- `f2fs_get_verity_descriptor` reads descriptor location from xattr, validates bounds, and reads the descriptor.
- `f2fs_read_merkle_tree_page`, `f2fs_readahead_merkle_tree`, and `f2fs_write_merkle_tree_block` translate fs-verity offsets into F2FS metadata offsets.

## Failure Handling
If enablement fails, `f2fs_end_enable_verity` truncates cached and on-disk metadata beyond `i_size`, protects cleanup with `i_gc_rwsem[WRITE]` so GC cannot reinstantiate pages, clears `FI_VERITY_IN_PROGRESS`, and marks the filesystem for fsck if truncation fails.

## Dependencies
- Uses `f2fs_getxattr` and `f2fs_setxattr` from the xattr layer.
- Uses `max_file_blocks` from `super.c` to enforce max metadata position.
- Installed by `super.c` through `sb->s_vop = &f2fs_verityops` when `CONFIG_FS_VERITY` is enabled.

## Notable Edge Cases
- Verity cannot be enabled for atomic files.
- Descriptor xattr corruption triggers `ERROR_CORRUPTED_VERITY_XATTR`.
- Xattrs cannot hold the descriptor directly because F2FS xattrs are small and not encrypted, while verity metadata must be encrypted for encrypted files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/verity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/xattr.c

## Purpose
`xattr.c` implements F2FS extended attribute handlers, storage lookup, listing, mutation, security initialization, and xattr cache lifecycle.

## Main Responsibilities
- Provides VFS xattr handlers for `user.*`, `trusted.*`, `security.*`, and F2FS `system.advise`.
- Implements F2FS xattr get/list/set operations over inline inode xattr space plus an optional xattr node block.
- Initializes inode security xattrs through LSM callbacks when `CONFIG_F2FS_FS_SECURITY` is enabled.
- Maintains an inline-xattr slab cache for the default inline xattr allocation size.
- Detects malformed xattr entries, marks fsck-needed state, and reports F2FS corruption errors.

## Key Data and Interfaces
- Exported handlers:
  - `f2fs_xattr_user_handler`
  - `f2fs_xattr_trusted_handler`
  - `f2fs_xattr_advise_handler`
  - `f2fs_xattr_security_handler`
  - `f2fs_xattr_handlers[]`
- Exported operations:
  - `f2fs_getxattr`
  - `f2fs_setxattr`
  - `f2fs_listxattr`
  - `f2fs_init_security`
  - `f2fs_init_xattr_cache`
  - `f2fs_destroy_xattr_cache`

## Storage Model
F2FS combines:
- Inline xattr area inside the inode node.
- Optional external xattr node block referenced by `F2FS_I(inode)->i_xattr_nid`.

`read_all_xattrs` builds a temporary contiguous image of inline plus external xattrs. `write_all_xattrs` writes back inline content and allocates/truncates the xattr node block as needed.

## Lookup and Mutation Flow
- `lookup_all_xattrs` reads the required storage, searches inline first, then external storage, and returns the matching entry or `-ENODATA`.
- `f2fs_getxattr` validates name length, locks `i_xattr_sem` when needed, retrieves the entry, checks caller buffer size, and copies the value.
- `f2fs_listxattr` walks all entries, applies handler visibility rules, and emits prefixed names.
- `f2fs_setxattr` checks checkpoint/error state, initializes quota, balances filesystem space, takes the global F2FS op lock plus `i_xattr_sem`, and calls `__f2fs_setxattr`.
- `__f2fs_setxattr` handles create/replace/remove semantics, same-value shortcut, free-space validation, entry compaction, new entry insertion, encrypted inode flag update, directory checkpoint tracking, ctime update, and dirty marking.

## Special Attributes
- `system.advise` maps to `F2FS_I(inode)->i_advise`; only owner/capable callers may modify selected advise bits.
- Encryption context writes mark the inode encrypted.
- Security xattrs are initialized through `security_inode_init_security`.

## Dependencies
- Defines the xattr operations installed by `super.c` via `sb->s_xattr = f2fs_xattr_handlers`.
- Used by `super.c` fscrypt context callbacks and by `verity.c` descriptor-location storage.
- Depends on F2FS node/page helpers from `f2fs.h` and `segment.h`.

## Notable Edge Cases
- Corrupt xattr entry bounds set `SBI_NEED_FSCK` and call `f2fs_handle_error(ERROR_CORRUPTED_XATTR)`.
- If an inline-only inode has corrupted/missing xattr data during set, the code attempts `f2fs_recover_xattr_data`.
- Values larger than `MAX_VALUE_LEN(inode)` are rejected with `-E2BIG`.
- User xattrs honor the `XATTR_USER` mount option; trusted xattrs require `CAP_SYS_ADMIN` to list.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/xattr.h

## Purpose
`xattr.h` defines F2FS on-disk xattr structures, constants, layout macros, handler declarations, and conditional stubs.

## Main Contents
- Magic and limits:
  - `F2FS_XATTR_MAGIC`
  - `F2FS_XATTR_REFCOUNT_MAX`
- Xattr namespace indexes:
  - user, POSIX ACL access/default, trusted, lustre, security, advise, encryption, verity.
- Reserved internal names:
  - encryption context name `"c"`
  - verity descriptor-location name `"v"`
  - `system.advise`
- On-disk structures:
  - `struct f2fs_xattr_header`
  - `struct f2fs_xattr_entry`
- Layout helpers:
  - `XATTR_HDR`
  - `XATTR_ENTRY`
  - `XATTR_FIRST_ENTRY`
  - `XATTR_ALIGN`
  - `ENTRY_SIZE`
  - `XATTR_NEXT_ENTRY`
  - `IS_XATTR_LAST_ENTRY`
  - `list_for_each_xattr`
  - `XATTR_SIZE`
  - `MIN_OFFSET`
  - `MAX_VALUE_LEN`

## Layout Contract
The header documents that F2FS uses inline xattr space plus one xattr block. Entries are packed after the header, with values stored immediately after names and with a zero terminator marking the end. `MIN_OFFSET` defines the maximum usable xattr region before the node footer.

## Conditional API
When `CONFIG_F2FS_FS_XATTR` is enabled, this header declares the real xattr handlers and operations. Otherwise it supplies `NULL` handlers and `-EOPNOTSUPP` stubs for get/set, plus no-op cache lifecycle functions.

When `CONFIG_F2FS_FS_SECURITY` is disabled, `f2fs_init_security` is a no-op stub.

## Dependencies
- Consumed by `xattr.c`, `super.c`, and `verity.c`.
- Depends on inode-specific helpers/macros from the broader F2FS headers for inline xattr sizing and inode state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/fat/Kconfig

## Purpose
`Kconfig` defines Linux kernel configuration options for FAT-family filesystem support.

## Main Options
- `FAT_FS`: common FAT foundation layer. It is tristate, selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`, and is required by MSDOS and VFAT.
- `MSDOS_FS`: enables classic MSDOS FAT filesystem support and selects `FAT_FS`.
- `VFAT_FS`: enables VFAT/Windows long filename support and selects `FAT_FS`.
- `FAT_DEFAULT_CODEPAGE`: integer default FAT codepage, dependent on `FAT_FS`, default `437`.
- `FAT_DEFAULT_IOCHARSET`: default VFAT charset string, dependent on `VFAT_FS`, default `"iso8859-1"`.
- `FAT_DEFAULT_UTF8`: boolean to enable the FAT `utf8` mount option by default, dependent on `VFAT_FS`, default `n`.
- `FAT_KUNIT_TEST`: tristate KUnit tests for FAT, dependent on `KUNIT && FAT_FS`, defaulting to `KUNIT_ALL_TESTS`.

## Behavior and Dependencies
The configuration separates the shared FAT core from the two mountable frontends. The help text explains that `FAT_FS` alone is just the shared foundation, while `MSDOS_FS` and/or `VFAT_FS` provide usable filesystem support. Charset/codepage options define defaults that can still be overridden at mount time.

## Notable Edge Cases
- If FAT core is built as a module, dependent FAT-family filesystems must also be modules.
- The config text discourages using UTF-8 as the default FAT charset unless explicitly desired.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/fat/Makefile

## Purpose
`Makefile` defines build targets for Linux FAT-family filesystem modules/objects.

## Build Rules
- `obj-$(CONFIG_FAT_FS) += fat.o`
- `obj-$(CONFIG_VFAT_FS) += vfat.o`
- `obj-$(CONFIG_MSDOS_FS) += msdos.o`
- `obj-$(CONFIG_FAT_KUNIT_TEST) += fat_test.o`

## Object Composition
- `fat-y` is built from shared FAT core files:
  - `cache.o`
  - `dir.o`
  - `fatent.o`
  - `file.o`
  - `inode.o`
  - `misc.o`
  - `nfs.o`
- `vfat-y` is built from `namei_vfat.o`.
- `msdos-y` is built from `namei_msdos.o`.

## Dependencies
This file directly reflects the options declared in `fs/fat/Kconfig`, mapping selected kernel config symbols to core, VFAT, MSDOS, and KUnit test build products.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fat/Makefile -->