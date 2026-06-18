# Group Research: group_978_linux_stable_sources_os_linux_linux_stable_fs_exfat_super_c_sources__be36a1a33be1

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/super.c -->
# File Research: sources/os/linux/linux-stable/fs/exfat/super.c

## Summary
Implements the Linux exFAT superblock, mount-context, boot-region validation, root inode setup, mount option parsing, shutdown, and module registration paths.

## Main Responsibilities
- Parses exFAT mount parameters through the modern `fs_context` API.
- Reads and validates the exFAT boot sector and boot checksum region.
- Initializes per-superblock state, allocation bitmap, upcase table, inode hash table, root inode, and NLS conversion.
- Maintains volume dirty/media-failure flags in the boot sector.
- Handles statfs, remount/reconfigure, forced shutdown, superblock teardown, and inode slab lifecycle.

## Key APIs
- `exfat_init_fs_context()`, `exfat_parse_param()`, `exfat_get_tree()`, `exfat_reconfigure()`.
- `exfat_fill_super()`, `__exfat_fill_super()`.
- `exfat_read_boot_sector()`, `exfat_verify_boot_region()`.
- `exfat_set_volume_dirty()`, `exfat_clear_volume_dirty()`, `exfat_force_shutdown()`.
- `exfat_alloc_inode()`, `exfat_free_inode()`, `exfat_kill_sb()`.

## Important Behavior
Mount validation checks boot signature, filesystem name, zeroed FAT-compatible fields, FAT count, sector/cluster geometry, FAT length, data start, boot-region signatures, and checksum sectors. The root directory chain is counted before loading upcase/bitmap entries to avoid infinite traversal on corrupt media.

`exfat_fill_super()` sets `SB_NODIRATIME`, timestamp limits, max file size, dentry operations, NLS state, root inode metadata, inode hash insertion, and the root dentry. Remount only allows dynamic changes for options that are not cached into inodes or dentries; charset, uid/gid, masks, time interpretation, and name handling are rejected if changed.

## State and Lifetime
`struct exfat_sb_info` is allocated per mount context. On mount failure, bitmap and boot-sector buffers are released on the relevant error paths. On kill, `kill_block_super()` runs first and the remaining exFAT superblock state is freed after RCU, including NLS, upcase table, iocharset, and `sbi`.

## Risks
Boot geometry and checksum validation are central corruption gates. Volume flag writes bypass changes on read-only mounts but otherwise synchronously update the boot sector with flush/FUA semantics. Remount swaps option structs, so rejected cached options must stay rejected to avoid stale dentry/inode interpretation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exfat/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exportfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/exportfs/Makefile

## Summary
Builds the generic exportfs support object when `CONFIG_EXPORTFS` is enabled.

## Main Contents
- Adds `exportfs.o` to the kernel build for `CONFIG_EXPORTFS`.
- Defines `exportfs-objs := expfs.o`.

## Risks
This file is simple build glue. Its only behavioral significance is that all exportfs code in this directory currently comes from `expfs.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exportfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/exportfs/expfs.c -->
# File Research: sources/os/linux/linux-stable/fs/exportfs/expfs.c

## Summary
Implements generic filesystem export support: encoding inodes/dentries into file handles and decoding file handles back into acceptable dentries for NFS, fanotify, and other exportfs consumers.

## Main Responsibilities
- Encodes inode- and dentry-based file handles.
- Provides a generic non-decodeable 64-bit inode/generation file identifier.
- Reconnects disconnected dentries to the dcache tree when subtree checks require connected paths.
- Finds child names by scanning parent directories when a filesystem lacks `get_name`.
- Validates decoded aliases against caller-provided acceptability rules.

## Key APIs
- `exportfs_encode_inode_fh()`.
- `exportfs_encode_fh()`.
- `exportfs_decode_fh_raw()`.
- `exportfs_decode_fh()`.

## Important Behavior
`exportfs_encode_inode_fh()` delegates to filesystem `export_operations->encode_fh()` when available, or emits an inode/generation FID for `EXPORT_FH_FID` users. User flag bits in returned fileid types are rejected.

Decode first asks the filesystem to turn a file handle into a dentry. Directory results may be reconnected to root through `reconnect_path()`. Non-directory results first try acceptable aliases, then decode and reconnect the parent, recover the child name, re-lookup under that parent, and re-run acceptability checks.

The default `get_name()` opens the parent directory and iterates entries until it finds the child inode number from `vfs_getattr_nosec()`.

## State and Synchronization
Dentry aliases are walked under `inode->i_lock` with temporary dentry references. Reconnect logic handles races where rename or delete reconnects or invalidates a target while exportfs is reconstructing a path.

## Risks
Reconnect behavior depends on filesystem `get_parent`, `fh_to_dentry`, and `fh_to_parent` correctness. Directory scans match by inode number, so filesystems with unstable inode identity or unusual directory semantics must provide robust export operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/exportfs/expfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ext2/Kconfig

## Summary
Declares ext2 kernel configuration options and marks the ext2 driver deprecated.

## Main Contents
- `EXT2_FS`: tristate driver option, selecting `BUFFER_HEAD` and `FS_IOMAP`.
- `EXT2_FS_XATTR`: optional extended attribute support.
- `EXT2_FS_POSIX_ACL`: optional POSIX ACL support, dependent on xattrs and selecting `FS_POSIX_ACL`.
- `EXT2_FS_SECURITY`: optional security-label xattr handler support.

## Important Behavior
The help text warns that the ext2 driver does not properly support timestamps beyond `03:14:07 UTC on 19 January 2038`, advises using ext4 for ext2-format filesystems, and frames this code as a simple filesystem reference.

## Risks
Feature options are layered: POSIX ACL and security labels require xattr support. Disabling xattrs removes both ACL storage and security-label support from the ext2 build.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ext2/Makefile

## Summary
Defines the ext2 built object composition.

## Main Contents
- Builds `ext2.o` when `CONFIG_EXT2_FS` is enabled.
- Core objects: `balloc.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `ioctl.o`, `namei.o`, `super.o`, `symlink.o`, `trace.o`.
- Adds `xattr.o`, `xattr_user.o`, and `xattr_trusted.o` for `CONFIG_EXT2_FS_XATTR`.
- Adds `acl.o` for `CONFIG_EXT2_FS_POSIX_ACL`.
- Adds `xattr_security.o` for `CONFIG_EXT2_FS_SECURITY`.
- Adds `-I$(src)` for tracepoint compilation.

## Risks
The build layout mirrors feature dependencies from Kconfig. ACL and security behavior disappear entirely when their config symbols are off.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/acl.c

## Summary
Implements ext2 POSIX ACL conversion, retrieval, update, and inheritance over ext2 extended attributes.

## Main Responsibilities
- Converts ACL xattr payloads between ext2 on-disk format and in-memory `struct posix_acl`.
- Reads access/default ACLs from xattrs.
- Writes access/default ACLs to xattrs and updates the VFS ACL cache.
- Initializes inherited ACLs for newly allocated inodes.

## Key APIs
- `ext2_get_acl()`.
- `ext2_set_acl()`.
- `ext2_init_acl()`.

## Important Behavior
On-disk ACLs start with `EXT2_ACL_VERSION`, then store short entries for owner/group/mask/other and full entries for named users/groups. UID/GID values are converted through `init_user_ns`.

`ext2_get_acl()` does not support RCU lookup and returns `-ECHILD` in RCU mode. `ext2_set_acl()` updates inode mode through `posix_acl_update_mode()` for access ACLs before storing the xattr. Default ACLs are accepted only for directories.

## Risks
ACL parsing is strict about entry sizes, tags, version, and trailing bytes. `ext2_set_acl()` uses `nop_mnt_idmap`, so idmapped mount semantics are not applied here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/ext2/acl.h

## Summary
Defines ext2 POSIX ACL on-disk structures, size/count helpers, and ACL function declarations or stubs.

## Main Contents
- `EXT2_ACL_VERSION`.
- `ext2_acl_entry`, `ext2_acl_entry_short`, and `ext2_acl_header`.
- `ext2_acl_size()` and `ext2_acl_count()`.
- Declarations for `ext2_get_acl()`, `ext2_set_acl()`, and `ext2_init_acl()` when ACL support is enabled.
- Null/no-op stubs when `CONFIG_EXT2_FS_POSIX_ACL` is disabled.

## Important Behavior
The size helpers encode the ext2 ACL storage rule: the first four base ACL entries use the short format, while named user/group entries use the full format with an ID field.

## Risks
The count helper returns `-1` for malformed payload sizes; callers must treat that as invalid on-disk ACL data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/balloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/balloc.c

## Summary
Implements ext2 block bitmap validation, block allocation/freeing, per-file reservation windows, free-block accounting, and sparse-superblock group metadata sizing.

## Main Responsibilities
- Locates group descriptors and validates block bitmap metadata bits.
- Allocates and frees data blocks while updating bitmaps, group descriptors, quotas, inode dirty state, and percpu counters.
- Maintains a filesystem-wide red-black tree of block reservation windows.
- Chooses free blocks near goals, inside reservations, or by scanning groups.
- Enforces reserved-block policy for non-privileged users.
- Reports free block counts and backup super/group-descriptor block usage.

## Key APIs
- `ext2_get_group_desc()`.
- `ext2_new_blocks()`.
- `ext2_free_blocks()`.
- `ext2_data_block_valid()`.
- `ext2_init_block_alloc_info()`, `ext2_discard_reservation()`, `ext2_rsv_window_add()`.
- `ext2_count_free_blocks()`.
- `ext2_bg_has_super()`, `ext2_bg_num_gdb()`.

## Important Behavior
Allocation starts with a goal block, maps it to a group, reads the group block bitmap, and tries to allocate near the goal. Regular files may use a reservation window if enabled. Reservation windows live in an rb-tree, grow after good hit ratios, can cross group boundaries, and are abandoned if they cause false ENOSPC.

`ext2_new_blocks()` charges quota before allocation, checks global reserved-block rules, searches the goal group first, then other groups, and falls back to no-reservation allocation before returning ENOSPC. It rejects allocations in block bitmap, inode bitmap, or inode table zones.

`ext2_free_blocks()` validates the block range, splits frees across group boundaries, rejects system-zone frees, clears bitmap bits atomically under the blockgroup lock, and updates counters only for bits that were actually set.

## State and Synchronization
Group descriptor counters are protected by per-blockgroup locks. Reservation windows are protected by `s_rsv_window_lock`. Per-superblock free block state is tracked both in group descriptors and `s_freeblocks_counter`.

## Risks
This file sits on multiple consistency boundaries: bitmap bits, group descriptor counts, percpu counters, quota state, and reservation rb-tree state must stay aligned. Corrupt metadata can trigger error paths that continue with a corrupt bitmap depending on mount error policy.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/dir.c

## Summary
Implements ext2 linear directory layout handling using folios/pagecache: validation, lookup, readdir, insertion, deletion, empty-directory checks, and directory file operations.

## Main Responsibilities
- Validates ext2 directory entry records in folios.
- Provides directory iteration through `iterate_shared`.
- Finds names and `..` entries.
- Adds, updates, and deletes directory entries.
- Initializes `.` and `..` for new directories.
- Checks whether a directory contains only `.` and `..`.
- Maintains directory version cookies for stable llseek/readdir behavior.

## Key APIs
- `ext2_find_entry()`.
- `ext2_inode_by_name()`.
- `ext2_dotdot()`.
- `ext2_add_link()`.
- `ext2_set_link()`.
- `ext2_delete_entry()`.
- `ext2_make_empty()`.
- `ext2_empty_dir()`.
- `ext2_dir_operations`.

## Important Behavior
Directory records are checked for minimum record size, 4-byte alignment, name length fit, block-boundary containment, and valid inode number. Checked folios are marked with `folio_set_checked()`.

`ext2_add_link()` scans existing records for an empty slot or a splittable record, expanding at `i_size` as needed. `ext2_delete_entry()` merges the deleted record into the previous record when possible. Directory writes clear `EXT2_BTREE_FL`, update times, dirty the inode, and honor dirsync via `filemap_write_and_wait()` plus `sync_inode_metadata()`.

## State and Synchronization
Directory file private data stores an i_version cookie used by `generic_llseek_cookie()` and readdir validation. Folios are kmap-local mapped; successful lookup helpers return mapped folios that callers must release with `folio_release_kmap()`.

## Risks
Directory entry corruption produces `ext2_error()` and often `-EIO`. Correct kmap nesting and release discipline is explicitly documented because lookup helpers return mapped folio pointers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/ext2.h -->
# File Research: sources/os/linux/linux-stable/fs/ext2/ext2.h

## Summary
Central ext2 private header defining in-memory structures, on-disk structures, feature flags, mount flags, allocation constants, directory formats, helper macros, and cross-file prototypes.

## Main Contents
- Block number typedefs and reservation-window structures.
- `struct ext2_sb_info` with group geometry, superblock buffers, counters, locks, reservation tree, xattr cache, and DAX state.
- `struct ext2_inode_info` with block pointers, flags, xattr fields, block group, reservation info, lookup hint, locks, orphan/quota state, and VFS inode.
- On-disk `struct ext2_super_block`, `struct ext2_inode`, and directory entry formats.
- Feature flags for compat, ro-compat, and incompat ext2/ext3-era features.
- Mount option flags and ioctl constants.
- Prototypes for block allocation, inode allocation, directory helpers, inode mapping, ioctl, namei, superblock, and operation tables.

## Important Behavior
The header defines the supported feature masks, including support for ext attrs, filetype, meta_bg, sparse super, large file, and btree dir. It maps ext2 file flags to VFS inode flags through declarations implemented in `inode.c`.

Inline helpers compute first/last block of a group and wrap little-endian bitmap bit operations.

## Risks
Many ext2 subsystems share mutable state declared here: blockgroup locks, reservation tree locks, inode metadata locks, truncate mutexes, and percpu counters. Misusing these interfaces can desynchronize disk metadata and in-memory accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/ext2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/file.c

## Summary
Implements ext2 regular file operations, including buffered I/O dispatch, direct I/O through iomap, DAX I/O and faults, fsync, mmap preparation, file open/release, and file inode operations.

## Main Responsibilities
- Selects DAX, direct I/O, or buffered read/write paths.
- Handles DAX mmap faults and write faults.
- Implements direct I/O fallback to buffered writes for unsupported hole writes.
- Discards reservation windows when writable file instances are released.
- Syncs metadata buffer tracking through `mmb_fsync()`.
- Exposes file xattr, ACL, fiemap, attribute, and fileattr operations.

## Key APIs
- `ext2_file_operations`.
- `ext2_file_inode_operations`.
- `ext2_fsync()`.
- `ext2_dio_read_iter()`, `ext2_dio_write_iter()`.
- DAX helpers under `CONFIG_FS_DAX`.

## Important Behavior
DAX reads/writes use `dax_iomap_rw()` under inode locks. DAX faults take pagefault and invalidate-lock protection. Direct writes force synchronous completion for extending or unaligned writes, then may fall back to buffered write for remaining data.

`ext2_file_open()` enables `FMODE_CAN_ODIRECT` and initializes quotas. `ext2_release_file()` discards block reservations for writable file handles under `truncate_mutex`.

## Risks
Direct I/O on non-extent ext2 must avoid stale data exposure when writing holes; the code returns `-ENOTBLK` to force buffered fallback. Reservation lifetime depends on release/truncate/evict paths discarding windows at the right times.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/ialloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/ialloc.c

## Summary
Implements ext2 inode allocation and freeing, including group-selection policy, inode bitmap updates, group descriptor accounting, quota setup, ACL/security initialization, and free inode/directory counting.

## Main Responsibilities
- Reads inode bitmaps.
- Frees inode bitmap bits and updates free inode/directory counters.
- Selects block groups for new directory and non-directory inodes.
- Implements the Orlov directory allocator and older directory allocation mode.
- Allocates inodes, initializes ext2 private inode fields, inserts locked inodes, and initializes quota/ACL/security state.
- Counts free inodes and directories.

## Key APIs
- `ext2_new_inode()`.
- `ext2_free_inode()`.
- `ext2_count_free_inodes()`.
- `ext2_count_dirs()`.

## Important Behavior
Directory placement uses either old allocation or Orlov allocation. Orlov spreads top-level directories, uses average free inode/block counts, directory counts, and per-group debt to avoid clustering too many directories in one group. Non-directories prefer the parent group, then use quadratic probing, then linear fallback.

`ext2_new_inode()` sets the inode bitmap bit atomically, updates group descriptors and percpu counters, initializes ownership, ext2 flags inherited from the parent, generation number, ACLs, security xattrs, quotas, and async prereads the target inode table block.

`ext2_free_inode()` drops quota state first, validates inode number, clears the bitmap bit atomically, adjusts directory counts if needed, and syncs the bitmap on synchronous mounts.

## State and Synchronization
Bitmap updates use per-blockgroup locks. Group descriptor free inode and used directory counters are updated under the same lock. The generation counter is protected by `s_next_gen_lock`.

## Risks
Allocator decisions use approximate percpu counters, so allocation must handle races where a selected group has no free inodes by continuing the scan. Failure after bitmap allocation must go through `discard_new_inode()` and quota cleanup paths to avoid leaks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/inode.c

## Summary
Implements ext2 inode lifecycle, block mapping through direct/indirect/triple-indirect trees, iomap integration, buffered address-space operations, DAX mapping support, truncation, inode read/write, getattr, and setattr.

## Main Responsibilities
- Maps logical file blocks to physical blocks and allocates missing branches.
- Builds and splices indirect block chains safely against truncate races.
- Provides `ext2_get_block()` for buffer-head based I/O and `ext2_iomap_ops` for iomap/DAX/direct I/O.
- Handles write failures by truncating pagecache and blocks.
- Evicts deleted inodes, truncates data, deletes xattrs, frees inode blocks and inode bitmap state.
- Truncates direct and indirect block trees.
- Reads raw on-disk inodes into VFS/ext2 in-memory inodes.
- Writes in-memory inode state back to disk, including large-file feature enablement.
- Implements `getattr`, `setattr`, and file operation selection.

## Key APIs
- `ext2_get_block()`.
- `ext2_iomap_ops`.
- `ext2_aops`.
- `ext2_fiemap()`.
- `ext2_evict_inode()`.
- `ext2_iget()`.
- `ext2_write_inode()`.
- `ext2_setattr()`, `ext2_getattr()`.
- `ext2_set_inode_flags()`, `ext2_set_file_ops()`.

## Important Behavior
Ext2 uses 12 direct pointers plus single, double, and triple indirect blocks. `ext2_block_to_path()` computes offsets into that tree. `ext2_get_branch()` reads existing indirect blocks and detects concurrent changes with key verification. Allocation happens under `truncate_mutex`, allocates all needed metadata/data blocks before linking them, and only splices the missing pointer after rechecking the chain.

Iomap writes to holes inside `i_size` with direct I/O are rejected with `-ENOTBLK` to force buffered I/O. DAX allocations zero newly allocated blocks before exposing them through the tree.

Truncation detaches partial branches under `i_meta_lock`, frees subtrees recursively, discards reservations, and uses `invalidate_lock` around block tree changes. Fast symlinks are excluded from block truncation.

## State and Synchronization
`truncate_mutex` serializes block allocation and truncation. `i_meta_lock` protects indirect pointer verification/detach. `mapping->invalidate_lock` protects truncate/DAX invalidation interactions. Metadata buffer heads are tracked through `i_metadata_bhs`.

## Risks
The block tree code is race-sensitive: partial indirect chains can change during lookup, truncate can remove branches, and allocation must not expose uninitialized blocks. Inode timestamp storage is 32-bit ext2 format, matching the Kconfig deprecation warning.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/ioctl.c

## Summary
Implements ext2 file attribute get/set and legacy ext2 ioctl handling for inode generation and reservation-window size.

## Main Responsibilities
- Exposes user-visible ext2 inode flags through `fileattr`.
- Updates user-modifiable inode flags and maps them to VFS inode flags.
- Handles get/set inode generation ioctls.
- Handles get/set reservation window size ioctls.
- Provides compat ioctl translation for 32-bit generation ioctls.

## Key APIs
- `ext2_fileattr_get()`.
- `ext2_fileattr_set()`.
- `ext2_ioctl()`.
- `ext2_compat_ioctl()`.

## Important Behavior
`ext2_fileattr_set()` rejects fsx-style attributes, rejects quota files, updates only `EXT2_FL_USER_MODIFIABLE`, refreshes VFS flags, updates ctime, and dirties the inode.

`EXT2_IOC_SETVERSION` requires ownership/capability and a writable mount. Reservation size ioctls require regular files and the reservation mount option; setting size lazily creates block allocation info under `truncate_mutex` and clamps to `EXT2_MAX_RESERVE_BLOCKS`.

## Risks
Reservation size locking is noted as uncertain in a comment; practical protection is via `truncate_mutex`. The compat path only translates version ioctls, not reservation-size ioctls.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/ext2/namei.c

## Summary
Implements ext2 VFS namespace operations: lookup, create, tmpfile, mknod, symlink, link, mkdir, unlink, rmdir, rename, parent lookup, and operation tables.

## Main Responsibilities
- Bridges VFS inode operations to ext2 inode allocation and directory-entry helpers.
- Resolves dentries through linear directory lookup.
- Creates regular files, special files, symlinks, directories, hard links, and tmpfiles.
- Removes directory entries and adjusts link counts.
- Renames entries, including directory `..` updates across parents.
- Provides exportfs parent lookup through `ext2_get_parent()`.

## Key APIs
- `ext2_dir_inode_operations`.
- `ext2_special_inode_operations`.
- `ext2_get_parent()`.

## Important Behavior
Create/mknod/link/mkdir/unlink/rename initialize quotas for affected directories. `ext2_add_nondir()` centralizes link insertion and new inode instantiation; on failure it drops link count and discards the new inode.

Symlinks are stored as fast symlinks in `i_data` when they fit, otherwise as pagecache-backed slow symlinks. `mkdir` increments parent and child link counts, writes `.` and `..`, then adds the directory entry. `rename` supports only `RENAME_NOREPLACE`, handles replacement link counts, checks non-empty target directories, and updates `..` when moving a directory across parents.

## Risks
Correct link-count rollback is critical in create, mkdir, symlink failure, hardlink failure, unlink, rmdir, and rename paths. Directory layout manipulation is delegated to `dir.c`, so these operations depend on mapped folio release and directory-entry update correctness there.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext2/namei.c -->