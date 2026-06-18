# Group Research: group_698_linux_sources_os_linux_linux_fs_befs_befs_h_sources_os_linux_linux_f_f501d9e0b381

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/befs.h -->
# File Research: sources/os/linux/linux/fs/befs/befs.h

## Purpose
Core private BeFS header for the Linux kernel driver. It defines in-memory BeFS superblock and inode state, shared error codes, debug function prototypes, and helper conversions between BeFS inode addresses and logical block numbers.

## Main Interfaces
- `struct befs_mount_options`: parsed mount options for uid/gid override, debug flag, and I/O charset.
- `struct befs_sb_info`: in-memory superblock fields copied from disk, including block size, byte order, allocation group geometry, journal range, root/index inode addresses, mount options, and NLS table.
- `struct befs_inode_info`: BeFS-private inode payload embedded around `struct inode`; stores inode address, parent, attributes, flags/type, and either a datastream or short symlink buffer.
- `enum befs_err`: BeFS-local status codes for generic errors and B+tree traversal states.
- `BEFS_SB()` / `BEFS_I()`: private-data accessors.
- `iaddr2blockno()` / `blockno2iaddr()`: allocation-group address conversions.
- `befs_iaddrs_per_block()`: number of BeFS inode/block-run addresses per filesystem block.

## Dependencies
Includes `befs_fs_types.h` for on-disk and host structures, and includes `endian.h` at the end so conversion helpers can use the private superblock type.

## Research Notes
This header is the coupling point between the BeFS VFS layer, datastream mapper, B+tree reader, inode validation, superblock loading, and debug helpers. The driver treats BeFS as read-only at the VFS layer, so most mutable state here is mount/session metadata rather than allocation state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/befs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/befs_fs_types.h -->
# File Research: sources/os/linux/linux/fs/befs/befs_fs_types.h

## Purpose
Defines BeFS on-disk structures and their host-order equivalents. This file is the canonical layout contract for superblocks, inodes, datastreams, block runs, attributes, and B+tree metadata.

## Key Definitions
- Constants:
  - `BEFS_NAME_LEN`, `BEFS_SYMLINK_LEN`, `BEFS_NUM_DIRECT_BLOCKS`, `B_OS_NAME_LENGTH`.
  - `BEFS_DBLINDIR_BRUN_LEN`, fixed at 4, used by double-indirect datastream lookup.
- Superblock flags/magic:
  - `BEFS_SUPER_MAGIC1/2/3`, `BEFS_CLEAN`, `BEFS_DIRTY`.
  - Native byte-order markers and endian-specific constants.
- Inode flags:
  - `BEFS_INODE_IN_USE`, `BEFS_ATTR_INODE`, `BEFS_LONG_SYMLINK`, transaction/write flags.
- Bitwise filesystem-endian scalar types:
  - `fs16`, `fs32`, `fs64`, plus `befs_time_t`.
- Block-run structures:
  - `befs_disk_block_run` uses filesystem-endian fields.
  - `befs_block_run` uses CPU-endian fields.
- Superblock:
  - `befs_super_block` mirrors on-disk layout, including allocation-group geometry, log bounds, root directory, and indices inode.
- Datastream:
  - Direct block-run array, indirect run, double-indirect run, maximum range fields, and byte size.
- Inode:
  - `befs_inode` includes identity, ownership, mode, flags, timestamps, parent/attribute runs, type, inode size, datastream or inline symlink, and small-data area.
- B+tree:
  - `befs_disk_btree_super`, `befs_btree_super`, `befs_btree_nodehead`, and host node header.
  - Key type enum covers string and numeric key classes, though the current driver uses directory string keys.

## Research Notes
All disk structures are `PACKED`, making this file sensitive to unaligned access and endian conversion correctness. It intentionally separates disk-endian and CPU-endian representations for block runs, datastreams, and B+tree state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/befs_fs_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/btree.c -->
# File Research: sources/os/linux/linux/fs/befs/btree.c

## Purpose
Implements read-only traversal and lookup for BeFS B+trees, primarily directory indexes. It sits above `datastream.c`, which maps logical tree offsets to disk blocks.

## Main Functions
- `befs_bt_read_super()`: reads the B+tree superblock from datastream offset 0, converts fields to CPU byte order, dumps debug information, and validates `BEFS_BTREE_MAGIC`.
- `befs_bt_read_node()`: reads a B+tree node at a byte offset, handles buffer replacement, converts node header fields, and stores pointers into the buffer.
- `befs_btree_find()`: public exact string-key lookup. It reads the tree superblock, descends internal nodes via `befs_find_key()`, follows overflow links where needed, then searches the leaf and returns the stored value.
- `befs_find_key()`: binary search inside one node. It compares packed string keys and returns match, overflow, or not-found state.
- `befs_btree_read()`: public ordered traversal by key ordinal. It seeks to the first leaf and walks right-linked leaf nodes until the requested key index is reached.
- `befs_btree_seekleaf()`: descends to the first leaf node, with explicit handling for empty trees and empty internal nodes.
- `befs_leafnode()`: treats nodes with invalid overflow pointer as leaves.
- Layout helpers:
  - `befs_bt_keylen_index()`
  - `befs_bt_valarray()`
  - `befs_bt_keydata()`
  - `befs_bt_get_key()`
- `befs_compare_strings()`: bytewise string comparison with length tie-break.

## Data Model
A node contains:
1. `befs_btree_nodehead`
2. packed key bytes
3. aligned `fs16` key-end-offset array
4. `fs64` value array

The code uses 8-byte alignment for the key length index, noting that documented 4-byte rounding did not work in practice.

## Limitations and Risks
- The comments state this is currently only suitable for directory B+trees: duplicate keys and non-string key types are not implemented.
- `befs_bt_get_key()` allows `index == all_key_count`, which can address one past the valid key index in malformed paths.
- `befs_find_key()` assumes node key count is nonzero before reading the last key.
- The B+tree reader relies on on-disk node integrity; it does not deeply bounds-check key length arrays against buffer size.

## Dependencies
Uses `befs_read_datastream()` for all reads, endian helpers from `endian.h`, and BeFS diagnostics from `debug.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/btree.h -->
# File Research: sources/os/linux/linux/fs/befs/btree.h

## Purpose
Public BeFS B+tree API header.

## Interfaces
- `befs_btree_find()`: exact key lookup in a BeFS datastream-backed B+tree.
- `befs_btree_read()`: ordinal read/traversal of B+tree leaf entries, returning key, key size, and value.

## Research Notes
This small header exposes only the two operations needed by the VFS directory implementation: name lookup and directory iteration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/datastream.c -->
# File Research: sources/os/linux/linux/fs/befs/datastream.c

## Purpose
Maps BeFS datastream logical file blocks to physical block runs and reads datastream-backed data. This is the block mapping layer used by regular file reads, symlink reads, and B+tree reads.

## Main Functions
- `befs_read_datastream()`: converts byte position to logical file block, maps it with `befs_fblock2brun()`, reads the resulting block run through `befs_bread_iaddr()`, and optionally returns the offset within the buffer.
- `befs_fblock2brun()`: dispatches logical block mapping to direct, indirect, or double-indirect lookup based on datastream range limits.
- `befs_read_lsymlink()`: sequentially reads long symlink contents from a datastream into a caller buffer.
- `befs_count_blocks()`: estimates file space usage in filesystem blocks, including inode and indirect metadata.
- `befs_find_brun_direct()`: linear search through the inode’s direct block-run array; adjusts returned run to begin at the requested block.
- `befs_find_brun_indirect()`: reads indirect block-run blocks and linearly searches their entries.
- `befs_find_brun_dblindirect()`: computes indexes into double-indirect and indirect blocks for the fixed-size double-indirect region and reads only the needed mapping blocks.

## Constants
- `BAD_IADDR = {0, 0, 0}` is exported as a sentinel invalid inode/block address.

## Notable Details
- Direct and indirect regions map variable-length block runs, requiring linear accumulation.
- Double-indirect mapping assumes data block runs and indirect blocks are organized around `BEFS_DBLINDIR_BRUN_LEN`.
- Metadata block counting assumes indirect blocks in the double-indirect region are also fixed-length.

## Risks
- The double-indirect index calculation uses `indir_indx = dblindir_leftover / diblklen`; given surrounding comments, this is a sensitive calculation and likely worth cross-checking against BeFS format expectations.
- The code trusts datastream range fields from disk after inode conversion; corrupted ranges can push mapping into invalid block reads, with errors surfaced through `BEFS_ERR`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/datastream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/datastream.h -->
# File Research: sources/os/linux/linux/fs/befs/datastream.h

## Purpose
Public datastream API for BeFS.

## Interfaces
- `befs_read_datastream()`: read a block containing a datastream byte position.
- `befs_fblock2brun()`: map a logical file block to a BeFS block run.
- `befs_read_lsymlink()`: read a long symlink from datastream storage.
- `befs_count_blocks()`: count data and metadata blocks used by a datastream.
- `BAD_IADDR`: shared invalid block-run sentinel.

## Research Notes
This header exposes the block mapping primitives consumed by both `linuxvfs.c` and `btree.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/datastream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/debug.c -->
# File Research: sources/os/linux/linux/fs/befs/debug.c

## Purpose
Provides BeFS logging and optional debug dump helpers.

## Main Functions
- `befs_error()`: emits `pr_err` with superblock ID prefix.
- `befs_warning()`: emits `pr_warn` with superblock ID prefix.
- `befs_debug()`: emits `pr_debug` only under `CONFIG_BEFS_DEBUG`.
- `befs_dump_inode()`: debug-dumps raw inode fields, block runs, timestamps, symlink or datastream layout.
- `befs_dump_super_block()`: debug-dumps raw superblock fields.
- `befs_dump_index_entry()`: debug-dumps B+tree superblock fields.
- `befs_dump_index_node()`: debug-dumps B+tree node header fields.

## Conditional Code
Most dump output is compiled behind `CONFIG_BEFS_DEBUG`. There is also an unused `#if 0` block for small-data and run dumping.

## Dependencies
Uses endian conversion helpers and BeFS structures through `befs.h`.

## Research Notes
The file intentionally keeps runtime overhead low unless debug is enabled. Error and warning paths remain active and include the filesystem identifier.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/endian.h -->
# File Research: sources/os/linux/linux/fs/befs/endian.h

## Purpose
Centralizes BeFS endian conversion for scalar filesystem-endian types and composite structures.

## Main Helpers
- Scalar conversions:
  - `fs64_to_cpu()` / `cpu_to_fs64()`
  - `fs32_to_cpu()` / `cpu_to_fs32()`
  - `fs16_to_cpu()` / `cpu_to_fs16()`
- Composite conversions:
  - `fsrun_to_cpu()`: disk block run to host block run.
  - `cpu_to_fsrun()`: host block run to disk block run.
  - `fsds_to_cpu()`: disk datastream to host datastream, including all direct runs and range fields.

## Behavior
Conversion is driven by `BEFS_SB(sb)->byte_order`, set during superblock loading from the filesystem byte-order marker.

## Research Notes
Because BeFS volumes may be big- or little-endian, all disk field access depends on these helpers. The `fs*` types are `__bitwise`, making sparse-style type checking possible.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/inode.c -->
# File Research: sources/os/linux/linux/fs/befs/inode.c

## Purpose
Validates raw BeFS inodes before VFS inode construction.

## Main Function
- `befs_check_inode()`: checks:
  - inode magic equals `BEFS_INODE_MAGIC1`
  - inode’s self-recorded block address matches the VFS block number
  - `BEFS_INODE_IN_USE` flag is set

## Return Values
Returns `BEFS_OK` for usable inodes and `BEFS_BAD_INODE` for failed validation.

## Research Notes
This file performs focused structural sanity checks. Detailed inode conversion and VFS setup are handled in `linuxvfs.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/inode.h -->
# File Research: sources/os/linux/linux/fs/befs/inode.h

## Purpose
Prototype header for BeFS inode validation.

## Interface
- `befs_check_inode()`: validates a raw on-disk inode against expected block number and flags.

## Research Notes
Small single-purpose header used by `linuxvfs.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/io.c -->
# File Research: sources/os/linux/linux/fs/befs/io.c

## Purpose
Low-level BeFS disk I/O helper for reading a block by BeFS inode/block-run address.

## Main Function
- `befs_bread_iaddr()`: validates allocation group, converts `befs_inode_addr` to a logical block number with `iaddr2blockno()`, then reads it with `sb_bread()`.

## Error Handling
- Rejects allocation groups greater than `num_ags`.
- Logs and returns `NULL` on invalid address or failed buffer read.

## Research Notes
This is the bottom of the BeFS read stack. Higher layers map file positions to `befs_inode_addr`, then use this helper to fetch the actual buffer.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/io.h -->
# File Research: sources/os/linux/linux/fs/befs/io.h

## Purpose
Prototype header for low-level BeFS block read helper.

## Interface
- `befs_bread_iaddr()`: read a buffer for a BeFS inode/block-run address.

## Research Notes
Used by datastream code after logical-to-physical mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/linuxvfs.c -->
# File Research: sources/os/linux/linux/fs/befs/linuxvfs.c

## Purpose
Linux VFS integration for the BeFS driver. It registers the filesystem, mounts read-only block devices, builds VFS inodes from BeFS inodes, implements lookup/readdir through B+trees, maps file blocks for reads, handles symlinks, exports file handles, parses mount options, and reports filesystem stats.

## Filesystem Registration
- Defines `befs_fs_type` with:
  - name `befs`
  - `FS_REQUIRES_DEV`
  - `kill_block_super`
  - fs_context operations
- `init_befs_fs()` initializes the inode cache and registers the filesystem.
- `exit_befs_fs()` destroys cache and unregisters.

## VFS Operations
- Super operations:
  - inode allocation/free
  - put_super
  - statfs
  - show_options
- Directory operations:
  - `generic_read_dir`
  - `befs_readdir`
  - `generic_file_llseek`
  - `generic_setlease`
- Directory inode ops:
  - `befs_lookup`
- Address-space ops:
  - `befs_read_folio`
  - `befs_bmap`
- Symlink address-space ops:
  - `befs_symlink_read_folio`

## File Reading
- `befs_get_block()` rejects writes (`create` returns `-EPERM`), maps file logical blocks using `befs_fblock2brun()`, and fills a mapped buffer head.
- Regular files use `generic_ro_fops`.

## Directory Handling
- `befs_lookup()` optionally converts dentry names from mounted NLS charset to UTF-8, searches the directory B+tree, and instantiates the found inode.
- `befs_readdir()` iterates B+tree entries by ordinal `ctx->pos`, optionally converts UTF-8 names to NLS, and emits directory entries.

## Inode Loading
- `befs_iget()`:
  - maps Linux inode number to BeFS inode address
  - reads raw inode block
  - validates with `befs_check_inode()`
  - applies uid/gid mount overrides or disk ownership
  - synthesizes atime/ctime from BeFS modified time
  - handles short symlink inline storage
  - converts datastreams for regular files, directories, and long symlinks
  - computes `i_blocks` via `befs_count_blocks()`
  - assigns VFS ops based on mode

## Mount and Superblock
- `befs_fill_super()`:
  - forces read-only if mounted writable
  - reads superblock at block 0, accounting for x86 512-byte offset vs PPC location
  - calls `befs_load_sb()` and `befs_check_sb()`
  - sets filesystem block size and VFS superblock ops
  - creates root dentry
  - loads requested or default NLS table
- `befs_reconfigure()` allows only read-only remount.
- `befs_put_super()` frees charset, unloads NLS, and releases private superblock.

## Mount Options
- `uid`
- `gid`
- `iocharset`
- `debug`

`befs_show_options()` prints non-default uid/gid, charset, and debug option.

## Export Support
Defines export operations using generic file-handle helpers and BeFS inode lookup. Parent lookup uses stored BeFS parent metadata.

## Notable Risks
- `befs_get_parent()` calls `befs_iget()` with `befs_ino->i_parent.start`; this is a narrow use of the block-run field and is worth checking against intended BeFS parent address semantics.
- NLS conversion allocates per lookup/readdir name and returns `-EILSEQ` on unconvertible characters.
- Filesystem is explicitly read-only; attempts to map write blocks are denied.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/linuxvfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/super.c -->
# File Research: sources/os/linux/linux/fs/befs/super.c

## Purpose
Loads and validates BeFS superblock metadata.

## Main Functions
- `befs_load_sb()`:
  - detects disk byte order from `fs_byte_order`
  - converts disk superblock fields into `struct befs_sb_info`
  - converts log, root, and indices block runs
  - initializes `nls` to `NULL`
- `befs_check_sb()`:
  - validates all three BeFS magic values
  - accepts block sizes 1024, 2048, 4096, or 8192
  - rejects block sizes larger than `PAGE_SIZE`
  - verifies `1 << block_shift == block_size`
  - logs inconsistency if `ag_shift` disagrees with `blocks_per_ag`
  - rejects dirty or journal-nonempty filesystems

## Research Notes
The driver refuses to mount unclean BeFS volumes and instructs users to boot BeOS and mount the volume to clean the journal. This matches the driver’s read-only/non-journal-replay design.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/super.h -->
# File Research: sources/os/linux/linux/fs/befs/super.h

## Purpose
Prototype header for BeFS superblock load and validation.

## Interfaces
- `befs_load_sb()`: copy/convert on-disk superblock into in-memory private state.
- `befs_check_sb()`: validate private superblock state.

## Research Notes
Used by `linuxvfs.c` during mount.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/bfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/bfs/Kconfig

## Purpose
Kernel configuration entry for SCO UnixWare BFS filesystem support.

## Configuration
- Symbol: `BFS_FS`
- Type: tristate
- Prompt: `BFS file system support`
- Depends on: `BLOCK`
- Selects: `BUFFER_HEAD`

## Help Text
Describes BFS as the Boot File System used by SCO UnixWare for bootloader access to the kernel and important files, usually mounted at `/stand` on a UnixWare `STAND` slice. Notes that Linux can read/write these files and points to `Documentation/filesystems/bfs.rst`.

## Research Notes
The config allows BFS as built-in or module `bfs`, but warns root filesystem support cannot be modular.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/bfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/bfs/Makefile -->
# File Research: sources/os/linux/linux/fs/bfs/Makefile

## Purpose
Build file for the BFS filesystem driver.

## Build Rules
- `obj-$(CONFIG_BFS_FS) += bfs.o`
- `bfs-objs := inode.o file.o dir.o`

## Research Notes
The BFS module is composed of three implementation files: superblock/inode handling, file data/block mapping, and directory operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/bfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/bfs/bfs.h -->
# File Research: sources/os/linux/linux/fs/bfs/bfs.h

## Purpose
Private BFS driver header for in-core state, accessors, debug macro, and cross-file prototypes.

## Key Structures
- `struct bfs_sb_info`:
  - total blocks
  - free blocks/inodes
  - last file end block
  - last inode number
  - inode bitmap
  - global BFS mutex
- `struct bfs_inode_info`:
  - disk inode number
  - starting and ending data blocks
  - metadata buffer-head tracking for fsync
  - embedded VFS inode

## Constants
- `BFS_MAX_LASTI 513`: theoretical maximum last inode number, with comment explaining the practical root-directory limit that prevents using all 512 possible inodes.

## Helpers
- `BFS_SB()`
- `BFS_I()`
- `printf()` macro that logs with `BFS-fs` and function name.

## Exports
Declares BFS inode, file, address-space, and directory operation symbols shared across the three BFS source files.

## Research Notes
BFS uses a simple global mutex and contiguous file allocation model, reflected in the minimal private inode state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/bfs/bfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/bfs/dir.c -->
# File Research: sources/os/linux/linux/fs/bfs/dir.c

## Purpose
Implements BFS directory reading and directory inode operations: create, lookup, link, unlink, rename, and directory entry helpers.

## Directory Iteration
- `bfs_readdir()`:
  - validates directory position alignment to `BFS_DIRENT_SIZE`
  - reads directory blocks using contiguous block range from `BFS_I(dir)`
  - emits nonzero `ino` entries
  - advances `ctx->pos` by fixed directory-entry size

## Directory File Operations
- `read = generic_read_dir`
- `iterate_shared = bfs_readdir`
- `fsync = bfs_fsync`
- `llseek = generic_file_llseek`

`bfs_fsync()` syncs metadata buffer heads via `mmb_fsync()`.

## Inode Operations
- `bfs_create()`:
  - allocates new VFS inode
  - finds free inode bit under global BFS mutex
  - initializes regular-file inode ops and mapping ops
  - marks inode dirty
  - adds directory entry
- `bfs_lookup()`:
  - rejects names longer than `BFS_NAMELEN`
  - finds matching directory entry under mutex
  - loads target with `bfs_iget()`
- `bfs_link()`:
  - adds another directory entry, increments link count, updates ctime, and instantiates dentry
- `bfs_unlink()`:
  - finds matching entry, clears `de->ino`, marks metadata dirty, updates timestamps, decrements link count
- `bfs_rename()`:
  - supports only `RENAME_NOREPLACE`
  - rejects directory renames
  - finds old and optional new entries
  - adds new entry if needed, clears old entry, decrements overwritten inode link count

## Directory Entry Helpers
- `bfs_add_entry()` scans existing directory blocks for a free fixed-size slot, extends directory size only within preallocated directory blocks, fills fixed-length name field, and marks metadata dirty.
- `bfs_namecmp()` handles fixed-length BFS names and NUL termination.
- `bfs_find_entry()` scans directory contents by block and offset.

## Research Notes
BFS directories are fixed-record arrays in contiguous blocks. There is no directory block growth path here beyond consuming existing free slots, so `bfs_add_entry()` can return `-ENOSPC` even if free disk blocks exist.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/bfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/bfs/file.c -->
# File Research: sources/os/linux/linux/fs/bfs/file.c

## Purpose
Implements BFS regular file operations, page-cache address-space operations, and contiguous block allocation/movement.

## File Operations
- `generic_file_llseek`
- `generic_file_read_iter`
- `generic_file_write_iter`
- `generic_file_mmap_prepare`
- `filemap_splice_read`

## Block Movement
- `bfs_move_block()` reads one old block, copies data into a new block, marks new dirty, and forgets old buffer.
- `bfs_move_blocks()` moves an inclusive range of blocks to a new location.

## Block Mapping and Allocation
- `bfs_get_block()`:
  - maps existing blocks without allocation when `create == 0`
  - grants writes within existing allocation
  - checks filesystem block bounds
  - serializes allocation/movement under global BFS mutex
  - extends files in place if the file is currently the last allocated file
  - otherwise moves the whole file to the next free region after `si_lf_eblk`
  - updates free block count, last-file end block, inode range, and maps the result

## Address-Space Operations
- `bfs_writepages()`: mpage writeback.
- `bfs_read_folio()`: block read into folio.
- `bfs_write_begin()`: block write begin with failure cleanup.
- `bfs_bmap()`: generic block mapping.
- `bfs_aops`: dirty/invalidate/read/write/bmap/migrate hooks.

## Research Notes
BFS uses contiguous file allocation. Extending a non-last file may relocate the entire file, which is simple but expensive and sensitive to allocation accounting. The comment notes an assumption that inode writeback cannot update `inode->i_blocks` during part of allocation accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/bfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/bfs/inode.c -->
# File Research: sources/os/linux/linux/fs/bfs/inode.c

## Purpose
Implements BFS superblock operations, inode load/write/evict, mount, statfs, inode cache, and module registration.

## Inode Loading
- `bfs_iget()`:
  - validates inode number range
  - reads the inode table block
  - reconstructs Linux mode from disk `i_mode` lower bits and `i_vtype`
  - assigns directory or regular-file operations
  - loads contiguous block range, disk inode number, uid/gid, link count, size, block count, and timestamps

## Disk Inode Access
- `find_inode()` validates inode number, reads the inode table block, and returns a pointer to the on-disk inode inside the buffer.

## Inode Writeback
- `bfs_write_inode()`:
  - serializes under BFS mutex
  - writes vtype, inode number, mode, ownership, links, timestamps, block range, and end offset
  - syncs buffer for `WB_SYNC_ALL`

## Eviction
- `bfs_evict_inode()`:
  - truncates page cache
  - syncs or invalidates tracked metadata buffers
  - clears inode
  - for deleted inodes, zeroes disk inode, frees data blocks/inode bitmap bit, and adjusts `si_lf_eblk` if this was the last file

## Superblock and Statfs
- `bfs_put_super()` destroys mutex and frees private info.
- `bfs_statfs()` reports magic, block size, total/free blocks, total/free files, fsid, and name length.
- `bfs_sops` wires inode allocation/free, write, eviction, put_super, and statfs.

## Mount Path
- `bfs_fill_super()`:
  - allocates and initializes `bfs_sb_info`
  - sets block size to `BFS_BSIZE`
  - reads and validates BFS superblock magic/ranges
  - warns on unclean filesystem
  - computes `si_lasti`, handling the practical maximum inode warning
  - initializes reserved inode bits
  - loads root inode and root dentry
  - computes total/free blocks
  - verifies last block is readable
  - scans the inode table to validate file block ranges, build inode bitmap, count free inodes, subtract used blocks, and find last allocated file block

## Filesystem Registration
- `bfs_fs_type` registers name `bfs`, block-device requirement, fs_context initialization, and `kill_block_super`.
- `init_bfs_fs()` creates inode cache and registers filesystem.
- `exit_bfs_fs()` unregisters and destroys cache.

## Research Notes
The mount scan performs important consistency checks before accepting the filesystem. BFS write support is present, but constrained by contiguous allocation and a simple global lock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/bfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/binfmt_elf.c -->
# File Research: sources/os/linux/linux/fs/binfmt_elf.c

## Purpose
Main Linux ELF executable loader and ELF core dumper. It registers the standard ELF binary format, validates ELF images, maps executable/interpreter segments, builds the initial user stack and aux vector, starts execution, and emits ELF core files under `CONFIG_ELF_CORE`.

## Loader Registration
- `elf_format` provides:
  - `load_binary = load_elf_binary`
  - `core_dump = elf_core_dump` when coredumps are enabled
  - `min_coredump = ELF_EXEC_PAGESIZE`
- Registered with `core_initcall(init_elf_binfmt)` and removed at module exit.

## Stack and Aux Vector
- `create_elf_tables()`:
  - aligns stack
  - copies platform/base-platform strings if provided
  - generates `AT_RANDOM`
  - fills `mm->saved_auxv`
  - emits hardware capability, page size, clock tick, program header info, base, flags, entry, credentials, secureexec, execfn, execfd, rseq, and platform aux entries
  - lays out `argc`, argv pointers, envp pointers, and auxv on the new user stack
  - updates `arg_start/end` and `env_start/end`

## Segment Mapping
- `padzero()`: clears trailing partial page after file-backed segment contents.
- `elf_map()`: maps file-backed segment bytes, using `total_size` for first mapping to reserve the full image and then unmap holes.
- `elf_load()`: maps file data and zeroes/maps bss-like memory through `vm_brk_flags()`.
- `total_mapping_size()`: computes contiguous PT_LOAD span.
- `maximum_alignment()`: computes maximum power-of-two PT_LOAD alignment.

## ELF Validation and Program Header Loading
- `elf_read()` wraps exact-size `kernel_read()`.
- `load_elf_phdrs()` validates program header entry size/count/total size and reads headers.
- Architecture hooks:
  - `arch_elf_pt_proc()`
  - `arch_check_elf()`
  - `arch_elf_adjust_prot()` through `make_prot()`
- GNU property parsing:
  - `parse_elf_properties()`
  - `parse_elf_property()`

## Main Exec Flow
`load_elf_binary()`:
1. Validates ELF magic, type, architecture, non-FDPIC, and mmap capability.
2. Loads program headers.
3. Handles `PT_INTERP`: reads interpreter path, opens interpreter, applies `would_dump()`, and reads interpreter ELF header.
4. Processes `PT_GNU_STACK`, processor-specific headers, interpreter headers, and GNU properties.
5. Allows architecture final rejection through `arch_check_elf()`.
6. Calls `begin_new_exec()`, sets personality, applies `READ_IMPLIES_EXEC`, snapshots ASLR state, and calls `setup_new_exec()`.
7. Sets up argument pages.
8. Maps every PT_LOAD segment with correct protections and ET_EXEC/ET_DYN placement rules.
9. Handles PIE/static-PIE load bias, alignment, interpreter mapping, and brk placement/randomization.
10. Creates ELF tables, sets mm code/data/stack bounds, optionally maps page zero for SVr4 compatibility, applies platform register initialization, finalizes exec, and starts the thread.

## Core Dump Support
Under `CONFIG_ELF_CORE`, the file implements:
- ELF note helpers (`memelfnote`, `notesize`, `writenote`)
- ELF/core/program-header construction helpers
- process and thread notes:
  - `NT_PRSTATUS`
  - `NT_PRPSINFO`
  - `NT_SIGINFO`
  - `NT_AUXV`
  - `NT_FILE`
  - regset-backed notes
- `fill_files_note()` records mapped files for debuggers.
- `elf_core_dump()` writes ELF header, note phdr, PT_LOAD phdrs for VMAs, arch extra phdr/data, notes, VMA memory ranges, and extended numbering section header when needed.

## Security and Robustness Notes
- Validates interpreter path size and NUL termination.
- Uses `MAP_FIXED_NOREPLACE` for collision-sensitive executable mappings.
- Checks `p_filesz <= p_memsz`, task-size overflow, and mmap capability.
- Preserves `would_dump()` behavior for unreadable binaries with interpreters.
- GNU property parsing enforces sorted unique property types.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/binfmt_elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/binfmt_elf_fdpic.c -->
# File Research: sources/os/linux/linux/fs/binfmt_elf_fdpic.c

## Purpose
Implements the ELF-FDPIC binary format loader and FDPIC core dumper. FDPIC supports position-independent executables with explicit load maps, especially for NOMMU and embedded architectures.

## Registration
- `elf_fdpic_format` provides:
  - `load_binary = load_elf_fdpic_binary`
  - `core_dump = elf_fdpic_core_dump` under `CONFIG_ELF_CORE`
- Registered with `core_initcall(init_elf_fdpic_binfmt)`.

## ELF Identification
- `is_elf()` checks ELF magic, type `ET_EXEC`/`ET_DYN`, architecture, and mmap capability.
- `elf_check_fdpic()` determines FDPIC support; non-FDPIC ELF is delegated to standard `binfmt_elf` on MMU systems.
- `is_constdisp()` determines whether constant displacement mapping should be used.

## Program Header Handling
- `elf_fdpic_fetch_phdrs()` validates header entry size/count, reads headers, and extracts `PT_GNU_STACK` stack permissions and requested stack size.

## Main Exec Flow
`load_elf_fdpic_binary()`:
1. Initializes executable and interpreter parameter structures.
2. Validates executable and FDPIC constraints.
3. Reads executable program headers.
4. Scans for `PT_INTERP`, opens interpreter, applies `would_dump()`, and reads interpreter header.
5. Reads interpreter program headers when present.
6. Determines stack size and executable-stack policy.
7. Calls `begin_new_exec()`, sets personality including `PER_LINUX_FDPIC`, applies `READ_IMPLIES_EXEC`, and sets up new exec state.
8. Lays out stack/brk for MMU or NOMMU.
9. Maps executable and interpreter with `elf_fdpic_map_file()`.
10. Creates user stack tables and load maps with `create_elf_fdpic_tables()`.
11. Applies architecture platform initialization, finalizes exec, and starts the thread at interpreter or executable entry.

## User Stack and Load Maps
- `create_elf_fdpic_tables()`:
  - copies platform/base-platform strings
  - copies executable and interpreter load maps onto user stack
  - records load map addresses in `mm->context`
  - builds aux vector including `AT_BASE`, `AT_ENTRY`, credentials, secureexec, execfn, execfd, and platform entries
  - lays out argc/argv/envp and updates mm argument/environment bounds

## Mapping Logic
- `elf_fdpic_map_file()`:
  - counts PT_LOAD segments
  - allocates flexible load map
  - dispatches to constant-displacement mapping on NOMMU or direct mmap
  - resolves entry point, program header address, and dynamic section address
  - validates dynamic section has aligned entries and final NULL tag
  - merges adjacent load map segments on MMU where possible
- `elf_fdpic_map_file_constdisp_on_uclinux()`:
  - NOMMU constant-displacement loader using one anonymous allocation and `read_code()`
- `elf_fdpic_map_file_by_direct_mmap()`:
  - maps PT_LOAD segments independently, honoring arrangement flags
  - clears leading/trailing/excess bytes and maps anonymous memory for bss extension on MMU

## Core Dump Support
Under `CONFIG_ELF_CORE`:
- Adds FDPIC load map addresses to `elf_prstatus_fdpic`.
- Builds thread status notes with register and optional fpreg data.
- Writes ELF header, note phdr, PT_LOAD phdrs for VMAs, extra core phdr/data, notes, and dumped VMA ranges.
- Supports extended program header numbering through a synthetic section header.

## Research Notes
This file parallels `binfmt_elf.c` but has FDPIC-specific state: executable/interpreter load maps, per-segment runtime addresses independent from virtual addresses, and NOMMU-specific mapping paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/binfmt_elf_fdpic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/binfmt_flat.c -->
# File Research: sources/os/linux/linux/fs/binfmt_flat.c

## Purpose
Implements the Linux `bFLT` flat binary loader, primarily for NOMMU/embedded systems, with optional compressed FLAT support and relocation processing.

## Registration
- `flat_format` provides `load_binary = load_flat_binary`.
- Registered at `core_initcall(init_flat_binfmt)`.

## Format State
- `struct lib_info` stores one supported library/program slot:
  - code/data/brk starts
  - text length
  - entry point
  - build date
  - loaded flag
- `MAX_SHARED_LIBS` is 1 in this implementation.
- Constants:
  - `FLAT_DATA_ALIGN`
  - `FLAT_STACK_ALIGN`
  - `RELOC_FAILED`
  - `UNLOADED_LIB`

## Stack Table Setup
- `create_flat_tables()` builds argc, argv, envp, and optional argvp/envp pointers on the user stack, updating `arg_start/end` and `env_start/end`.

## Optional Compressed FLAT
Under `CONFIG_BINFMT_ZFLAT`:
- `decompress_exec()` parses gzip headers, validates unsupported flags, inflates file data using zlib, and writes into destination memory.

## Relocation
- `calc_reloc()` maps relocation offsets into runtime text or data addresses and sends `SIGSEGV` on invalid relocation.
- `old_reloc()` supports legacy flat relocation records under `CONFIG_BINFMT_FLAT_OLD`.
- `skip_got_header()` skips RISC-V GOT PLT headers before GOT relocation.
- `load_flat_file()` performs:
  - header parsing and magic/version validation
  - sanity checks for large/corrupt sizes
  - data rlimit check
  - `begin_new_exec()`, personality setup, and memory mapping/allocation
  - optional ROM text mapping for NOMMU
  - optional compressed code/data loading
  - code/data/brk/stack mm field setup
  - GOT relocation
  - relocation table processing
  - instruction-cache flush
  - zeroing bss, brk, and stack area

## Main Exec Flow
`load_flat_binary()`:
1. Computes required stack length including argv/envp pointer arrays and, on NOMMU, argument string pages.
2. Calls `load_flat_file()`.
3. Writes library data-start pointers or `UNLOADED_LIB` sentinels.
4. Sets the active binary format.
5. Sets up arg pages or NOMMU stack and creates flat tables.
6. Applies platform initialization if present.
7. Finalizes exec and starts the thread at the flat entry point.

## Security and Robustness Notes
- Validates magic, version, compression support, and high bits of size fields.
- Enforces `RLIMIT_DATA` against data plus bss.
- Uses `read_code()`, `copy_to_user()`, and relocation helpers with error checks.
- Relocation failures abort exec or signal the current task for invalid offsets.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/binfmt_flat.c -->