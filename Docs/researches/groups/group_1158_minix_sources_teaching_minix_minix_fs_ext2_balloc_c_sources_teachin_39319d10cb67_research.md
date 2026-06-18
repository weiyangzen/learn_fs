# Group Research: group_1158_minix_sources_teaching_minix_minix_fs_ext2_balloc_c_sources_teachin_39319d10cb67

Scope: `Docs/research_subset_a.md`, focused on the listed MINIX teaching filesystem files. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/balloc.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/balloc.c

This file implements ext2 block allocation, block freeing, and inode-local block preallocation.

Key entry points:
- `discard_preallocated_blocks(struct inode *rip)`: frees preallocated blocks either for one inode or globally across the in-core inode table.
- `alloc_block(struct inode *rip, block_t block)`: allocates a data block near a caller-provided goal or near the inode’s block group.
- `free_block(struct super_block *sp, bit_t bit_returned)`: clears a block bitmap bit, updates free counters, and tells libminixfs/VM that the block is no longer associated with an inode.
- Internal `alloc_block_bit()` scans group block bitmaps, optionally allocating an entire byte for `EXT2_PREALLOC_BLOCKS`.

Important behavior:
- Honors read-only mounts by panicking on attempted metadata mutation.
- Avoids reserved blocks unless `opt.use_reserved_blocks` is set.
- Discards all preallocations when free space is low.
- Maintains `s_free_blocks_count`, group `free_blocks_count`, `lmfs_change_blockusage`, `group_descriptors_dirty`, and `s_bsearch`.
- `check_block_number()` prevents allocation/freeing of group metadata blocks such as bitmaps and inode tables.

Dependencies:
- Uses `get_group_desc`, `get_block`, `setbit`, `setbyte`, `unsetbit`, `lmfs_markdirty`, `lmfs_free_block`.
- Depends heavily on `struct super_block`, `struct inode`, and bitmap accessor macros from `buf.h`.

Notable risks:
- Several allocator invariants panic rather than recover.
- Preallocation depends on `EXT2_PREALLOC_BLOCKS == CHAR_BIT`; this is asserted.
- `setbyte()` allocation starts from the beginning of a bitmap rather than the requested goal word, so preallocation locality is coarser than normal `setbit()` allocation.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/buf.h -->
# File Research: sources/teaching/minix/minix/fs/ext2/buf.h

This header provides typed views over an LMFS buffer’s raw `data` pointer.

Defined data views:
- `b_data(bp)`: ordinary byte data.
- `b_ind(bp)`: block address array for indirect blocks.
- `b_bitmap(bp)`: bitmap chunk array for inode/block bitmaps.

Role:
- Central convenience layer for interpreting `struct buf` contents in ext2 code.
- Used throughout allocation, block mapping, directory parsing, read/write, and zeroing code.

Notable detail:
- `union fsdata_u` uses one-element arrays, relying on the actual buffer allocation being larger than the declared member.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/const.h -->
# File Research: sources/teaching/minix/minix/fs/ext2/const.h

This header defines ext2 server constants, operation codes, inode/block layout values, feature masks, and directory-entry macros.

Major definitions:
- Cache/table sizes: `NR_INODES`, `INODE_HASH_SIZE`, `INODE_HASH_MASK`.
- Directory operation flags: `LOOK_UP`, `ENTER`, `DELETE`, `IS_EMPTY`.
- Inode dirty/time flags: `IN_CLEAN`, `IN_DIRTY`, `ATIME`, `CTIME`, `MTIME`.
- ext2 layout constants: `ROOT_INODE`, `SUPER_BLOCK_BYTES`, `EXT2_NDIR_BLOCKS`, `EXT2_IND_BLOCK`, `EXT2_DIND_BLOCK`, `EXT2_TIND_BLOCK`, `EXT2_N_BLOCKS`.
- Directory record sizing helpers: `DIR_ENTRY_ACTUAL_SIZE`, `DIR_ENTRY_SHRINK`, `DIR_ENTRY_MAX_NAME_LEN`.
- Feature masks: compatible, read-only-compatible, incompatible features, and supported feature sets.
- File type constants for ext2 directory entries.
- Preallocation width: `EXT2_PREALLOC_BLOCKS`.

Role:
- Provides the common semantic contract used by allocation, path lookup, mount feature checks, and block mapping.
- `MAX_FAST_SYMLINK_LENGTH` ties fast symlink capacity to the inode block pointer array.

Notable constraints:
- `EXT2_NDIR_BLOCKS` is hard-coded into `ext2_max_size()` assumptions.
- Only `INCOMPAT_FILETYPE` is supported among incompatible features.
- Supported read-only compatible features are sparse super and large file.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/const.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/fs.h -->
# File Research: sources/teaching/minix/minix/fs/ext2/fs.h

This is the master ext2 filesystem-server header.

Role:
- Defines `_SYSTEM` for MINIX system headers.
- Pulls in MINIX, libc, fsdriver, and local ext2 headers.
- Includes `const.h`, `type.h`, `proto.h`, and `glo.h`.
- Defines `ext2_debug` as `printf`.

Impact:
- Most ext2 `.c` files include this header first, giving them shared constants, types, prototypes, globals, and fsdriver access.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/glo.h -->
# File Research: sources/teaching/minix/minix/fs/ext2/glo.h

This header declares ext2 server globals, with `_TABLE` controlling definition versus `extern`.

Globals:
- `err_code`: temporary error return storage.
- `cch[NR_INODES]`: declared cache-related array, initialized in `main.c`.
- `fs_dev`: current filesystem device.
- `group_descriptors_dirty`: signals pending group descriptor writeback.
- `opt`: runtime mount/server options.
- `le_CPU`: endian flag for ext2 little-endian metadata conversion.
- `ext2_table`: fsdriver dispatch table.

Role:
- Connects all ext2 service modules through shared state.
- `group_descriptors_dirty` is particularly important for allocator updates and `write_super()`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/glo.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/ialloc.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/ialloc.c

This file implements ext2 inode allocation and deallocation.

Key entry points:
- `alloc_inode(parent, bits, uid, gid)`: allocates an inode bitmap bit, obtains an in-core inode slot, initializes ownership/mode/device/superblock fields, and wipes block-related fields.
- `free_inode(rip)`: frees the inode bitmap bit and marks the in-core inode not allocated.

Allocation strategies:
- `find_group_any()`: MFS-like first group with free inode, starting at `s_igsearch`.
- `find_group_hashalloc()`: BSD-like placement for non-directories, trying parent group, quadratic probing, then linear fallback.
- `find_group_dir()`: Linux-like directory placement by average free inode count and best free block count.
- `find_group_orlov()`: Orlov allocator for spreading top-level directories and placing child entries in sufficiently free groups.

Metadata updates:
- Updates group and superblock free inode counts.
- Updates used directory counts for directory inodes.
- Sets `group_descriptors_dirty`.
- Maintains `s_igsearch` on inode free.

Notable safeguards:
- Rejects/reserves inodes below `EXT2_FIRST_INO(sp)`.
- Panics if allocator returns an inode beyond `s_inodes_count`.
- Panics on freeing invalid or already-free inode bits.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/inode.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/inode.c

This file manages the in-core ext2 inode cache and disk inode read/write.

Key entry points:
- `fs_putnode(ino_nr, count)`: VFS putnode hook, decrements inode references.
- `init_inode_cache()`: initializes unused inode queue and hash lists.
- `get_inode(dev, numb)`: looks up or loads an inode, manages hash/LRU state.
- `find_inode(dev, numb)`: returns an active inode without opening a new disk inode.
- `put_inode(rip)`: drops a reference, truncates and frees unlinked inodes, writes dirty inodes, returns blocks from preallocation.
- `update_times(rip)`: applies pending atime/ctime/mtime flags.
- `rw_inode(rip, rw_flag)`: maps inode number to inode-table block and copies disk/in-core inode fields.
- `dup_inode(ip)`: increments reference count.

Data structures:
- Uses `hash_inodes[INODE_HASH_SIZE]` plus `unused_inodes` tail queue.
- Tracks cache hit/miss counters.

Disk conversion:
- `icopy()` translates between `struct inode` and `d_inode`, using `conv2/conv4` for endian conversion and preserving OS-dependent fields.

Notable behavior:
- On final put of an unlinked inode, calls `truncate_inode()` then `free_inode()`.
- Always discards preallocated blocks when an inode becomes unused.
- New cache entries initialize preallocation fields from `opt.use_prealloc`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/inode.h -->
# File Research: sources/teaching/minix/minix/fs/ext2/inode.h

This header defines the ext2 in-core inode table.

Structure:
- First section mirrors ext2 disk inode fields: mode, UID/GID, size, timestamps, link count, block count, flags, OS-dependent fields, block pointers, ACL fields.
- Second section adds in-memory state: device, inode number, reference count, superblock pointer, dirty flag, block allocation search hints, directory search hints, mountpoint flag, seek/update flags, preallocation state, hash and unused-list links.

Globals:
- `inode[NR_INODES]`: in-core inode table.
- `unused_inodes`: tail queue of free/unused inode slots.
- `hash_inodes`: inode hash table.
- `inode_cache_hit`, `inode_cache_miss`.

Important fields:
- `i_bsearch` and `i_last_pos_bl_alloc` support locality and preallocation.
- `i_last_dpos` and `i_last_dentry_size` accelerate directory insertion.
- `i_prealloc_blocks`, `i_prealloc_count`, `i_prealloc_index`, `i_preallocation` support sequential-write preallocation.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/link.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/link.c

This file implements link, unlink, rmdir, symlink read, rename, truncate, and free-space operations.

Key entry points:
- `fs_link()`: creates hard links after link-count and directory checks.
- `fs_unlink()`: dispatches unlink versus rmdir behavior.
- `fs_rdlink()`: reads normal symlinks from data blocks or fast symlinks from `i_block[]`.
- `fs_rename()`: implements cross-directory and same-directory rename, replacement, directory ancestry checks, and `..` updates.
- `fs_trunc()`: truncates or frees a byte range.
- `truncate_inode()`: changes file size and frees blocks beyond new size.

Internal helpers:
- `remove_dir()`: validates directory emptiness and removes `.`/`..`.
- `unlink_file()`: deletes a directory entry and decrements link count.
- `freesp_inode()`: zeros partial blocks and frees full blocks with `write_map(..., WMAP_FREE)`.
- `zeroblock_half()` and `zeroblock_range()` zero partial block regions.

Important behavior:
- Truncation discards preallocated blocks first.
- Fast symlinks avoid block I/O by storing target text in inode block pointer space.
- Rename protects mountpoints and prevents moving a directory into its descendant.
- Directory removal depends on `search_dir(..., IS_EMPTY)`.

Notable risks:
- Several rename paths rely on inode pointer identity and comments acknowledge possible filesystem loops.
- `fs_trunc()` uses `find_inode()` and thus only operates on active in-core inodes.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/link.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/main.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/main.c

This file is the ext2 server entry point and SEF startup handler.

Key behavior:
- Defines mount/server options: `sb`, `orlov`, `oldalloc`, `mfsalloc`, `reserved`, `prealloc`, `noprealloc`.
- `main()` registers args, starts SEF, detects CPU endian, asserts little-endian CPU, then runs `fsdriver_task(&ext2_table)`.
- `sef_cb_init_fresh()` initializes defaults, parses `-o` options, enables VM cache usage, initializes inode table/cache, and creates a small initial LMFS buffer pool.
- `sef_cb_signal_handler()` handles `SIGTERM` by syncing and terminating the fsdriver.

Default options:
- Orlov enabled.
- MFS allocator disabled.
- Reserved block usage disabled.
- Alternate superblock offset zero.
- Preallocation disabled by default.

Notable constraint:
- The server asserts little-endian operation despite conversion helpers existing elsewhere.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/main.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/misc.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/misc.c

This file implements ext2 sync.

Key entry point:
- `fs_sync()`: flushes dirty in-core inodes, flushes all LMFS buffers, updates superblock write time, and writes superblock/group descriptors.

Important ordering:
- Inodes are written before `lmfs_flushall()` because `rw_inode()` leaves updates in the block cache.
- Superblock write happens after buffer flushing if the device is still mounted.

Read-only behavior:
- Returns immediately on read-only filesystems.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/mount.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/mount.c

This file implements ext2 mount, unmount, and mountpoint marking.

Key entry points:
- `fs_mount(dev, flags, root_node, res_flags)`: opens block device, reads superblock, validates feature flags/state/root inode, sets LMFS block size/usage, and returns root node metadata.
- `fs_mountpt(ino_nr)`: validates a node can be used as a mountpoint and marks it.
- `fs_unmount()`: syncs, writes clean state, closes device, invalidates LMFS cache, and clears `s_dev`.

Important mount checks:
- Rejects unsupported incompatible and read-only-compatible features.
- Rejects `EXT2_ERROR_FS` state.
- Verifies root inode exists, has nonzero mode, and is a directory.
- Marks writable mounts as `EXT2_ERROR_FS` until clean unmount.

Notable bug risk:
- `fs_mountpt()` calls `put_inode(rip)` before setting `rip->i_mountpoint = TRUE`, potentially writing to an inode after reference release if the inode became unused.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/open.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/open.c

This file implements creation of regular files, special nodes, directories, symlinks, and seek notifications.

Key entry points:
- `fs_create()`: creates a regular file and returns fsdriver node metadata.
- `fs_mknod()`: creates special files with device number stored in `i_block[0]`.
- `fs_mkdir()`: creates directory inode, then adds `.` and `..`, adjusting link counts.
- `fs_slink()`: creates symbolic links, using fast symlink storage when possible.
- `fs_seek()`: marks an inode as seeked to inhibit readahead.

Core helper:
- `new_node()`: allocates an inode, writes it before directory entry insertion for crash robustness, then creates the directory entry.

Important behavior:
- Directory creation rolls back the parent entry if `.` or `..` insertion fails.
- Symlink creation rejects targets larger than one block and rejects embedded NULs by comparing copied target length with `strlen`.
- On symlink failure, link count is cleared and the directory entry is deleted.

Dependencies:
- Uses `advance`, `alloc_inode`, `search_dir`, `rw_inode`, `new_block`, and `fsdriver_copyin`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/open.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/path.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/path.c

This file implements ext2 path component lookup and directory entry mutation.

Key entry points:
- `fs_lookup()`: looks up a name under a directory inode and returns fsdriver node metadata.
- `advance()`: resolves one directory component and opens the target inode.
- `search_dir()`: handles lookup, insertion, deletion, and directory-empty checks.

Directory logic:
- Validates directory inode type.
- Rejects names longer than `EXT2_NAME_MAX`.
- For `ENTER`, computes aligned required record size, reuses cached insertion hints, finds empty entries, shrinks existing entries, or extends the directory with `new_block()`.
- For `DELETE`, clears `d_ino`, optionally saves inode number inside the name field, marks parent dirty, resets `EXT2_INDEX_FL` when HTree is unsupported, and merges with previous entry.
- For `LOOK_UP`, returns the entry inode number.
- For `IS_EMPTY`, ignores `.` and `..`.

Feature interaction:
- When `INCOMPAT_FILETYPE` is present, `ENTER` writes ext2 directory file type values from inode mode.

Notable assumptions:
- Directories are assumed not to have holes.
- Directory record traversal trusts existing record lengths.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/path.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/protect.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/protect.c

This file implements chmod and chown handlers.

Entry points:
- `fs_chmod(ino_nr, mode)`: updates permission bits while preserving file type and non-mode bits, marks ctime and inode dirty, returns full mode.
- `fs_chown(ino_nr, uid, gid, mode)`: changes owner/group, clears setuid/setgid bits, marks ctime and inode dirty, returns updated mode.

Dependencies:
- Uses `get_inode`, `put_inode`, and shared inode dirty/time flags.

Behavior:
- Permission and ownership policy checks are assumed to happen above the filesystem server; this layer applies requested metadata changes.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/protect.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/proto.h -->
# File Research: sources/teaching/minix/minix/fs/ext2/proto.h

This header declares ext2 server function prototypes and aliases `put_block` to `lmfs_put_block`.

Coverage:
- Allocation: block and inode alloc/free.
- Inode cache and disk I/O.
- Link/unlink/rename/truncate.
- Sync, mount, create, directory lookup, chmod/chown.
- Read/write/getdents and block mapping.
- Superblock/group descriptor operations.
- Utility functions for endian conversion, string comparison, bitmap mutation.
- Write-side block mapping helpers.

Role:
- Provides cross-module API boundaries for the ext2 server.
- Shows the fsdriver-facing surface implemented across the ext2 `.c` files.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/read.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/read.c

This file implements ext2 read/write transfer dispatch, block mapping reads, readahead, symlink block access, and `getdents`.

Key entry points:
- `fs_readwrite()`: shared read/write/peek handler that chunks I/O by filesystem block.
- `read_map()`: maps file offsets through direct, single, double, and triple indirect blocks.
- `get_block_map()`: maps and obtains a buffer for a file offset.
- `rd_indir()`: reads an indirect-block entry.
- `fs_getdents()`: emits directory entries through fsdriver dentry API.

Internal:
- `rw_chunk()` handles sparse reads as zeroes, peeks sparse blocks to VM as zero, allocates blocks on write, reads existing blocks, and copies to/from fsdriver data.
- `rahead()` performs cache lookup and prefetch planning, with minimum prefetch unless a seek occurred.
- `get_dtype()` maps ext2 directory file type fields to `DT_*` values.

Important behavior:
- Sparse file holes read as zero without block allocation.
- Writes beyond EOF allocate blocks through `new_block()`.
- Full-block writes may avoid reading old data.
- Directory iteration requires aligned positions and skips entries with `d_ino == 0`.

Notable issue:
- `fs_getdents()` has duplicate `assert(bp != NULL)`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/read.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/stadir.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/stadir.c

This file implements stat and statvfs for ext2.

Entry points:
- `fs_stat(ino_nr, statbuf)`: opens inode, updates pending times, fills POSIX stat fields, then releases inode.
- `fs_statvfs(st)`: fills filesystem-wide block, inode, free-space, and name-length data.

Important fields:
- Special file device number is reported from `i_block[0]`.
- `st_blocks` uses ext2 `i_blocks`, which counts 512-byte units.
- `f_bavail` subtracts reserved blocks from total free blocks.
- `ST_NOTRUNC` is set in `f_flag`.

Dependencies:
- Uses `get_inode`, `put_inode`, `update_times`, and `get_super`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/stadir.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/super.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/super.c

This file reads, writes, and manages ext2 superblock and group descriptor state.

Key entry points:
- `get_super(dev)`: validates and returns the single mounted superblock.
- `get_block_size(dev)`: returns LMFS filesystem block size.
- `read_super(sp)`: reads superblock and group descriptor table, validates layout, derives in-memory fields, initializes search hints.
- `write_super(sp)`: writes superblock and dirty group descriptors.
- `get_group_desc(bnum)`: returns a group descriptor by group number.

Important behavior:
- Supports alternate superblock location through `opt.block_with_super`.
- Allocates on-disk and in-memory group descriptor arrays.
- Validates magic, block size, inode size, inode/block counts.
- Derives `s_block_size`, `s_blocksize_bits`, `s_max_size`, `s_inodes_per_block`, `s_itb_per_group`, `s_groups_count`, `s_gdb_count`, `s_desc_per_block`, `s_dirs_counter`, `s_bsearch`, and `s_igsearch`.
- Uses page-sized chunks for bdev reads/writes of descriptor table.

Endian handling:
- `super_copy()` and `gd_copy()` convert little-endian on non-little-endian CPUs, though runtime asserts little-endian in `main.c`.

Notable bug risk:
- `write_super()` calls `super_copy(ondisk_superblock, sp)` but then writes `(char *) sp` rather than `(char *) ondisk_superblock`; on big-endian this would bypass conversion.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/super.h -->
# File Research: sources/teaching/minix/minix/fs/ext2/super.h

This header defines ext2 superblock and group descriptor structures.

`struct super_block`:
- Starts with the ext2 on-disk superblock fields copied from Linux ext2 definitions.
- Includes dynamic revision fields, feature flags, UUID/name fields, journal-related fields, hash seed/default mount options, and padding.
- Appends in-memory derived state: inode/table sizing, group count, descriptor pointer, block size, sectors per block, max file size, device, read-only flag, allocation search hints, directory counter.

Globals:
- `superblock`: active in-memory superblock.
- `ondisk_superblock`: buffer for disk-format superblock.

`struct group_desc`:
- Tracks block bitmap, inode bitmap, inode table, free block/inode counts, used directories, and reserved fields.

Role:
- Shared metadata model for mount, allocation, inode I/O, statvfs, and sync.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/super.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/table.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/table.c

This file defines the ext2 fsdriver dispatch table.

Registered operations:
- Mount/unmount, lookup, putnode.
- Read/write/peek via `fs_readwrite`.
- Getdents, truncate, seek.
- Create, mkdir, mknod, hard link, unlink/rmdir, rename.
- Symlink creation/readlink.
- Stat, chown, chmod, utime, mountpoint, statvfs, sync.
- LMFS driver, block read/write/peek/flush hooks.

Role:
- This is the binding layer between MINIX fsdriver requests and ext2 implementation functions.
- `_TABLE` causes global definitions rather than extern declarations through `glo.h`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/table.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/time.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/time.c

This file implements explicit timestamp updates.

Entry point:
- `fs_utime(ino_nr, atime, mtime)`: applies `UTIME_NOW`, `UTIME_OMIT`, or explicit seconds values for atime and mtime, marks ctime for update, and dirties inode.

Important behavior:
- Clears stale atime/mtime update flags by assigning `rip->i_update = CTIME`.
- Ext2 subsecond timestamps are unsupported, so explicit times use `tv_sec` only.
- Final timestamp writes happen later through `update_times()`/`rw_inode()`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/time.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/type.h -->
# File Research: sources/teaching/minix/minix/fs/ext2/type.h

This header defines disk-format ext2 inode, directory entry descriptor, directory traversal macros, and runtime options.

Types:
- `d_inode`: disk inode format, matching ext2 fields and OS-dependent sections.
- `struct ext2_disk_dir_desc`: ext2 directory record header plus first name byte.
- `struct opt`: server options for Orlov allocation, MFS-like allocation, reserved block usage, alternate superblock, and preallocation.

Macros:
- `CUR_DISC_DIR_POS`, `NEXT_DISC_DIR_DESC`, `NEXT_DISC_DIR_POS` for directory block traversal.

Role:
- Provides disk-level structure definitions used by inode copy, directory lookup/getdents, symlink fast storage sizing, and mount option parsing.

Notable detail:
- The directory entry structure models revision >= 0.5 file type layout where high name length bits became `d_file_type`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/type.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/utility.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/utility.c

This file provides ext2 utility routines for buffers, endian conversion, string comparison, and bitmap operations.

Key functions:
- `get_block(dev, block, how)`: wrapper around `lmfs_get_block` that panics on real I/O errors and returns `NULL` only for failed `PEEK`.
- `conv2(norm, w)` / `conv4(norm, x)`: endian conversion helpers.
- `ansi_strcmp(ansi_s, s2, ansi_s_length)`: compares fixed-length directory names with C strings.
- `setbit(bitmap, max_bits, word)`: finds and sets a free bit starting at a bitmap word.
- `setbyte(bitmap, max_bits)`: finds and sets a fully free byte for preallocation.
- `unsetbit(bitmap, bit)`: clears a set bit and reports if it was already clear.

Role:
- Shared low-level support for block/inode allocation, directory lookup, and disk structure conversion.

Notable bug:
- `setbyte()` tests `if (*wptr | 0)` which is equivalent to `if (*wptr)`, so it works as a nonzero test but is likely intended to be clearer.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/utility.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/write.c -->
# File Research: sources/teaching/minix/minix/fs/ext2/write.c

This file implements write-side block mapping, indirect block allocation/freeing, and new block acquisition.

Key entry points:
- `write_map(rip, position, new_wblock, op)`: inserts or frees a block mapping at a file offset, including direct, single, double, and triple indirect paths.
- `new_block(rip, position)`: allocates and maps a block for a file offset, choosing sequential allocation goals when possible.
- `zero_block(bp)`: zeros an LMFS buffer and marks it dirty.

Internal helpers:
- `wr_indir(bp, index, block)`: writes one indirect-block entry with endian conversion.
- `empty_indir(bp, sb)`: checks if an indirect block has only `NO_BLOCK` entries.

Important behavior:
- `write_map()` is the authority for maintaining `i_blocks`.
- Frees empty indirect blocks recursively after removing data blocks.
- Allocates new indirect blocks on demand and zeroes them before use.
- `new_block()` disables preallocation on non-sequential writes.

Notable risk:
- `empty_indir()` compares raw `b_ind(bp)[i]` with `NO_BLOCK` without conversion, unlike `rd_indir()`; this is harmless on asserted little-endian but inconsistent with conversion-aware code.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ext2/write.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/hgfs/Makefile -->
# File Research: sources/teaching/minix/minix/fs/hgfs/Makefile

This Makefile builds the VMware Host/Guest File System server.

Build settings:
- Program: `hgfs`.
- Source: `hgfs.c`.
- Manual page: `hgfs.8`.
- Links against `libsffs`, `libhgfs`, `libfsdriver`, and `libsys`.
- Uses `<minix.service.mk>`.

Role:
- Declares HGFS as a MINIX service wrapping shared-folder filesystem support.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/hgfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/hgfs/hgfs.c -->
# File Research: sources/teaching/minix/minix/fs/hgfs/hgfs.c

This file is the HGFS server glue layer between `libsffs` and `libhgfs`.

Key behavior:
- Defines `sffs_params params` and option parsing for prefix, uid, gid, file mask, directory mask, and case sensitivity.
- `sef_cb_init_fresh()` initializes defaults, parses `-o`, initializes HGFS library, then initializes SFFS with the HGFS operation table.
- `sef_local_startup()` registers SEF init and SFFS signal handler.
- `main()` sets environment args, starts SEF, runs `sffs_loop()`, then cleans up HGFS.

Dependencies:
- `hgfs_init()` provides an `sffs_table`.
- `sffs_init()` exposes HGFS through the shared-folder filesystem abstraction.

Failure handling:
- Reports disabled shared folders on `EAGAIN`.
- Cleans up HGFS if SFFS initialization fails.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/hgfs/hgfs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/Makefile -->
# File Research: sources/teaching/minix/minix/fs/isofs/Makefile

This Makefile builds the ISO9660 filesystem server.

Build settings:
- Program: `isofs`.
- Sources: main/table/mount/super/inode/link/utility/path/read/SUSP/Rock Ridge/stat files.
- Links against `libfsdriver`, `libbdev`, `libsys`, and `libminixfs`.
- Adds `CPPFLAGS+= -DNR_BUFS=100`.
- Uses `<minix.service.mk>`.

Role:
- Defines isofs as a read-only MINIX fsdriver service backed by block-device and LMFS helpers.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/const.h -->
# File Research: sources/teaching/minix/minix/fs/isofs/const.h

This header defines ISO9660 constants and feature toggles.

Key constants:
- `GETDENTS_BUFSIZ`.
- ISO standard ID: `CD001`.
- Superblock/volume descriptor offset: `32768`.
- Minimum block size: `2048`.
- Fixed ISO9660 field sizes for IDs and timestamps.
- Maximum ISO and Rock Ridge file ID lengths.
- System UID/GID defaults.

Feature toggles:
- `ISO9660_OPTION_ROCKRIDGE` enabled.
- `ISO9660_OPTION_MODE3` present but disabled with TODO.

Role:
- Shared format constants for volume descriptor parsing, directory parsing, and Rock Ridge handling.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/const.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/glo.h -->
# File Research: sources/teaching/minix/minix/fs/isofs/glo.h

This header declares isofs globals, with `_TABLE` controlling definition.

Globals:
- `fs_dev`: current device handled by the server.
- `opt`: global mount/server options.
- `isofs_table`: fsdriver dispatch table.

Role:
- Minimal shared global state for the read-only ISO9660 server.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/glo.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/inc.h -->
# File Research: sources/teaching/minix/minix/fs/isofs/inc.h

This is the shared include header for isofs.

Role:
- Defines `_SYSTEM`.
- Includes MINIX, fsdriver, libminixfs, bdev, libc, dirent, and assert headers.
- Defines `b_data(bp)` as a `char *` view over buffer data.
- Includes local `const.h`, `proto.h`, `super.h`, and `glo.h`.

Impact:
- Gives all isofs modules a common environment and the same raw buffer accessor.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/inc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/inode.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/inode.c

This file implements isofs inode cache management, directory loading, ISO9660 directory record parsing, and Rock Ridge integration.

Key entry points:
- `fs_putnode()`: decrements reference count for an opened inode.
- `get_inode(ino_nr)`: returns an active cached inode without incrementing.
- `open_inode(ino_nr)`: returns cached inode and increments `i_count`.
- `put_inode()`, `dup_inode()`: reference management.
- `read_directory(dir)`: reads and caches all entries of a directory.
- `read_inode(dir_entry, extent, offset)`: reads one ISO directory record, creates/reuses inode cache entry, parses ISO and Rock Ridge data.
- `inode_cache_get()` / `inode_cache_add()`: uthash-backed inode lookup/insert.

Parsing behavior:
- Directory inode numbers use extent location; file inode numbers use absolute directory record byte position.
- `read_inode_iso9660()` parses names, strips version suffixes, computes extents, timestamps, modes, sizes, block counts, and basic ownership.
- `read_inode_susp()` parses System Use/Rock Ridge data and overlays POSIX metadata, symlink target, alternate name, and reparented inode handling.

Directory cache:
- Uses a stack buffer for up to 256 entries, then allocates an exact-sized persistent array.
- Performs a second pass for directories larger than the stack buffer.
- Skips entries marked by Rock Ridge reparenting.

Notable risks:
- Memory allocation is permanent for cached directories/inodes; comments acknowledge structural improvement needed.
- `check_inodes()` is a stub that always returns true.
- Rock Ridge copied names allocate `name_length + 1` but copy only `name_length`, leaving terminator dependent on allocator zeroing.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/inode.h -->
# File Research: sources/teaching/minix/minix/fs/isofs/inode.h

This header defines ISO9660 and Rock Ridge inode-related structures.

Structures:
- `struct iso9660_dir_record`: packed ISO directory record.
- `struct rrii_dir_record`: temporary Rock Ridge record with timestamps, mode, uid/gid, device, alternate name, symlink target, and reparented inode.
- `struct dir_extent`: contiguous logical-sector extent chain.
- `struct inode_dir_entry`: directory entry wrapper with inode pointer and ISO/Rock Ridge names.
- `struct inode`: in-memory inode with reference counts, mountpoint flag, `struct stat`, first extent, cached directory contents, symlink name, and skip flag.
- `struct opt`: currently only `norock`.

Constants:
- Directory flag masks `D_DIRECTORY`, `D_NOT_LAST_EXTENT`, `D_TYPE`.

Role:
- Defines the read-only isofs metadata model consumed by lookup, read, getdents, stat, and Rock Ridge parsing.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/link.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/link.c

This file implements readlink for isofs.

Entry point:
- `fs_rdlink(ino_nr, data, bytes)`: gets inode, verifies it is a symbolic link, copies up to requested bytes from Rock Ridge `s_name`.

Behavior:
- Returns `EINVAL` if inode is not cached/open.
- Returns `EACCES` if the inode mode is not symlink.
- Uses `fsdriver_copyout`.

Dependency:
- Symlink targets are populated by Rock Ridge `SL` records in `susp_rock_ridge.c`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/link.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/main.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/main.c

This file is the isofs server entry point and startup logic.

Key behavior:
- Defines `norock` option to disable Rock Ridge interpretation.
- `sef_cb_init_fresh()` initializes options, parses `-o`, clears timezone environment for time conversion, and initializes LMFS buffer pool.
- `sef_cb_signal_handler()` terminates fsdriver on `SIGTERM`.
- `sef_local_startup()` registers init/restart/signal callbacks.
- `main()` sets args, starts SEF, and runs `fsdriver_task(&isofs_table)`.

Role:
- Starts a read-only ISO9660 fsdriver service with optional Rock Ridge support.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/mount.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/mount.c

This file implements isofs mount, mountpoint marking, and unmount.

Entry points:
- `fs_mount(dev, flags, root_node, res_flags)`: opens the device read-only, reads volume descriptors, and returns root inode metadata.
- `fs_mountpt(ino_nr)`: validates inode exists, is not already mounted on, and is a directory, then marks mountpoint.
- `fs_unmount()`: releases primary volume descriptor/root inode, closes device, and checks inodes.

Important behavior:
- Mount ignores write flags and always opens with `BDEV_R_BIT`.
- Root UID/GID returned to VFS are `SYS_UID`/`SYS_GID`.
- `check_inodes()` currently does not actually detect active inodes.

Role:
- Bridges fsdriver mount lifecycle with ISO9660 volume descriptor parsing in `super.c`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/path.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/path.c

This file implements isofs component lookup.

Key functions:
- Internal `search_dir(ldir_ptr, string, numb)`: validates directory, loads cached directory contents, handles `"."`, and linearly searches names.
- `fs_lookup(dir_nr, name, node, is_mountpt)`: finds parent inode, resolves child inode number, opens child inode, and returns fsdriver node metadata.

Behavior:
- Read-only lookup over cached directory arrays.
- Uses Rock Ridge names when directory loading chose them.
- Returns `ENOTDIR`, `ENOENT`, `EINVAL`, or `EIO` depending on failure stage.

Notable detail:
- Lookup opens the resulting inode but does not release the parent because `get_inode()` does not increment the parent reference.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/path.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/proto.h -->
# File Research: sources/teaching/minix/minix/fs/isofs/proto.h

This header declares isofs function prototypes.

Coverage:
- Inode cache/reference functions.
- Directory and inode parsing.
- Readlink, mount, mountpoint, unmount, lookup.
- Read and getdents.
- Stat/statvfs.
- Volume descriptor read/release.
- SUSP and Rock Ridge parsing.
- Utility functions for inode entry/extents, extent block reads, ISO date conversion, and allocation.

Role:
- Defines module boundaries for the isofs server.
- Shows the server’s read-only fsdriver-facing API.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/read.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/read.c

This file implements isofs file reads and directory enumeration.

Entry points:
- `fs_read(ino_nr, data, bytes, pos, call)`: reads file data from extents into fsdriver output.
- `fs_getdents(ino_nr, data, bytes, pos)`: emits cached directory entries.

Read behavior:
- Rejects missing inode.
- Returns EOF when position is past file size.
- Clamps read length to file size.
- Splits reads by logical block size.
- Uses `read_extent_block()` and `fsdriver_copyout()`.

Getdents behavior:
- Loads directory contents through `read_directory()`.
- Uses `fsdriver_dentry_add()` with inode number, cached name, and `IFTODT(mode)`.
- Updates `*pos` to the next directory index after successful finish.

Notable risk:
- `read_extent_block(&i_node->extent, pos)` receives a byte position; utility semantics must match that use.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/stadir.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/stadir.c

This file implements stat and statvfs for isofs.

Entry points:
- `fs_stat(ino_nr, statbuf)`: copies cached inode `struct stat`.
- `fs_statvfs(st)`: reports block sizing, total volume blocks, and name max.

Behavior:
- Read-only filesystem statistics set `ST_NOTRUNC`.
- `f_bsize`, `f_frsize`, and `f_iosize` are all the ISO logical block size.
- `f_blocks` comes from the primary volume descriptor’s volume space size.
- Does not report free block/inode fields, consistent with read-only ISO media.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/stadir.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/super.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/super.c

This file reads ISO9660 volume descriptors and initializes the root inode.

Key functions:
- `release_vol_pri_desc(vol_pri)`: releases the root inode reference held by the primary volume descriptor.
- Internal `create_vol_pri_desc(vol_pri, buf)`: copies and validates primary volume descriptor, sets LMFS block size/usage, parses root directory record, and stores root inode.
- `read_vds(vol_pri, dev)`: scans volume descriptors starting at byte 32768 until set terminator or max attempts.

Validation:
- Requires standard ID `CD001`, descriptor version 1, and logical block size >= 2048.
- Requires both a primary descriptor and a set terminator.

Root handling:
- Builds a one-extent view from root directory record.
- Calls `read_inode()` to create/cache root inode.
- Sets root inode `i_count = 1` and stores it in `v_pri`.

Role:
- Equivalent of superblock load for read-only ISO9660.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/super.h -->
# File Research: sources/teaching/minix/minix/fs/isofs/super.h

This header defines ISO9660 volume descriptor constants and primary volume descriptor structure.

Constants:
- Volume descriptor types: boot, primary, supplementary, partition, set terminator.
- `MAX_ATTEMPTS` for scanning volume descriptors.

`struct iso9660_vol_pri_desc`:
- Packed 2048-byte primary volume descriptor fields: IDs, volume sizes, logical block size, path table locations, root directory record, publisher/application fields, volume timestamps, and padding.
- Appends in-memory fields: `inode_root` and `i_count`.
- Defines global `v_pri`.

Role:
- Shared volume descriptor state for mount, reads, stats, directory parsing, and SUSP handling.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/super.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/susp.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/susp.c

This file implements System Use Sharing Protocol parsing for isofs when Rock Ridge support is compiled in.

Key functions:
- `parse_susp(dir, buffer)`: handles fundamental SUSP entries.
- `parse_susp_buffer(dir, buffer, size)`: iterates SUSP entries and dispatches to fundamental SUSP or Rock Ridge parser.

Supported SUSP entries:
- `CE`: continuation area; recursively parses continuation data from another block.
- `PD`: padding.
- `SP`, `ER`, `ES`: ignored.
- `ST`: terminator; stops processing with `ECANCELED`.

Important behavior:
- Continuation parsing is limited to one logical block and comments note missing infinite-recursion protection.
- Rock Ridge parsing is skipped when `opt.norock` is true.
- Invalid entry length, zero signature, or too-small entries terminate parsing.

Role:
- Provides the generic extension entry walker used by `read_inode_susp()`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/susp.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/susp_rock_ridge.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/susp_rock_ridge.c

This file implements Rock Ridge Interchange Protocol parsing for isofs.

Key functions:
- `parse_susp_rock_ridge_plcl(dir, block)`: handles relocated/reparented directories by loading or reusing the inode at a target block.
- `parse_susp_rock_ridge_sl(dir, buffer, length)`: parses symbolic link components.
- `parse_susp_rock_ridge(dir, buffer)`: dispatches individual Rock Ridge entries.

Supported Rock Ridge entries:
- `PX`: POSIX mode, UID, GID.
- `PN`: device major/minor.
- `SL`: symbolic link target.
- `NM`: alternate POSIX name.
- `PL`/`CL`: parent/child link relocation.
- `RE`, `SF`: ignored.
- `TF`: POSIX timestamps in 7-byte ISO format; 17-byte format noted unsupported.

Important behavior:
- Symbolic link parsing handles normal components plus `.`, `..`, and root.
- Name and symlink buffers are bounded by `ISO9660_RRIP_MAX_FILE_ID_LEN`.
- Reparenting may reuse an already cached inode or read a target directory record to create one.

Notable risks:
- Several fields are read with direct casts from unaligned buffer offsets.
- Timestamp parsing comment notes 17-byte TF format is unsupported.
- PN parsing has a Minix-specific workaround guarded by disabled standard interpretation.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/susp_rock_ridge.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/table.c -->
# File Research: sources/teaching/minix/minix/fs/isofs/table.c

This file defines the isofs fsdriver dispatch table.

Registered operations:
- Mount/unmount, lookup, putnode.
- Read, getdents, readlink.
- Stat, mountpoint, statvfs.
- LMFS driver, block read/write, and flush hooks.

Disabled operations:
- `fdr_peek` and `fdr_bpeek` are inside `#if 0` because of subpage block size concerns.
- No write/create/unlink/rename operations are registered, matching read-only ISO9660 behavior.

Role:
- Binds the isofs implementation to MINIX fsdriver.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/isofs/table.c -->