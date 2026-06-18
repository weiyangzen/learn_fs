# Group Research: group_736_linux_sources_os_linux_linux_fs_exfat_super_c_sources_os_linux_linux_cc668a7894b4

Scope checked against `Docs/research_subset_a.md`: all files are under the included `sources/os/linux/linux` source tree. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exfat/super.c -->
# File Research: sources/os/linux/linux/fs/exfat/super.c

Read status: complete, 943 lines.

This file implements the exFAT filesystem superblock, mount, remount, shutdown, and module lifecycle path. It owns `fs_context` option parsing, validates the on-disk exFAT boot region, initializes the in-memory `exfat_sb_info`, sets up the root inode, and registers the `exfat` filesystem type.

Key responsibilities:
- Mount option handling for uid/gid, masks, `allow_utime`, `iocharset`, `errors=`, `discard`, `keep_last_dots`, `sys_tz`, `time_offset`, and `zero_size_dir`.
- Boot sector validation: signature, `fs_name`, zeroed FAT compatibility field, FAT count, sector/cluster sizing, FAT/data layout consistency, volume flags, and boot checksum region.
- Superblock operations: inode allocation/free, inode write/eviction hooks, `statfs`, `show_options`, `put_super`, and shutdown.
- Root directory setup through `exfat_read_root()`, including root chain initialization, link count from directory entries, mode ownership mapping, timestamp initialization, and directory operations.
- NLS setup for non-UTF-8 mounts and UTF-8 dentry operation selection.
- Forced shutdown behavior via `exfat_force_shutdown()`, including freeze/thaw for sync shutdown modes and disabling discard after shutdown.
- Module init/exit: exFAT cache initialization, inode slab cache creation, filesystem registration, RCU-delayed superblock teardown, NLS unload, and upcase table freeing.

Important data/control flow:
- `exfat_init_fs_context()` allocates and defaults `exfat_sb_info`; `exfat_parse_param()` mutates its mount options.
- `exfat_get_tree()` calls `get_tree_bdev()` with `exfat_fill_super()`.
- `exfat_fill_super()` applies mount defaults, checks discard support, installs superblock operations, calls `__exfat_fill_super()`, initializes hashing/NLS, creates the root inode, and attaches `sb->s_root`.
- `__exfat_fill_super()` reads and verifies the boot sector/region, counts root clusters, loads upcase table and allocation bitmap, repairs the root cluster bitmap bit if needed, and counts used clusters.
- `exfat_reconfigure()` allows only limited dynamic remount changes; cached inode/dentry-affecting options are rejected if changed.

Concurrency and safety:
- `sbi->s_lock` protects volume dirty flag transitions around unmount/remount cleanup.
- RCU is used in `exfat_kill_sb()` to delay `sbi` freeing until readers are gone.
- Boot block writes use dirty buffer marking plus `REQ_SYNC | REQ_FUA | REQ_PREFLUSH` when changing volume flags.
- Mount-time validation is defensive against malformed sector sizes, FAT/data overlap, bad checksum, and impossible cluster geometry.

External dependencies:
- Uses Linux VFS `fs_context`, block device mount helpers, buffer heads, NLS, slab caches, RCU, and statfs APIs.
- Relies on other exFAT implementation files for FAT/cache/bitmap/upcase/inode/dentry operations declared in `exfat_fs.h`.

Research notes:
- This is the central exFAT integration file rather than the allocator or directory implementation.
- Error policy defaults to remount-ro and is exposed in mount option display.
- Persistent volume flags preserve dirty/media-failure bits across updates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exfat/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exportfs/Makefile -->
# File Research: sources/os/linux/linux/fs/exportfs/Makefile

Read status: complete, 7 lines.

This Makefile builds the generic filesystem export support module.

Key responsibilities:
- Adds `exportfs.o` when `CONFIG_EXPORTFS` is enabled.
- Defines `exportfs-objs := expfs.o`, so the module/object is composed from `expfs.c`.

Research notes:
- The build surface is intentionally minimal.
- The functional implementation for this directory is in `fs/exportfs/expfs.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exportfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/exportfs/expfs.c -->
# File Research: sources/os/linux/linux/fs/exportfs/expfs.c

Read status: complete, 610 lines.

This file implements generic VFS export helpers used by NFS export and file-handle users. It maps inodes/dentries to file handles and decodes file handles back to dentries, including reconnecting disconnected dentries to the dcache tree when subtree checks require a connected path.

Key responsibilities:
- Default `get_name()` implementation: scans a parent directory with `iterate_dir()` to find the entry matching a child inode number.
- File-handle encoding via `exportfs_encode_inode_fh()` and `exportfs_encode_fh()`, delegating to filesystem `export_operations` when present.
- Fallback non-decodeable 64-bit inode/generation file IDs for fanotify-style use when full export decode support is unavailable.
- File-handle decoding through `exportfs_decode_fh_raw()` and `exportfs_decode_fh()`.
- Dentry reconnect logic for disconnected dentries: `reconnect_path()`, `reconnect_one()`, `dentry_connected()`, and `clear_disconnected()`.
- Alias selection through `find_acceptable_alias()` to satisfy caller-provided export/subtree acceptance checks.

Important data/control flow:
- Encoding checks `exportfs_can_encode_fh()` and rejects unsupported user flag bits in returned file ID types.
- Decoding calls filesystem `fh_to_dentry`; for directories it may reconnect to root before applying `acceptable()`.
- For non-directories, decoding first tries acceptable aliases; if needed, it decodes the parent via `fh_to_parent`, reconnects that parent, finds the child name, looks it up, verifies inode identity, and then rechecks aliases.
- `exportfs_decode_fh()` normalizes most decode errors to `-ESTALE`, except `-ENOMEM`.

Concurrency and safety:
- Alias walking uses `inode->i_lock` and reference-safe dentry handling.
- Reconnect paths tolerate rename/unlink races by rechecking whether dentries became connected or stale.
- Directory scanning uses `vfs_getattr_nosec()` instead of directly trusting `i_ino`, which matters for 64-bit inode numbers on 32-bit hosts.
- Strictly rejects invalid fileid types with user flag bits set.

External dependencies:
- Uses filesystem-provided `struct export_operations`.
- Integrates with VFS dentries, mounts, path lookup, credentials, directory iteration, and NFS export documentation assumptions.

Research notes:
- This file is generic infrastructure, not tied to one filesystem.
- Correctness depends heavily on dcache aliasing and reconnect semantics.
- It is the bridge between stable file handles and volatile VFS dentries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/exportfs/expfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/Kconfig -->
# File Research: sources/os/linux/linux/fs/ext2/Kconfig

Read status: complete, 50 lines.

This Kconfig file defines ext2 build-time configuration options.

Key responsibilities:
- Defines `EXT2_FS` as a tristate option for “Second extended fs support (DEPRECATED)”.
- Selects `BUFFER_HEAD` and `FS_IOMAP` for the ext2 driver.
- Documents ext2 deprecation due to insufficient timestamp support beyond 03:14:07 UTC on 19 January 2038.
- Advises users to mount ext2 filesystems with the ext4 driver instead.
- Defines optional support for extended attributes, POSIX ACLs, and security labels.

Options:
- `EXT2_FS_XATTR`: enables extended attributes.
- `EXT2_FS_POSIX_ACL`: depends on xattrs and selects `FS_POSIX_ACL`.
- `EXT2_FS_SECURITY`: depends on xattrs and enables security-label xattr handlers such as SELinux labels.

Research notes:
- The file explicitly frames ext2 as retained mainly as a simple reference filesystem for developers.
- Optional ACL/security features are layered on xattr support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/Makefile -->
# File Research: sources/os/linux/linux/fs/ext2/Makefile

Read status: complete, 16 lines.

This Makefile builds the ext2 filesystem object.

Key responsibilities:
- Builds `ext2.o` when `CONFIG_EXT2_FS` is enabled.
- Core object list: `balloc.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `ioctl.o`, `namei.o`, `super.o`, `symlink.o`, and `trace.o`.
- Adds include path for tracepoint infrastructure with `CFLAGS_trace.o := -I$(src)`.
- Conditionally adds xattr, ACL, and security-label implementation files.

Research notes:
- The Makefile shows ext2’s major implementation split: block allocation, inode allocation, inode/block mapping, directory format handling, VFS name operations, file operations, mount/superblock handling, symlinks, and tracepoints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/acl.c -->
# File Research: sources/os/linux/linux/fs/ext2/acl.c

Read status: complete, 276 lines.

This file implements ext2 POSIX ACL support on top of ext2 extended attributes.

Key responsibilities:
- Converts ACL xattr bytes from disk format to in-memory `struct posix_acl` via `ext2_acl_from_disk()`.
- Converts in-memory ACLs to ext2 disk xattr format via `ext2_acl_to_disk()`.
- Loads access/default ACLs with `ext2_get_acl()`.
- Stores or removes ACLs through `__ext2_set_acl()` and `ext2_set_acl()`.
- Initializes inherited ACLs for new inodes with `ext2_init_acl()`.

Important data/control flow:
- Access ACLs use `EXT2_XATTR_INDEX_POSIX_ACL_ACCESS`.
- Default ACLs use `EXT2_XATTR_INDEX_POSIX_ACL_DEFAULT` and are only valid for directories.
- `ext2_set_acl()` updates inode mode through `posix_acl_update_mode()` for access ACL changes, then marks the inode dirty if mode changed.
- `ext2_init_acl()` uses `posix_acl_create()` to derive default/access ACLs from the parent and stores them on the new inode.

Safety and validation:
- Disk ACL parser validates header size, ACL version, entry count, entry bounds, tag type, and exact buffer consumption.
- Unknown ACL tags fail with `-EINVAL`.
- RCU ACL lookup is unsupported and returns `-ECHILD`.
- Missing xattrs map to no ACL rather than an error.

External dependencies:
- Depends on ext2 xattr get/set helpers.
- Uses Linux POSIX ACL helpers and init user namespace UID/GID conversion.

Research notes:
- ACLs are not stored in the inode proper; they are serialized as xattrs.
- The disk format has compact short entries for owner/group/mask/other and full entries for named users/groups.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/acl.h -->
# File Research: sources/os/linux/linux/fs/ext2/acl.h

Read status: complete, 73 lines.

This header defines the ext2 ACL xattr disk format and compile-time ACL integration points.

Key responsibilities:
- Defines `EXT2_ACL_VERSION`.
- Defines disk ACL structures: `ext2_acl_entry`, `ext2_acl_entry_short`, and `ext2_acl_header`.
- Provides `ext2_acl_size()` and `ext2_acl_count()` helpers for converting between ACL entry count and serialized size.
- Declares ACL functions when `CONFIG_EXT2_FS_POSIX_ACL` is enabled.
- Provides null/no-op ACL integration when POSIX ACL support is disabled.

Research notes:
- The size/count helpers encode the disk-format distinction between the first four short ACL entries and subsequent full entries.
- When ACL support is disabled, VFS inode operation hooks resolve to `NULL`, and new inode ACL initialization succeeds as a no-op.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/balloc.c -->
# File Research: sources/os/linux/linux/fs/ext2/balloc.c

Read status: complete, 1535 lines.

This file implements ext2 block bitmap handling, block allocation, block freeing, free-space accounting, and reservation-window management.

Key responsibilities:
- Retrieves and validates block group descriptors with `ext2_get_group_desc()`.
- Reads and validates per-group block bitmaps, ensuring metadata blocks are marked allocated.
- Frees data blocks with `ext2_free_blocks()`, including group-boundary splitting, system-zone checks, bitmap clearing, descriptor updates, quota freeing, and percpu free-block counter updates.
- Allocates blocks with `ext2_new_blocks()`, using goal-directed allocation, bitmap scans, group fallback, quota charging, reserved-block policy, and optional reservation windows.
- Manages reservation windows for regular files using an RB tree rooted in `s_rsv_window_root`.
- Counts free blocks and computes sparse-super/group-descriptor block usage.

Reservation-window design:
- Each regular file may lazily receive `ext2_block_alloc_info`, which contains a reservation-window node and last allocation hints.
- Reservation windows are inserted into an RB tree ordered by filesystem block range.
- Allocation first tries an existing suitable reservation, otherwise finds a new reservable gap near the goal.
- Window size can grow based on hit rate and requested allocation size, capped by `EXT2_MAX_RESERVE_BLOCKS`.
- Reservation can be disabled globally with mount option state or per inode by setting reservation size to zero.

Allocation flow:
- Quota is charged up front with `dquot_alloc_block()`.
- `ext2_has_free_blocks()` enforces reserved-block policy for non-privileged users.
- The allocator starts in the goal group, then scans other groups, skipping groups with no free blocks or insufficient space for reservations.
- If reservations falsely cause ENOSPC, allocation retries without reservation.
- Successful allocation marks bitmap buffers dirty, updates group descriptor counts, subtracts percpu free blocks, and adjusts quota if fewer blocks were allocated than requested.

Safety and validation:
- `ext2_valid_block_bitmap()` checks block bitmap, inode bitmap, and inode table bits.
- `ext2_data_block_valid()` rejects ranges outside the data zone, wrapping ranges, ranges past `s_blocks_count`, and ranges overlapping the superblock.
- Allocation and free paths reject block ranges that overlap block bitmap, inode bitmap, or inode table.
- Per-block-group bitmap mutation uses block-group locks.
- Reservation tree mutation uses `s_rsv_window_lock`.

External dependencies:
- Uses buffer heads, quota operations, capabilities, percpu counters, blockgroup locks, and RB trees.
- Called heavily from `inode.c` when mapping file blocks.

Research notes:
- This is the core ext2 free-space allocator.
- It combines old bitmap allocation with preallocation-like reservation windows for better locality in growing regular files.
- Metadata consistency is maintained manually through bitmaps, group descriptors, superblock-level counters, and quota state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/dir.c -->
# File Research: sources/os/linux/linux/fs/ext2/dir.c

Read status: complete, 739 lines.

This file implements ext2 directory record handling using the page cache/folios. It owns directory entry validation, iteration, lookup-by-name, insertion, deletion, empty-directory checks, and directory file operations.

Key responsibilities:
- Converts directory record lengths between disk and memory, including 64 KiB block-size handling.
- Validates directory folios with `ext2_check_folio()`.
- Reads and maps directory folios through `ext2_get_folio()`.
- Iterates directories with `ext2_readdir()`.
- Finds named entries via `ext2_find_entry()` and finds `..` via `ext2_dotdot()`.
- Adds directory entries with `ext2_add_link()`.
- Updates existing entries with `ext2_set_link()`.
- Deletes entries with `ext2_delete_entry()`.
- Creates `.` and `..` entries with `ext2_make_empty()`.
- Checks rmdir emptiness with `ext2_empty_dir()`.
- Exposes `ext2_dir_operations`.

Directory format behavior:
- Directories are block-sized chunks containing variable-length `ext2_dir_entry_2` records.
- Entries must be 4-byte aligned, fit within a chunk, have sufficient `rec_len` for `name_len`, and reference valid inode numbers.
- Deletion merges the removed record into the previous record where possible.
- Insertion either uses an empty record or splits a larger record.
- File type byte is populated only when the filesystem has `EXT2_FEATURE_INCOMPAT_FILETYPE`.

Concurrency and consistency:
- Directory changes use folio locking and `__block_write_begin()` through `ext2_prepare_chunk()`.
- `ext2_commit_chunk()` increments inode version, completes write, extends `i_size` if needed, and unlocks the folio.
- Readdir tracks an inode version cookie in `file->private_data`; if the directory changed, offsets are revalidated to record boundaries.
- Directory sync behavior writes and waits on directory mapping and inode metadata.

Error handling:
- Corrupt zero-length entries cause `-EIO`.
- Bad directory layout reports `ext2_error()`.
- Entry lookup returns `-ENOENT` when absent.
- Duplicate insertion returns `-EEXIST`.

Research notes:
- This file deliberately contains directory layout knowledge, while `namei.c` contains VFS operation glue.
- It is an important correctness boundary because ext2 directory records are mutable variable-length records inside ordinary file data blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/ext2.h -->
# File Research: sources/os/linux/linux/fs/ext2/ext2.h

Read status: complete, 820 lines.

This header defines ext2’s in-memory structures, on-disk structures, constants, feature bits, mount flags, ioctl numbers, helper macros, and cross-file prototypes.

Key responsibilities:
- Defines ext2 block number types and `E2FSBLK` format.
- Defines reservation-window structures used by `balloc.c`.
- Defines `struct ext2_sb_info`, the in-core superblock state.
- Defines `struct ext2_group_desc`, `struct ext2_inode`, `struct ext2_super_block`, and directory entry structures.
- Defines inode flags, mount flags, default options, feature bits, special inode numbers, and directory record sizing macros.
- Declares functions shared among ext2 implementation files.
- Provides helpers for block group first/last block numbers and little-endian bitmap operations.

Important structures:
- `ext2_sb_info`: group sizing, descriptor buffers, mount options, counters, blockgroup locks, reservation tree, xattr cache, DAX device info, and superblock buffer.
- `ext2_inode_info`: ext2-specific inode block pointers, flags, ACL/xattr fields, deletion time, block group, reservation info, lookup hint, xattr semaphore, metadata lock, truncate mutex, orphan list, quota pointers, and metadata buffer tracking.
- `ext2_super_block`: on-disk ext2 superblock including counts, geometry, mount/check metadata, revision, feature bits, UUID/name, journal compatibility fields, hash seed, and defaults.
- `ext2_inode`: on-disk inode layout including mode, UID/GID, size, timestamps, block pointers, generation, ACL fields, fragments, and OS-dependent fields.

Key feature definitions:
- Supported compatible feature: ext attrs.
- Supported incompatible features: filetype and meta_bg.
- Supported readonly-compatible features: sparse super, large file, and btree dir.
- Mount flags include old allocator, grpid, error policy, xattrs, ACL, quota, reservation, and DAX.

Concurrency notes:
- `s_lock` protects mount state and selected superblock fields.
- `truncate_mutex` serializes truncate against block mapping and protects reservation internals.
- `i_meta_lock` protects indirect block tree metadata checks/updates.
- Block group locks protect group bitmap/count mutation.

Research notes:
- This header is the central contract for ext2 implementation files.
- It preserves the historical ext2 on-disk ABI while adapting to modern VFS APIs such as iomap, DAX, folios, file attributes, ACLs, and quota.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/ext2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/file.c -->
# File Research: sources/os/linux/linux/fs/ext2/file.c

Read status: complete, 343 lines.

This file implements ext2 regular-file operations, including buffered I/O dispatch, direct I/O, optional DAX I/O/fault handling, fsync, open/release, mmap preparation, and regular-file inode operations.

Key responsibilities:
- Provides DAX read/write paths with `dax_iomap_rw()` when `CONFIG_FS_DAX` and inode DAX are active.
- Provides DAX page fault handling through `dax_iomap_fault()`.
- Provides direct I/O read/write paths using `iomap_dio_rw()` and `ext2_iomap_ops`.
- Falls back from direct writes to buffered writes for unsupported cases such as holes.
- Updates file size for extending DAX/direct writes at the correct synchronization point.
- Drops reservation windows on last writable file release.
- Implements `ext2_fsync()` with metadata buffer tracking.
- Exposes `ext2_file_operations` and `ext2_file_inode_operations`.

I/O behavior:
- `ext2_file_read_iter()` dispatches to DAX, direct I/O, or generic buffered read.
- `ext2_file_write_iter()` dispatches to DAX, direct I/O, or generic buffered write.
- Direct writes force synchronous completion for unaligned or extending writes.
- Partial direct writes can continue with buffered write, then flush and invalidate the affected page-cache range.
- `ext2_dio_write_end_io()` updates `i_size` before page cache invalidation to avoid stale zeroing races.

DAX behavior:
- DAX mmap sets custom vm operations and records file access.
- DAX write faults bracket page faults with filesystem pagefault freeze protection and invalidate lock.
- Huge DAX faults are explicitly unsupported because ext2 block allocation cannot guarantee huge-page alignment.

Concurrency and safety:
- Reads take shared inode lock for DAX/direct I/O.
- Writes take exclusive inode lock.
- Release path takes `truncate_mutex` before discarding reservation state.
- Fsync reports metadata writeback I/O errors through `ext2_error()`.

Research notes:
- This file is mostly VFS/iomap plumbing; physical block mapping is delegated to `inode.c`.
- It is where ext2 integrates old indirect-block storage with modern direct I/O and DAX APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/ialloc.c -->
# File Research: sources/os/linux/linux/fs/ext2/ialloc.c

Read status: complete, 673 lines.

This file implements ext2 inode bitmap handling, inode allocation, inode freeing, and directory placement policy.

Key responsibilities:
- Reads inode bitmaps with `read_inode_bitmap()`.
- Frees inodes with `ext2_free_inode()`, including quota release, bitmap clearing, descriptor count updates, and directory counter updates.
- Allocates new inodes with `ext2_new_inode()`.
- Implements classic and Orlov group selection policies for directory placement.
- Implements non-directory group selection that prefers parent locality and falls back to quadratic/linear search.
- Counts free inodes and directory counts from group descriptors.

Allocation policy:
- Directories use either the old allocator or Orlov allocator depending on mount options.
- Orlov allocator spreads top-level directories across groups, considers average free inodes/free blocks, directory counts, and per-group debt.
- Non-directories prefer the parent’s group, then use a hash-like quadratic search, then linear fallback.
- Per-group debt increases for directory allocation and decreases for non-directory allocation.

New inode flow:
- Allocate VFS inode.
- Select target group.
- Read inode bitmap and atomically set a free bit.
- Update free inode counters, directory counters, group descriptor counts, and debts.
- Initialize owner/group according to `GRPID` mount option or normal ownership rules.
- Initialize ext2 inode fields, inherited flags, block group, generation, ACLs, security xattrs, quotas, and dirty state.
- Insert inode locked, preread the inode table block, and return it.

Free inode flow:
- Reject reserved/nonexistent inode numbers.
- Clear the inode bitmap bit atomically.
- Update group descriptor free inode count and used directory count.
- Update percpu free inode and directory counters.
- Sync bitmap buffer for synchronous mounts.

Safety and consistency:
- Bitmap changes use block group locks.
- Inode freeing order avoids inode-number aliasing by relying on VFS inode teardown before bitmap reuse.
- Quota is freed before superblock/group locking to avoid lock recursion.
- Handles races where group selection saw free inodes but bitmap allocation loses to another allocator.

Research notes:
- This file is ext2’s inode counterpart to `balloc.c`.
- The Orlov allocator is the main policy complexity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/inode.c -->
# File Research: sources/os/linux/linux/fs/ext2/inode.c

Read status: complete, 1691 lines.

This file implements ext2 inode lifecycle, indirect-block file mapping, block allocation through mapping requests, truncation/free recursion, address-space operations, iomap integration, fiemap, inode read/write, and setattr/getattr.

Key responsibilities:
- Evicts inodes with `ext2_evict_inode()`, including deleted-inode truncation, xattr deletion, reservation cleanup, and inode freeing.
- Maps logical file blocks through the ext2 direct/single/double/triple indirect tree.
- Allocates indirect branches and data blocks using `ext2_new_blocks()`.
- Splices newly allocated branches into inode metadata after race checks.
- Supports buffer-head mapping through `ext2_get_block()`.
- Supports iomap through `ext2_iomap_ops`.
- Implements folio address-space operations for buffered read/write/writeback.
- Implements DAX address-space operations.
- Truncates files and recursively frees indirect subtrees.
- Reads raw inodes from inode tables and populates VFS inodes with `ext2_iget()`.
- Writes VFS inode state back to disk with `__ext2_write_inode()`.
- Implements `getattr`, `setattr`, and `fiemap`.

Block mapping design:
- `ext2_block_to_path()` converts a logical block to offsets through direct, indirect, double-indirect, or triple-indirect levels.
- `ext2_get_branch()` reads existing indirect blocks into a chain of pointer/key/buffer triples and detects holes, I/O failures, or concurrent modification.
- `ext2_find_goal()` prefers sequential allocation based on last allocation hints, otherwise locality near previous pointers, indirect blocks, or inode block group.
- `ext2_alloc_branch()` allocates needed metadata and data blocks before linking them into the tree.
- `ext2_splice_branch()` atomically attaches the new branch and updates allocation hints and inode metadata.
- `ext2_get_blocks()` is the central lookup/create routine used by buffer-head and iomap paths.

Truncation design:
- `ext2_truncate_blocks()` skips unsupported inode types and fast symlinks.
- Truncation takes the mapping invalidate lock and `truncate_mutex`.
- `ext2_find_shared()` detaches partially truncated branches safely.
- `ext2_free_data()` coalesces contiguous data block frees.
- `ext2_free_branches()` recursively frees indirect subtrees.
- Reservation windows are discarded after truncation.

Inode read/write:
- `ext2_get_inode()` computes inode table location from inode number and group descriptor.
- `ext2_iget()` validates deleted/stale inodes, reads UID/GID, timestamps, blocks, flags, ACL fields, generation, data pointers, and installs correct inode/file ops by type.
- Fast symlinks store the symlink target in `i_data`; slow symlinks use page-cache-backed data.
- Special files decode old or new device numbers from inode block fields.
- `__ext2_write_inode()` serializes VFS inode state back to the ext2 raw inode, handles UID/GID high bits, large-file feature enabling, device encoding, and new-inode zeroing.

I/O integration:
- `ext2_iomap_begin()` maps ext2 indirect blocks into iomap records for DAX/direct/fiemap.
- Direct writes to holes inside `i_size` return `-ENOTBLK` for buffered fallback to avoid stale exposure on non-extent storage.
- Buffered address-space operations use mpage and block helpers with `ext2_get_block()`.
- DAX writeback uses `dax_writeback_mapping_range()`.

Concurrency and safety:
- `truncate_mutex` serializes block tree mutation and truncation.
- `i_meta_lock` protects verification of indirect-chain consistency.
- Mapping invalidate lock protects truncation against DAX/page-cache interactions.
- Branch allocation prepares all blocks before publishing pointers, reducing recovery complexity on allocation failure.
- DAX newly allocated blocks are zeroed before being linked into the tree.

Research notes:
- This is the core ext2 data mapping file.
- It demonstrates classic Unix indirect-block mapping adapted to modern Linux iomap, DAX, folio, quota, and writeback infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/ioctl.c -->
# File Research: sources/os/linux/linux/fs/ext2/ioctl.c

Read status: complete, 159 lines.

This file implements ext2 ioctl and file attribute operations.

Key responsibilities:
- Gets and sets user-visible ext2 inode flags through `ext2_fileattr_get()` and `ext2_fileattr_set()`.
- Handles `EXT2_IOC_GETVERSION` and `EXT2_IOC_SETVERSION` for inode generation.
- Handles `EXT2_IOC_GETRSVSZ` and `EXT2_IOC_SETRSVSZ` for per-regular-file reservation window size.
- Provides compat ioctl translation for 32-bit generation ioctls.

Behavior:
- Fileattr set rejects fsx-style attributes and quota files.
- Fileattr set masks updates to `EXT2_FL_USER_MODIFIABLE`, then applies VFS inode flags through `ext2_set_inode_flags()`.
- Setting inode generation requires owner/capability check and a writable mount.
- Reservation-size ioctls require reservation mount option, regular file type, and owner/capability for setting.
- Reservation size is capped at `EXT2_MAX_RESERVE_BLOCKS`.
- If needed, setting reservation size lazily allocates `i_block_alloc_info` under `truncate_mutex`.

Safety and permissions:
- Uses `inode_owner_or_capable()` for privileged mutation.
- Uses `mnt_want_write_file()`/`mnt_drop_write_file()` around mutating ioctls.
- User pointer access uses `get_user()`/`put_user()`.
- Quota files are protected from user flag mutation.

Research notes:
- This is a small control-plane file for legacy ext2 ioctls and modern fileattr hooks.
- Reservation-size ioctls connect user-visible tuning to allocator state in `balloc.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/namei.c -->
# File Research: sources/os/linux/linux/fs/ext2/namei.c

Read status: complete, 434 lines.

This file implements ext2 VFS namespace operations. It is the glue between VFS inode operations and the directory record helpers in `dir.c`.

Key responsibilities:
- Lookup names with `ext2_lookup()`.
- Return parent dentries for export/reconnect paths with `ext2_get_parent()`.
- Create regular files, tmpfiles, device/special nodes, symlinks, hard links, directories, unlink, rmdir, and rename.
- Expose directory and special-file inode operation tables.

Operation flow:
- `ext2_lookup()` validates name length, resolves inode number via `ext2_inode_by_name()`, loads inode through `ext2_iget()`, and returns `d_splice_alias()`.
- `ext2_create()` allocates a new inode, installs regular file ops, marks it dirty, and adds the directory link.
- `ext2_tmpfile()` creates an unlinked regular file and finishes simple open.
- `ext2_mknod()` creates special files and installs `ext2_special_inode_operations`.
- `ext2_symlink()` uses fast symlinks when the target fits in `i_data`, otherwise writes a slow symlink through page-cache data.
- `ext2_link()` increments and instantiates hard links.
- `ext2_mkdir()` increments parent link count, creates child directory inode, initializes `.`/`..`, and links it into parent.
- `ext2_unlink()` deletes the directory entry and decrements target link count.
- `ext2_rmdir()` verifies emptiness, unlinks, zeroes size, and decrements directory link counts.
- `ext2_rename()` supports `RENAME_NOREPLACE`, handles replacement, directory parent `..` updates, link counts, ctime updates, and old-entry deletion.

Error handling and consistency:
- Name length over `EXT2_NAME_LEN` returns `-ENAMETOOLONG`.
- Lookup of a deleted inode referenced by a directory entry reports filesystem error and returns `-EIO`.
- New inode failure paths decrement link counts and discard new inodes.
- Directory rename validates target emptiness when replacing directories.
- Quotas are initialized on directories before namespace mutations.

External dependencies:
- Relies on `dir.c` for directory layout operations.
- Relies on `ialloc.c` for inode allocation.
- Relies on `inode.c` for inode loading and operation setup.
- Exposes hooks for xattrs, ACLs, file attributes, getattr, and setattr.

Research notes:
- The file intentionally avoids directory layout details; it orchestrates VFS semantics and link-count correctness.
- It is the main user-visible namespace mutation path for ext2.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/namei.c -->