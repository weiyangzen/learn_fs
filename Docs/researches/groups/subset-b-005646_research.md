# Research: subset-b-005646

This grouped report covers the requested source files in manifest order. Each file section preserves the original source path for the reconciliation splitter.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/super.c -->
# sources/distributed-fs/ceph-client/fs/exfat/super.c

Purpose: Implements the exFAT filesystem superblock/module glue: mount option parsing, fs_context setup, block-device superblock probing, boot-region validation, root inode creation, statfs/show_options, shutdown, and module cache registration.

Important APIs/types/functions: `exfat_sops`, `exfat_fs_type`, `exfat_parameters`, `exfat_parse_param`, `exfat_init_fs_context`, `exfat_get_tree`, `exfat_fill_super`, `__exfat_fill_super`, `exfat_read_boot_sector`, `exfat_verify_boot_region`, `exfat_read_root`, `exfat_set_volume_dirty`, `exfat_clear_volume_dirty`, `exfat_force_shutdown`, `init_exfat_fs`, and `exit_exfat_fs`. It depends on `struct exfat_sb_info`, `struct exfat_mount_options`, `struct boot_sector`, `struct exfat_chain`, and inode/cache helpers declared in `exfat_fs.h` and `exfat_raw.h`.

Control flow: mount begins in `exfat_init_fs_context`, which allocates `exfat_sb_info`, initializes locks/ratelimit state, seeds mount defaults from either current credentials or the remount target, and registers fs_context operations. `exfat_parse_param` mutates the temporary mount options. `get_tree_bdev` calls `exfat_fill_super`, which normalizes `allow_utime`, validates discard support, installs super operations and timestamp bounds, then calls `__exfat_fill_super`. The lower fill routine reads and validates the boot sector, verifies the 12-sector boot region checksum, counts the root cluster chain before directory-entry searches, loads the upcase table and allocation bitmap, fixes an unset root cluster bit, and counts used clusters. The upper fill routine then configures NLS/dentry ops, creates root inode `EXFAT_ROOT_INO`, initializes root inode metadata through `exfat_read_root`, hashes it, and installs `sb->s_root`.

State and persistence behavior: `sbi->boot_bh` holds the boot sector and is marked dirty/synced when volume flags change. `exfat_set_vol_flags` preserves `vol_flags_persistent`, skips on read-only mounts, writes `vol_flags`, and uses `REQ_SYNC | REQ_FUA | REQ_PREFLUSH`. `exfat_put_super` clears dirty state, frees the allocation bitmap, and releases the boot buffer under `s_lock`. `exfat_kill_sb` defers NLS/upcase/sbi freeing with RCU. Mount state includes charset ownership, bitmap state, used cluster counts, FAT/data offsets, root cluster, and volume flags.

Dependencies and integration points: Integrates with VFS `fs_context`, `super_operations`, block-device mounting, NLS, buffer heads, exFAT cache/upcase/bitmap code, dentry operations, inode operations, and block device freeze/thaw for forced shutdown. Remount uses a temporary `exfat_sb_info` and rejects dynamic changes to options cached in dentries or inodes.

Risks: The boot-sector parser is integer- and bounds-sensitive, especially FAT length, cluster count, sector/cluster shifts, and maxbytes calculation. Error cleanup has multiple ownership paths for `boot_bh`, bitmap, NLS, and upcase table. Remount swaps option structures, so charset pointer ownership must remain correct. Forced shutdown disables discard and marks a bit without necessarily syncing data in `NOSYNC`. Bad media/dirty flags are warnings rather than hard failures.

Test signals: Mount valid and corrupt exFAT images; verify boot checksum failures, unsupported sector sizes, bad FAT/data offsets, missing NLS charset, dirty/media-warning logging, read-only dirty-flag behavior, remount option rejection, `statfs` cluster accounting, discard option fallback, and module unload after mounted/unmounted instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exfat/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exportfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/exportfs/Makefile

Purpose: Builds the generic Linux exportfs support object when `CONFIG_EXPORTFS` is enabled.

Important APIs/types/functions: `obj-$(CONFIG_EXPORTFS) += exportfs.o` selects the composite object, and `exportfs-objs := expfs.o` maps that object to `expfs.c`.

Control flow: Kbuild includes `exportfs.o` only for enabled exportfs configurations. There is no runtime control flow in the file; it only controls object inclusion.

State and persistence behavior: No persistent state. The Makefile determines whether the exported helper symbols in `expfs.c` are present in the kernel/module build.

Dependencies and integration points: Integrated with Kconfig symbol `CONFIG_EXPORTFS` and the kernel's composite object convention. NFS export-capable filesystems and fanotify file-handle code depend on the resulting symbols.

Risks: Accidentally changing object names breaks symbol availability for all filesystems relying on exportfs helpers. The SPDX is GPL-2.0-only, matching `expfs.c`.

Test signals: Kernel build with `CONFIG_EXPORTFS=y/m`; confirm `expfs.o` is linked into `exportfs.o` and exported symbols such as `exportfs_encode_fh` and `exportfs_decode_fh` resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exportfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exportfs/expfs.c -->
# sources/distributed-fs/ceph-client/fs/exportfs/expfs.c

Purpose: Provides generic helpers for encoding inodes/dentries into file handles and decoding file handles back into connected dentries for NFS export and related users.

Important APIs/types/functions: Exports `exportfs_encode_inode_fh`, `exportfs_encode_fh`, `exportfs_decode_fh_raw`, and `exportfs_decode_fh`. Key internal helpers are `exportfs_get_name`, `find_acceptable_alias`, `dentry_connected`, `clear_disconnected`, `reconnect_one`, `reconnect_path`, `get_name`, `filldir_one`, and `exportfs_encode_ino64_fid`. It consumes filesystem `struct export_operations` methods such as `encode_fh`, `fh_to_dentry`, `fh_to_parent`, `get_parent`, and `get_name`.

Control flow: Encoding checks whether the filesystem can encode the requested handle. If there is no export operation and the caller only wants a non-decodeable FID, `exportfs_encode_ino64_fid` stores inode number plus generation. Connectable non-directory handles include parent inode information. Decoding first asks the filesystem for a dentry via `fh_to_dentry`, optionally rejects non-directories, and returns disconnected dentries directly when no caller acceptance callback is supplied. With subtree checks, directories are reconnected to root through repeated `get_parent`, name lookup, and `lookup_one_unlocked`; non-directories first search acceptable aliases, then decode/reconnect a parent and verify the child name maps back to the same inode.

State and persistence behavior: No on-disk state is mutated. Runtime dentry-cache state is changed by clearing `DCACHE_DISCONNECTED` after reconnection. Dentry and file references are carefully acquired/released while walking aliases, parents, and directory files.

Dependencies and integration points: Depends on VFS dentries, mounts, path lookup, directory iteration, credentials, kstats, and export operation contracts documented by NFS exporting. `get_name` falls back to opening the parent directory and iterating entries until a matching child inode number is found using `vfs_getattr_nosec` to handle 64-bit inode numbers.

Risks: Race handling is central: renames/removes can occur between parent discovery, name discovery, and lookup. Stale/corrupt filesystems must return `-ESTALE` rather than incorrectly reconnecting an inode. Alias scanning must not leak references while dropping inode locks. The fallback `get_name` is O(directory size) and can be expensive for large directories.

Test signals: NFS export subtree-check tests; decoding handles for renamed, removed, disconnected, and alias-heavy dentries; directory-only decode rejection; filesystems with custom `get_name`; 32-bit host with 64-bit inode numbers; fanotify FID-only encoding with too-small `max_len`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/exportfs/expfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ext2/Kconfig

Purpose: Defines build-time configuration for the deprecated ext2 filesystem driver and optional xattr, POSIX ACL, and security-label features.

Important APIs/types/functions: Kconfig symbols are `EXT2_FS`, `EXT2_FS_XATTR`, `EXT2_FS_POSIX_ACL`, and `EXT2_FS_SECURITY`. `EXT2_FS` selects `BUFFER_HEAD` and `FS_IOMAP`; ACL support selects `FS_POSIX_ACL`.

Control flow: Configuration dependency flow is linear: ext2 enables the core driver; xattrs depend on ext2; POSIX ACLs and security labels depend on xattrs. The help text directs users toward ext4 for ext2 media because this driver has a 2038 timestamp limitation.

State and persistence behavior: No runtime state. These symbols control whether source files and feature hooks are compiled, which affects on-disk xattr/ACL/security-label support availability.

Dependencies and integration points: Integrates with VFS buffer-head and iomap infrastructure, POSIX ACL framework, and xattr-based security modules such as SELinux. It also gates Makefile object selection.

Risks: Enabling ACL/security without xattr is intentionally disallowed. Disabling xattr removes ACL and security label paths at compile time, which changes user-visible filesystem semantics. The deprecation text is a maintenance signal for tests and consumers.

Test signals: Build matrix for core-only ext2, xattr-only, ACL, and security-label configurations; verify `acl.c` and `xattr_security.c` inclusion follows symbols; ensure help text and dependencies produce valid menuconfig choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/Makefile -->
# sources/distributed-fs/ceph-client/fs/ext2/Makefile

Purpose: Defines Kbuild object composition for the ext2 filesystem driver.

Important APIs/types/functions: `obj-$(CONFIG_EXT2_FS) += ext2.o` creates the composite ext2 object. Core members are `balloc.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `ioctl.o`, `namei.o`, `super.o`, `symlink.o`, and `trace.o`. Optional members are gated by `CONFIG_EXT2_FS_XATTR`, `CONFIG_EXT2_FS_POSIX_ACL`, and `CONFIG_EXT2_FS_SECURITY`.

Control flow: Kbuild composes `ext2.o` from mandatory and optional object lists. `CFLAGS_trace.o := -I$(src)` lets tracepoint infrastructure include the local `trace.h`.

State and persistence behavior: No runtime state. The file determines which feature implementations exist in the built driver.

Dependencies and integration points: Integrated with Kconfig symbols, tracepoint generation, VFS feature files, xattr handlers, ACL support, and security-label support.

Risks: Removing a mandatory object breaks core operation tables or exported internal helpers. Optional object gating must stay consistent with stubs in headers such as `acl.h` and `xattr.h`.

Test signals: Build ext2 under all option combinations; validate tracepoint compilation; confirm undefined symbols do not appear when xattr, ACL, or security support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/acl.c -->
# sources/distributed-fs/ceph-client/fs/ext2/acl.c

Purpose: Implements ext2 POSIX ACL support by translating between on-disk ext2 ACL xattr payloads and in-memory `struct posix_acl`.

Important APIs/types/functions: Public functions are `ext2_get_acl`, `ext2_set_acl`, and `ext2_init_acl`. Internal serializers are `ext2_acl_from_disk`, `ext2_acl_to_disk`, and `__ext2_set_acl`. The file uses xattr indexes `EXT2_XATTR_INDEX_POSIX_ACL_ACCESS` and `EXT2_XATTR_INDEX_POSIX_ACL_DEFAULT`.

Control flow: `ext2_get_acl` rejects RCU lookup, maps ACL type to xattr index, probes xattr size, allocates a value buffer, rereads the xattr, and converts it to `posix_acl`. `ext2_set_acl` updates mode bits for access ACLs via `posix_acl_update_mode`, stores or removes the xattr with `__ext2_set_acl`, then updates mode/ctime if needed. `ext2_init_acl` derives ACLs from the parent with `posix_acl_create` and writes default/access ACLs for a new inode.

State and persistence behavior: ACLs persist as extended attribute blocks/entries. Successful writes update the inode ACL cache with `set_cached_acl`; access ACL updates may change `inode->i_mode`, ctime, and dirty state. Default ACLs are rejected for non-directories unless clearing them.

Dependencies and integration points: Depends on ext2 xattr helpers, Linux POSIX ACL core, id conversion through `init_user_ns`, and VFS inode operation hooks from `file.c` and `namei.c`.

Risks: Disk format parsing is sensitive to short-vs-full entry sizing, version checks, exact end-pointer consumption, and invalid tags. `init_user_ns` mapping means ACL IDs are serialized in the initial namespace. Allocation failures must not partially update ACL cache or mode.

Test signals: ACL get/set/remove on files and directories; inherited default ACL creation; chmod interactions; corrupt xattr ACL payloads with bad version, length, tag, or trailing bytes; builds with ACL disabled using stubs from `acl.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/acl.h -->
# sources/distributed-fs/ceph-client/fs/ext2/acl.h

Purpose: Defines ext2 on-disk ACL structures, sizing/counting helpers, and compile-time ACL stubs/prototypes.

Important APIs/types/functions: Defines `EXT2_ACL_VERSION`, `ext2_acl_entry`, `ext2_acl_entry_short`, `ext2_acl_header`, `ext2_acl_size`, and `ext2_acl_count`. When `CONFIG_EXT2_FS_POSIX_ACL` is enabled, it declares `ext2_get_acl`, `ext2_set_acl`, and `ext2_init_acl`; otherwise it maps get/set hooks to `NULL` and makes `ext2_init_acl` a no-op.

Control flow: `ext2_acl_size` encodes the ext2 disk format rule that the first four ACL entries are short entries and later named user/group entries require full entries. `ext2_acl_count` reverses that calculation and returns `-1` for misaligned/invalid payload sizes.

State and persistence behavior: No direct state mutation. It defines the persistent ACL wire format consumed by `acl.c`.

Dependencies and integration points: Includes `linux/posix_acl_xattr.h` and is included by ext2 inode/name/file creation paths. Its stubs keep callers buildable when POSIX ACL support is disabled.

Risks: Size/count helpers must stay exactly synchronized with the serializer; off-by-one or alignment mistakes can reject valid ACLs or overrun corrupt xattrs. The lack of include guards relies on existing include patterns and could be fragile if reused differently.

Test signals: Unit-style validation of ACL payload sizes around 0-5 entries; compile with ACL enabled and disabled; xattr parser tests for malformed ACL size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/balloc.c -->
# sources/distributed-fs/ceph-client/fs/ext2/balloc.c

Purpose: Implements ext2 block bitmap validation, allocation, freeing, reservation-window management, free block counting, and sparse-superblock group descriptor accounting.

Important APIs/types/functions: Public helpers include `ext2_get_group_desc`, `ext2_new_blocks`, `ext2_free_blocks`, `ext2_data_block_valid`, `ext2_count_free_blocks`, `ext2_bg_has_super`, `ext2_bg_num_gdb`, `ext2_init_block_alloc_info`, `ext2_discard_reservation`, and `ext2_rsv_window_add`. Internal control centers are `read_block_bitmap`, `ext2_valid_block_bitmap`, `group_adjust_blocks`, `ext2_try_to_allocate`, `ext2_try_to_allocate_with_rsv`, `alloc_new_reservation`, `find_next_reservable_window`, and `ext2_has_free_blocks`.

Control flow: Allocation starts with quota reservation, optional inode reservation-window selection, reserved-block availability checks, and a goal group derived from the requested physical goal. It tries the goal group, then all groups, skipping empty or reservation-poor groups. Within a group it reads and validates the bitmap, optionally creates or extends a reservation window in the filesystem-wide red-black tree, finds free bits, and atomically sets contiguous bits. If reservations cause apparent ENOSPC, it retries without reservations. On success it rejects system-zone overlap, updates group descriptor counts, percpu free-block counter, quota, bitmap dirty state, and returns the first physical block plus actual count.

State and persistence behavior: Persistent state includes block bitmaps and group descriptor free-block counts; in-memory state includes percpu counters and reservation RB tree. Freeing validates the data zone, splits frees across group boundaries, refuses system-zone frees, atomically clears bitmap bits, dirties/syncs buffers on synchronous mounts, adjusts group/percpu counters, returns quota, and marks the inode dirty.

Dependencies and integration points: Used by `inode.c` block mapping and truncation. Depends on buffer heads, quota, capability checks for reserved blocks, per-blockgroup locks, superblock mount options, and ext2 group geometry from `ext2.h`.

Risks: Bitmap/group descriptor inconsistencies can allocate or free metadata blocks if validations regress. Reservation tree locking is split from bitmap locking and must avoid overlapping windows. Counter updates must match actual bits changed, including already-clear/already-set races. The `ext2_data_block_valid` check excludes first data block and superblock overlap but metadata-zone checks happen separately.

Test signals: xfstests allocation/free under fragmentation; ENOSPC with reserved blocks and unprivileged users; reservation on/off and `EXT2_IOC_SETRSVSZ`; corruption tests for bad block bitmap, freeing system zones, and cross-group frees; synchronous mount bitmap persistence; sparse-superblock group accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/balloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/dir.c -->
# sources/distributed-fs/ceph-client/fs/ext2/dir.c

Purpose: Implements ext2 directory entry parsing, validation, lookup, iteration, insertion, deletion, empty-directory initialization/checking, and directory file operations.

Important APIs/types/functions: Exports `ext2_dir_operations`, `ext2_find_entry`, `ext2_inode_by_name`, `ext2_add_link`, `ext2_delete_entry`, `ext2_make_empty`, `ext2_empty_dir`, `ext2_dotdot`, and `ext2_set_link`. Key helpers include `ext2_check_folio`, `ext2_get_folio`, `ext2_readdir`, `ext2_prepare_chunk`, `ext2_commit_chunk`, `ext2_handle_dirsync`, `ext2_rec_len_from_disk`, and `ext2_rec_len_to_disk`.

Control flow: Directory reads map folios with `read_mapping_folio`, validate the page once with `ext2_check_folio`, then emit entries while honoring `i_version`-based seek-cookie revalidation. Lookup scans from `i_dir_start_lookup`, wrapping around pages. Add/link scans existing and one expansion folio, detects duplicates, uses a free entry or splits a large record, writes the new entry, clears the btree flag, updates times, and optionally syncs directory metadata. Delete merges the target record into the previous record when possible. `make_empty` creates `.` and `..`; `empty_dir` accepts only those entries.

State and persistence behavior: Directory contents persist as block-sized chunks of variable-length `ext2_dir_entry_2` records in page cache/buffer heads. Mutations increment inode version, update size for extension, dirty directory metadata, and sync on dirsync. `file->private_data` stores a per-open 64-bit directory version cookie used by `generic_llseek_cookie`.

Dependencies and integration points: Called by `namei.c` namespace operations and exportfs parent lookup. Uses `ext2_get_block` for block allocation, VFS `dir_emit`, folio/kmap APIs, file leases, ioctl/fasync hooks via `ext2_dir_operations`, and ext2 feature flag `EXT2_FEATURE_INCOMPAT_FILETYPE` for d_type.

Risks: Directory corruption checks must catch zero rec_len, unaligned entries, cross-block spans, bad names, and inode numbers beyond the superblock. Kmap release nesting is subtle because returned entries are mapped folio addresses. Insertion operates past `i_size` while holding the folio lock, so error paths must unlock and release correctly.

Test signals: Directory create/unlink/rename under large directories; readdir after concurrent changes and seeks; corrupted directory images; 64 KiB block rec_len conversion; dirsync mount behavior; filetype feature on/off; empty directory checks before `rmdir`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/ext2.h -->
# sources/distributed-fs/ceph-client/fs/ext2/ext2.h

Purpose: Central ext2 private header defining in-memory superblock/inode state, on-disk ext2 structures, feature/mount flags, directory formats, allocation types, helper macros, and cross-file prototypes.

Important APIs/types/functions: Defines `ext2_sb_info`, `ext2_inode_info`, `ext2_group_desc`, `ext2_inode`, `ext2_super_block`, `ext2_dir_entry(_2)`, reservation types, `EXT2_SB`, `EXT2_I`, `ext2_mask_flags`, `ext2_group_first_block_no`, `ext2_group_last_block_no`, feature macros, mount option macros, bitmap little-endian aliases, ioctl constants, and prototypes for block, inode, dir, file, ioctl, namei, super, and symlink operations.

Control flow: Header inline logic masks inherited inode flags by inode type, maps group numbers to first/last physical blocks, verifies superblock offsets at build time, and exposes compile-time constants used throughout mount, allocation, block mapping, and namespace operations.

State and persistence behavior: `ext2_sb_info` holds mounted filesystem geometry, group descriptors, mount options, counters, locks, xattr cache, DAX device, and reservation tree. `ext2_inode_info` embeds VFS inode plus raw block pointers, flags, xattr block, deletion time, group, reservation info, xattr semaphore, metadata lock, truncate mutex, quota pointers, and metadata buffer tracking. On-disk structures encode superblock, group descriptor, inode, and directory layout.

Dependencies and integration points: Bridges all ext2 compilation units with Linux VFS, buffer heads, blockgroup locks, percpu counters, rbtrees, memory management, xattr/ACL code, DAX, quota, iomap, and export operations. Feature macros must align with ext2/ext3 on-disk compatibility semantics.

Risks: Structural definitions are ABI with disk images; field or endian mistakes corrupt filesystems. Lock comments describe critical serialization contracts for truncation vs block allocation and xattr access. Feature masks determine mount compatibility. `EXT2_CURRENT_REV` remains old revision while dynamic revision support is managed by superblock code.

Test signals: Compile-time offset checks; mount images with old/dynamic revisions and feature combinations; inode flag inheritance tests; large-file feature setting; DAX mount behavior; big-endian bitmap/inode compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/ext2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/file.c -->
# sources/distributed-fs/ceph-client/fs/ext2/file.c

Purpose: Provides ext2 regular-file operations for buffered I/O, direct I/O, DAX I/O/faults, mmap setup, fsync, open/release, and inode operation hooks.

Important APIs/types/functions: Exports `ext2_file_operations`, `ext2_file_inode_operations`, and `ext2_fsync`. Key helpers are `ext2_file_read_iter`, `ext2_file_write_iter`, `ext2_dio_read_iter`, `ext2_dio_write_iter`, `ext2_dio_write_end_io`, DAX `ext2_dax_read_iter`, `ext2_dax_write_iter`, `ext2_dax_fault`, `ext2_file_mmap_prepare`, `ext2_release_file`, and `ext2_file_open`.

Control flow: Reads route to DAX, direct I/O, or generic buffered I/O. Writes route similarly; direct writes take the inode lock, run generic write checks and metadata updates, force synchronous DIO for extending or unaligned writes, and fall back to buffered writes on `-ENOTBLK` or remaining iterator data. DAX writes use `dax_iomap_rw` and update i_size after successful extension. Release of writable files discards reservation windows under `truncate_mutex`.

State and persistence behavior: Fsync uses `mmb_fsync` for metadata buffer tracking and reports metadata I/O errors through `ext2_error`. Direct/DAX write completion updates `i_size` and marks inodes dirty for extending writes. Open enables `FMODE_CAN_ODIRECT` and initializes quotas. Release drops in-memory reservation windows, not disk data.

Dependencies and integration points: Depends on `ext2_iomap_ops`, `ext2_aops`, quota, iomap DIO, DAX, generic file helpers, VFS fileattr/xattr/ACL hooks, tracepoints, leases, splice, and THP unmapped-area selection.

Risks: Direct I/O to holes is intentionally forced to buffered fallback to avoid stale data exposure in non-extent mappings. DAX fault lock ordering is documented and must stay consistent with truncate and freeze. Partial direct writes require page-cache invalidation and writeback ordering. Reservation discard on release affects allocation locality but not correctness.

Test signals: Buffered/direct/DAX read-write matrices; unaligned DIO fallback; extending DIO i_size updates; fsync metadata error injection; mmap page faults with DAX; writable close discards reservation; quota open behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/ialloc.c -->
# sources/distributed-fs/ceph-client/fs/ext2/ialloc.c

Purpose: Implements ext2 inode bitmap allocation/freeing, directory-placement policies, inode counter maintenance, and free-inode/free-directory counting.

Important APIs/types/functions: Public functions are `ext2_new_inode`, `ext2_free_inode`, `ext2_count_free_inodes`, and `ext2_count_dirs`. Internal helpers are `read_inode_bitmap`, `ext2_release_inode`, `ext2_preread_inode`, `find_group_dir`, `find_group_orlov`, and `find_group_other`.

Control flow: New inode allocation chooses a block group: directories use old allocator or Orlov allocator; non-directories prefer parent group, then quadratic probing, then linear search. It scans inode bitmaps with atomic set-bit operations, handles races by retrying groups, updates bitmap and group descriptor counters, initializes ownership, timestamps, inherited flags, generation, inode state, quota, ACL, and security xattrs, then returns a locked new inode. Freeing validates the inode number, frees quota first, clears the inode bitmap bit, updates group/percpu counters, dirties/syncs the bitmap, and releases buffers.

State and persistence behavior: Persistent state includes inode bitmaps and group descriptor free-inode/used-directory counts. In-memory state includes percpu counters, `s_debts` for Orlov placement, inode generation counter, and newly allocated `ext2_inode_info` fields. `ext2_preread_inode` asynchronously reads the inode table block expected to be written soon.

Dependencies and integration points: Used by `namei.c` create/link/mkdir/mknod/symlink/tmpfile flows and by `inode.c` eviction/freeing. Depends on blockgroup locks, quota, xattrs, ACL initialization, security xattrs, random starting group for top-level directories, and superblock geometry.

Risks: Bitmap/counter mismatch can leak or double-allocate inode numbers. Failure after bitmap allocation but before inode insertion relies on VFS discard paths; quota/ACL/security failures must drop quota and discard the inode. Orlov uses approximate counters, so allocation must tolerate stale group choices. Reserved inode bounds are enforced after bitmap selection.

Test signals: Massive file and directory creation under concurrency; oldalloc vs Orlov placement; quota failures; ACL/security initialization failures; reserved inode/corrupt bitmap images; free-inode counter verification; synchronous mount bitmap writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/ialloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/inode.c -->
# sources/distributed-fs/ceph-client/fs/ext2/inode.c

Purpose: Implements ext2 inode lifecycle, classic direct/indirect block mapping, iomap integration, buffered/DAX address-space operations, truncation/freeing of block trees, on-disk inode read/write, getattr/setattr, and eviction.

Important APIs/types/functions: Public entry points include `ext2_iget`, `ext2_write_inode`, `ext2_evict_inode`, `ext2_get_block`, `ext2_iomap_ops`, `ext2_fiemap`, `ext2_aops`, `ext2_set_file_ops`, `ext2_set_inode_flags`, `ext2_getattr`, `ext2_setattr`, and `ext2_write_failed`. Internal block-tree helpers include `ext2_block_to_path`, `ext2_get_branch`, `ext2_find_goal`, `ext2_alloc_blocks`, `ext2_alloc_branch`, `ext2_splice_branch`, `ext2_get_blocks`, `ext2_find_shared`, `ext2_free_data`, and `ext2_free_branches`.

Control flow: Reads of inodes use `iget_locked`, locate the raw inode in its group inode table, validate deleted/corrupt states, load metadata/block pointers, and select regular/dir/symlink/special operation tables. Block lookup translates logical blocks to direct/indirect offsets, reads the branch, verifies it against concurrent truncation, and either returns a contiguous mapping or, for creates, locks `truncate_mutex`, allocates all indirect/data blocks unreachable from the inode, zeroes DAX allocations, revalidates, and splices the final pointer. Truncation invalidates page cache, locks mapping invalidation and `truncate_mutex`, detaches partial indirect branches, frees right-side subtrees, clears later inode-rooted subtrees, and discards reservation state.

State and persistence behavior: On-disk inode fields are serialized/deserialized with endian conversion, including 32-bit UID/GID compatibility, large-file high size, file ACL block, generation, direct/indirect block pointers, timestamps, flags, and device encoding. Metadata buffer heads are tracked via `mapping_metadata_bhs` for fsync/writeback. Eviction writes deletion time, truncates blocks, deletes xattrs, clears metadata tracking, frees reservation info, and returns the inode bitmap entry.

Dependencies and integration points: Depends on block allocator/freeing, xattr deletion, ACL hooks, quota, buffer heads/mpage, iomap, DAX, VFS attribute helpers, page cache invalidation, inode operation tables from other ext2 files, and superblock feature updates for large files.

Risks: Correctness depends on ordering: allocate and initialize branches before splicing, verify chains against truncation, and detach truncated branches before freeing. DAX zeroout and block-device alias cleaning prevent stale data exposure. Large-file feature mutation must sync the superblock. Fast symlinks share `i_data`, so truncation/writeback must not treat them as block trees.

Test signals: fsx/xfstests for indirect, double, and triple-indirect files; concurrent writes and truncates; DAX zeroing; failed writes beyond EOF; eviction of unlinked open files; fast/slow symlink handling; corrupt raw inode fields; large-file feature enable; fiemap over sparse files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/ext2/ioctl.c

Purpose: Implements ext2 file attribute get/set support and legacy ioctls for inode generation and reservation-window size.

Important APIs/types/functions: Public functions are `ext2_fileattr_get`, `ext2_fileattr_set`, `ext2_ioctl`, and `ext2_compat_ioctl`. Commands include `EXT2_IOC_GETVERSION`, `EXT2_IOC_SETVERSION`, `EXT2_IOC_GETRSVSZ`, `EXT2_IOC_SETRSVSZ`, and 32-bit aliases for get/set version.

Control flow: Fileattr get returns user-visible ext2 flags through `fileattr_fill_flags`. Fileattr set rejects fsx attributes and quota files, updates user-modifiable ext2 flags, reapplies VFS inode flags, updates ctime, and dirties the inode. `GETVERSION` returns `i_generation`; `SETVERSION` requires ownership/capability and a writable mount, copies a user value, updates ctime and generation under inode lock, and dirties the inode. Reservation-size ioctls operate only on regular files when reservation mount option is enabled; set clamps to `EXT2_MAX_RESERVE_BLOCKS` and lazily initializes allocation info under `truncate_mutex`.

State and persistence behavior: Attribute and generation changes persist through dirty inode writeback. Reservation size is in-memory allocation policy state, not an on-disk field; it changes future block allocation behavior for the open inode.

Dependencies and integration points: Used by file and directory file operations. Depends on VFS permission helpers, mount write guards, user copy helpers, fileattr API, and allocator reservation structures from `balloc.c`/`ext2.h`.

Risks: Reservation-size ioctl has a documented locking question but uses `truncate_mutex`, matching block allocation synchronization. Quota files must remain protected from flag changes. Compat ioctl only translates version commands; unsupported compat commands return `-ENOIOCTLCMD`.

Test signals: chattr/lsattr behavior; setting immutable/append/nodump/noatime flags; generation get/set permission and read-only mount failures; reservation ioctl on regular/non-regular files with reservation on/off; compat 32-bit ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/namei.c -->
# sources/distributed-fs/ceph-client/fs/ext2/namei.c

Purpose: Implements ext2 VFS namespace operations: lookup, create, tmpfile, mknod, symlink, hard link, mkdir, unlink, rmdir, rename, parent lookup for exportfs, and directory/special inode operation tables.

Important APIs/types/functions: Exports `ext2_dir_inode_operations`, `ext2_special_inode_operations`, and `ext2_get_parent`. Static operations include `ext2_lookup`, `ext2_create`, `ext2_tmpfile`, `ext2_mknod`, `ext2_symlink`, `ext2_link`, `ext2_mkdir`, `ext2_unlink`, `ext2_rmdir`, `ext2_rename`, and helper `ext2_add_nondir`.

Control flow: Lookup validates name length, reads an inode number from `dir.c`, loads it with `ext2_iget`, and splices aliases. Create/mknod/symlink/mkdir allocate an inode, assign operation tables/data, mark it dirty, populate directory entries, and instantiate dentries. Symlinks choose fast in-inode storage when the target fits in `i_data`, otherwise use page-cache symlink storage. Unlink finds and deletes the directory entry, then decrements link count. Rename locates the old entry, optionally tracks `..` for moved directories, replaces or adds the new entry, updates ctimes/link counts, deletes the old entry, and fixes `..` when moving across parents.

State and persistence behavior: Namespace state persists through directory entries and inode link counts. Directory operations update parent/child ctime, mtime, size for directories, and link counts for hard links and directories. Tmpfile creates an inode not linked into a directory. Rename supports only `RENAME_NOREPLACE` among flags.

Dependencies and integration points: Relies on `ialloc.c` for new inodes, `dir.c` for directory entry editing, `inode.c` for inode loading and operation assignment, quota initialization, ACL/xattr operations, and exportfs parent reconstruction through `ext2_get_parent`.

Risks: Error paths must balance link counts and discard new inodes after partially completed creates/mkdirs/symlinks. Rename has multiple mapped folios and must release each exactly once. Directory moves must update both old and new parent link counts plus the child's `..` entry. Deleted inode references during lookup are treated as filesystem errors.

Test signals: create/link/unlink/mkdir/rmdir/rename xfstests; cross-directory rename of directories; replacement rename with non-empty target directory rejection; fast vs slow symlink thresholds; tmpfile open; exportfs parent lookup; long-name `-ENAMETOOLONG` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/namei.c -->
