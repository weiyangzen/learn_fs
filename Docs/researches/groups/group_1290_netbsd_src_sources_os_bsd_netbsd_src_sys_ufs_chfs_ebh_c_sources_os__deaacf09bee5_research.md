# Group Research: group_1290_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_chfs_ebh_c_sources_os__deaacf09bee5

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh.c

This is the CHFS eraseblock handler implementation. It provides the logical eraseblock API declared in `ebh.h`, owns LEB-to-PEB mapping state, implements NOR/NAND-specific eraseblock header formats, scans flash on open, maintains free/in-use/erase queues, and runs a background erase thread.

Key responsibilities:
- Flash header protocol: `nor_*` and `nand_*` functions create, read, validate, write, dirty-mark, invalidate, and free eraseblock headers.
- Logical block locking: an RB tree of `chfs_ltree_entry` objects gives per-LEB reader/writer locking with reference-counted tree entries.
- Wear-leveling state: free PEBs are ordered by erase count, in-use PEBs by physical number, and erase candidates are kept in TAILQs.
- Media scan/recovery: `chfs_scan`, `nor_process_eb`, and `nand_process_eb` classify PEBs into corrupted, free, erased, erase-needed, and used sets.
- Public operations: `ebh_open`, `ebh_close`, `ebh_read_leb`, `ebh_write_leb`, `ebh_erase_leb`, `ebh_map_leb`, `ebh_unmap_leb`, `ebh_is_mapped`, and `ebh_change_leb`.

Important behavior:
- NOR headers use a dirty bit in the logical ID and can invalidate old headers by zeroing CRC/LID. During atomic change, the old NOR header is first marked dirty, then the new PEB is written, then the old header is invalidated.
- NAND headers use a monotonically increasing serial number. Recovery chooses the higher serial when multiple PEBs reference the same LEB.
- `get_peb` takes the lowest-erase-count free PEB, or synchronously erases queued PEBs if no free PEB is available.
- `erase_thread` waits on `eth_wakeup` and processes `to_erase`/`fully_erased` queues via `free_peb`.
- Unmapped LEB reads return a buffer filled with `0xff`.

Dependencies:
- NetBSD flash API: `flash_read`, `flash_write`, `flash_erase`, `flash_block_isbad`, `flash_block_markbad`, `flash_get_device`, `flash_get_interface`, `flash_get_size`.
- CHFS helpers/macros from `ebh.h`, `ebh_media.h`, `ebh_misc.h`, and `debug.h`.
- Kernel RB tree, TAILQ, mutex, rwlock, condvar, kthread, and kmem APIs.

Notable implementation risks:
- Several paths assume valid `lnr` indices into `ebh->lmap`; bounds are enforced mainly by callers or assertions.
- `ebh_close` frees `ebh` itself, so callers must not use or separately free the descriptor after closing.
- `ebh_open` also frees `ebh` on scan failure, which is unusual for an initializer taking caller-supplied storage.
- `release_peb` removes a PEB from the in-use tree but does not free the removed tree object there; ownership is easy to misread because erase queue entries are separately allocated.
- `erase_callback` requeues failed erases without consistently taking `erase_lock` in the non-DONE branch.
- `ebh_change_leb` calls `find_peb_in_use` without holding `erase_lock`, then calls `release_peb`, and later frees `peb`; this is a sensitive ownership/locking area.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh.h

This is the public/internal CHFS eraseblock handler header. It defines in-memory eraseblock header wrappers, scan structures, eraseblock state structures, operation tables, the main `chfs_ebh` descriptor, and the public EBH API.

Key definitions:
- `struct chfs_eb_hdr`: combines common erase-counter header with either NOR or NAND header.
- LEB status enum: unmapped, mapped, dirty, invalid, erase, erased, free.
- EB header status enum: OK, dirty, invalidated, bad magic, bad CRC, free, no header.
- `struct chfs_ltree_entry`: per-logical-eraseblock RB tree entry with user count and rwlock.
- `struct chfs_scan_leb` / `struct chfs_scan_info`: temporary scan results grouped into queues and a used RB tree.
- `struct chfs_peb`: physical eraseblock metadata used in free/in-use trees and erase queues.
- `struct chfs_ebh_ops`: flash-type-specific operations for header I/O, validation, recovery, creation, and data offset calculation.
- `struct chfs_ebh`: the runtime eraseblock handler descriptor, including flash device/interface, maps, locks, queues, trees, background erase thread, and NAND max serial.

Public API:
- Open/close: `ebh_open`, `ebh_close`.
- I/O: `ebh_read_leb`, `ebh_write_leb`, `ebh_change_leb`.
- Mapping lifecycle: `ebh_map_leb`, `ebh_unmap_leb`, `ebh_erase_leb`, `ebh_is_mapped`.

Dependencies:
- Kernel-only includes for NetBSD types, trees, queues, locks, kmem, kthread, and flash interface.
- Always includes `ebh_media.h` for on-media header structures.

Design notes:
- `chfs_ebh_ops` abstracts NOR/NAND differences while keeping shared scan, lock, and wear-leveling logic in `ebh.c`.
- `max_serial` is meaningful only for NAND.
- `layout_map` and an older mutex field are commented out, indicating unfinished or abandoned layout-level logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh_media.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh_media.h

This header defines the on-flash eraseblock header layout for CHFS EBH metadata.

Key definitions:
- Little-endian aliases: `le16`, `le32`, `le64`.
- `CHFS_MAGIC_BITMASK`: eraseblock header magic.
- `CHFS_LID_NOT_DIRTY_BIT` and `CHFS_LID_DIRTY_BIT_MASK`: NOR logical-ID dirty-state encoding.
- Size macros for common erase counter header, NOR header, NAND header, and invalidation payload.
- `struct chfs_eb_ec_hdr`: common packed erase counter header with magic, CRC of erase count, and erase count.
- `struct chfs_nor_eb_hdr`: packed NOR header with CRC and LID. Dirty and invalidated states are encoded in the LID/CRC fields.
- `struct chfs_nand_eb_hdr`: packed NAND header with CRC, LID, and serial number for duplicate-resolution recovery.

Dependencies:
- Requires fixed-width integer types from includers.
- Used by `ebh.h` and `ebh.c` to interpret and write media headers.

Design notes:
- NOR recovery relies on the ability to change programmed bits from one to zero.
- NAND recovery relies on serial ordering rather than dirty-bit mutation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh_media.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh_misc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh_misc.h

This header provides small EBH utility macros.

Key macros:
- `CHFS_GET_MEMBER_POS(type, member)`: computes member offset using a null pointer expression.
- `CHFS_GET_LID(lid)`: converts a little-endian LID to host order and masks off the NOR dirty bit.
- `EBH_TREE_DESTROY`: removes and frees every node in an RB tree.
- `EBH_TREE_DESTROY_MUTEX`: same as `EBH_TREE_DESTROY`, but also destroys each node’s rwlock.
- `EBH_QUEUE_DESTROY`: removes and frees every node in a TAILQ.

Dependencies:
- Kernel RB tree, TAILQ, `kmem_free`, and for the mutex variant, `rw_destroy`.
- `CHFS_GET_LID` depends on `CHFS_LID_DIRTY_BIT_MASK` from `ebh_media.h`.

Design notes:
- These macros are destructive and assume exclusive ownership of the tree/queue.
- The mutex destroy macro is marked as a hack, reflecting that lock lifetime is embedded in RB-tree node lifetime.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/media.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/media.h

This header defines CHFS on-flash filesystem node formats, distinct from EBH eraseblock headers.

Key definitions:
- Node type enum: vnode metadata, data node, directory entry, padding.
- `CHFS_NODE_HDR_SIZE`, `CHFS_MAX_NODE_SIZE`, and `CHFS_FS_MAGIC_BITMASK`.
- `struct chfs_flash_node_hdr`: common packed node header with magic, type, length, and header CRC.
- `struct chfs_flash_vnode`: packed vnode metadata node with vnode number, version, ownership, mode, size, timestamps, and node CRC.
- `struct chfs_flash_data_node`: packed data node with vnode number, version, file offset, data length, data CRC, node CRC, and flexible data payload.
- `struct chfs_flash_dirent_node`: packed directory entry node with child/parent vnode numbers, version, mctime, name length, dtype, name CRC, node CRC, and flexible name payload.
- `struct chfs_flash_padding_node`: packed padding node.

Dependencies:
- Requires fixed-width integer types from includers.
- Uses local little-endian aliases when `_LE_TYPES` is not already defined.

Design notes:
- This file is the CHFS node-level media ABI. EBH metadata decides where logical eraseblock payload starts; these node formats describe what CHFS stores inside that payload.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/media.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/Makefile

This kernel include makefile installs ext2fs public headers under `/usr/include/ufs/ext2fs`.

Installed headers:
- `ext2fs.h`
- `ext2fs_dinode.h`
- `ext2fs_dir.h`
- `ext2fs_extents.h`
- `ext2fs_extern.h`

It sets `INCSDIR` and includes NetBSD’s `bsd.kinc.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs.h

This is the main ext2/ext3/ext4-compatible filesystem format and in-memory mount header.

Key definitions:
- Boot/superblock offsets and sizes: `BBSIZE`, `SBSIZE`, `BBOFF`, `SBOFF`, `BBLOCK`, `SBLOCK`.
- Block conversion and sizing macros: `fsbtodb`, `lblkno`, `blksize`, `EXT2_FSBTODB*`, `EXT2_DBTOFSB`, `ext2_blkoff`, `ext2_lblkno`, etc.
- `struct ext2fs`: on-disk superblock layout including ext2, ext3, and ext4-era fields.
- `struct m_ext2fs`: in-memory mount-time derived fields such as block size, shifts, group count, inode-per-block count, group descriptor table, read-only/modified flags, and hash signedness.
- Feature flags for compatible, read-only-compatible, and incompatible features.
- Supported feature masks: this implementation supports selected sparse super, largefile, huge file, extra inode size, dir nlink, group descriptor checksum, file type, extents, flex_bg, and 64-bit features.
- Error behavior, creator OS, clean-state flags.
- `struct ext2_gd`: ext2/ext4 block group descriptor including high 32-bit block references and checksum-related fields.
- Group descriptor checksum support macro `E2FS_HAS_GD_CSUM`.
- Sparse-super helper `cg_has_sb`.
- Endian conversion macros and byte-swap function declaration for big-endian systems.
- Inode and cylinder-group location macros.

Dependencies:
- Includes `sys/bswap.h`.
- Used broadly by all ext2fs implementation files.

Design notes:
- Superblock fields are represented with fixed-width integer types matching disk layout, but not all ext4 features listed are supported for read/write operation.
- Group descriptors are noted as not byte-swapped outside kernel context.
- Many macros assume `m_ext2fs` derived fields are initialized correctly during mount.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_alloc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_alloc.c

This file implements ext2fs block and inode allocation/freeing, bitmap updates, group descriptor counter maintenance, group descriptor checksum handling, and lazy initialization of ext4 uninitialized bitmaps/inode tables.

Key public functions:
- `ext2fs_alloc`: allocates a data block, respecting reserved-space policy and preferred block selection.
- `ext2fs_valloc`: allocates an inode, choosing directory placement via `ext2fs_dirpref`.
- `ext2fs_blkpref`: chooses a preferred block for locality/contiguity.
- `ext2fs_blkfree`: frees a block and updates bitmap/group counters.
- `ext2fs_vfree`: frees an inode and updates bitmap/group counters.
- `ext2fs_cg_verify_and_initialize`: verifies group descriptor checksums and zeroes uninitialized inode-table ranges when mounting read-write.

Key internal functions:
- `ext2fs_hashalloc`: preferred group, quadratic rehash, then brute-force allocator search.
- `ext2fs_alloccg`: allocates a block from a specific cylinder group bitmap.
- `ext2fs_nodealloccg`: allocates an inode from a specific inode bitmap.
- `ext2fs_mapsearch`: finds a free bit in a block bitmap.
- `ext2fs_cg_update`: updates low/high free block, free inode, directory counts, inode-table-unused, and group descriptor checksum.
- `ext2fs_cg_get_csum`: computes ext4 metadata checksum or legacy group descriptor checksum.
- `ext2fs_init_bb`: initializes an uninitialized block bitmap.

Dependencies:
- NetBSD vnode/buffer APIs: `bread`, `bdwrite`, `getblk`, `clrbuf`.
- UFS inode and mount structures.
- `crc16` and an in-file CRC32C table for ext4 metadata checksums.
- Ext2fs superblock and group descriptor macros from `ext2fs.h`.

Important behavior:
- Allocation decrements global and group free counters and marks the superblock modified.
- Freeing validates range/duplicate-free conditions; duplicate free of a block panics.
- Lazy ext4 group initialization is supported for block and inode bitmaps and inode tables when descriptor checksum features are present.
- Directory inode placement chooses groups with above-average free inodes and high free block count.

Notable implementation risks:
- The checksum path is sensitive because descriptor data must be in little-endian disk encoding when checksummed.
- Error returns from bitmap reads often degrade to allocation failure instead of surfacing the exact I/O error.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_balloc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_balloc.c

This file implements logical block allocation for file data and indirect block trees.

Key public functions:
- `ext2fs_balloc`: allocates or resolves the physical storage backing a logical block.
- `ext2fs_gop_alloc`: allocates a byte range for the generic pager/write path, extending file size as needed.

Important behavior:
- Direct blocks are handled through the first `EXT2FS_NDADDR` inode block pointers.
- Indirect blocks are resolved with `ufs_getlbns`, using negative logical block numbers for metadata blocks.
- Newly allocated indirect blocks are cleared and written synchronously before being referenced, avoiding pointers to garbage after a crash.
- Data block allocation uses `ext2fs_alloc` and preferred-block hints from `ext2fs_blkpref`.
- On partial failure, allocated blocks are freed, indirect pointers are unwound, invalid buffers are released, and inode block counts are adjusted.

Dependencies:
- UFS inode helpers and `ufs_getlbns`.
- Ext2fs allocation functions from `ext2fs_alloc.c`.
- Buffer cache APIs: `bread`, `getblk`, `bwrite`, `bdwrite`, `brelse`.
- UVM history instrumentation when enabled.

Notable implementation risks:
- The function is built around classic ext2 block pointers; extent-based allocation is not handled here.
- The failure path is complex and depends on `unwindidx`, `allociblk`, and correct pointer restoration.
- One flag update in the deallocation path uses `ip->i_e2fs_flags |= IN_CHANGE | IN_UPDATE`, which mixes inode flags with ext2 disk flags naming; this is worth rechecking when modifying.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_bmap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_bmap.c

This file implements VOP_BMAP support, converting file logical block numbers to device block numbers.

Key functions:
- `ext2fs_bmap`: VOP entry point. Returns the underlying device vnode and dispatches to extent or classic block-pointer mapping.
- `ext4_bmapext`: maps logical blocks through ext4 extents using `ext4_ext_find_extent`.
- `ext2fs_bmaparray`: maps logical blocks through direct and indirect ext2 block pointers.

Important behavior:
- If the inode has `EXT2_EXTENTS`, mapping uses the extents path.
- Sparse or unmapped blocks return `-1` in `a_bnp`.
- Direct block mapping can compute sequential run length for clustering.
- Indirect mapping uses `ufs_getlbns`, checks cached indirect buffers with `incore`, reads missing indirect buffers through strategy I/O, and can compute run length within the final indirect block.
- Indirect metadata logical block numbers follow UFS negative-lbn conventions.

Dependencies:
- UFS inode/mount helpers and `blkptrtodb`.
- Ext2fs extent lookup from `ext2fs_extents.c`.
- Buffer cache and vnode strategy I/O APIs.

Design notes:
- This is mapping-only; it does not allocate blocks.
- Extent mapping sets `runp` and optional `runb` based on extent length or sparse range.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_bswap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_bswap.c

This file provides byte-swapping support for ext2fs on big-endian systems. It is compiled as meaningful code only when `BYTE_ORDER == BIG_ENDIAN`.

Key functions:
- `e2fs_sb_bswap`: swaps selected superblock fields between disk little-endian and host order, preserving unused fields by first copying the full structure.
- `e2fs_i_bswap`: swaps inode fields for a given on-disk inode size, including ext4 extra inode fields only when they fit.

Dependencies:
- `sys/endian.h`, `ext2fs.h`, `ext2fs_dinode.h`.
- Kernel `systm.h` or userland `string.h`.

Important behavior:
- Little-endian builds use macros in headers that reduce load/save operations to `memcpy`; this file only matters on big-endian.
- Inode swapping respects `EXT2_REV0_DINODE_SIZE` and `EXT2_DINODE_FITS` to avoid touching fields not present in older/smaller inodes.

Design notes:
- Not every modern superblock field is explicitly swapped; preserved fields remain copied as-is unless listed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_bswap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_dinode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_dinode.h

This header defines the ext2/ext3/ext4 on-disk inode format and inode-related constants/macros.

Key definitions:
- Reserved inode numbers: bad blocks, root, ACL, bootloader, undelete, resize, journal, first normal inode.
- `EXT2FS_NDADDR` and `EXT2FS_NIADDR`, matching UFS direct/indirect address counts.
- `struct ext2fs_dinode`: on-disk inode fields including mode, uid/gid, size, times, link count, block count, flags, block pointer array, generation, ACL, high size/block fields, checksums, extra inode size, nanosecond/epoch time fields, birth time, version high, and project id.
- `i_e2fs_*` macros mapping NetBSD in-memory inode fields to ext2 dinode members.
- Ext2 permission, file type, and file flag constants.
- Inode size helpers: `EXT2_DINODE_SIZE`, `EXT2_DINODE_FITS`.
- Time helpers: `ext2fs_dinode_time_get`, `EXT2_DINODE_TIME_GET`, `ext2fs_dinode_time_set`, `EXT2_DINODE_TIME_SET`.
- Overlay macros for device numbers and short symlinks.
- Endian load/save macros and big-endian byte-swap declaration.

Dependencies:
- `sys/stat.h`.
- `stddef.h` outside kernel/standalone for `offsetof`.

Design notes:
- Extra timestamp fields encode nanoseconds plus high epoch bits. The getter preserves Linux compatibility behavior for the `epoch_bits == 3` negative-time case.
- Short symlink data overlays the block pointer array.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_dir.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_dir.h

This header defines ext2 directory entry formats and directory helper macros.

Key definitions:
- `doff_t` as 32-bit directory offset and `EXT2FS_MAXDIRSIZE`.
- `EXT2FS_MAXNAMLEN` as 255.
- `struct ext2fs_direct`: on-disk variable-length directory entry header plus maximum name storage.
- `enum ext2fs_slotstatus` and `struct ext2fs_searchslot`: state used by lookup/insert code to track reusable directory space.
- Ext2 directory file type constants and conversion helpers:
  - `inot2ext2dt`: inode mode to ext2 directory type.
  - `ext2dt2dt`: ext2 directory type to NetBSD `DT_*`.
- `EXT2FS_DIRSIZ` and `EXT2_DIR_REC_LEN`: record length calculations.
- `struct ext2fs_dirtemplate`: template for `.` and `..` directory initialization.

Dependencies:
- `sys/dirent.h`
- `ext2fs_dinode.h`

Design notes:
- The header documents the ext2 rev0/rev1 split of `namlen` and `type`.
- Directory free space is represented by oversized `reclen` fields or zero inode entries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extents.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extents.c

This file implements read-side ext4 extent lookup and a small extent cache.

Key public functions:
- `ext4_ext_in_cache`: checks the inode extent cache for a logical block.
- `ext4_ext_put_cache`: stores an extent or sparse gap in the inode extent cache.
- `ext4_ext_find_extent`: walks the inode’s extent tree to locate the extent or sparse range covering a logical block.

Key internal functions:
- `ext4_ext_binsearch_index`: binary-searches an index node and detects sparse ranges before the first indexed block.
- `ext4_ext_binsearch`: binary-searches a leaf extent list and detects sparse gaps before, between, or after extents.

Important behavior:
- The root extent header is stored in the inode’s `e2di_blocks` array.
- Interior nodes are read from disk using index entries’ physical block references.
- `struct ext4_extent_path` carries the current buffer, header, selected index/extent, and sparse result.
- Sparse ranges are represented as synthetic extents with zero physical start and `ep_is_sparse = true`.

Dependencies:
- Ext2fs and UFS inode/buffer APIs.
- `ext2fs_extents.h` for extent structures.
- `bread`/`brelse` for reading extent tree blocks.

Design notes:
- This is lookup support only; there is no extent allocation, insertion, or deletion here.
- Callers must release `path->ep_bp` if non-null.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extents.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extents.h

This header defines ext4 extent structures and lookup APIs used by NetBSD ext2fs.

Key definitions:
- `EXT4_EXT_MAGIC`
- Extent cache result types: no hit, sparse gap, in extent.
- `struct ext4_extent`: leaf extent with logical start, length, and high/low physical start.
- `struct ext4_extent_index`: interior-tree entry pointing to a lower-level block.
- `struct ext4_extent_header`: tree header with magic, entry count, capacity, depth, and generation.
- `struct ext4_extent_cache`: cached logical-to-physical extent or gap.
- `struct ext4_extent_path`: traversal result/path object holding depth, buffer, sparse state, selected extent/index/header.

Public prototypes:
- `ext4_ext_in_cache`
- `ext4_ext_put_cache`
- `ext4_ext_find_extent`

Dependencies:
- `ufs/ufs/inode.h`, `sys/types.h`, and `stdbool.h` outside kernel.
- Forward declarations for `struct inode` and `struct m_ext2fs`.

Design notes:
- Structures mirror ext4 disk format but are used here for read-side lookup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extents.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extern.h

This is the central ext2fs internal/public kernel prototype header.

Key contents:
- Forward declarations for kernel VFS, vnode, inode, mount, directory, and buffer-related types.
- External pools: `ext2fs_inode_pool`, `ext2fs_dinode_pool`.
- `EXT2FS_ITIMES` macro to apply pending inode time updates.
- Prototypes grouped by implementation file:
  - Allocation: `ext2fs_alloc`, `ext2fs_realloccg`, `ext2fs_valloc`, `ext2fs_blkpref`, `ext2fs_blkfree`, `ext2fs_vfree`, `ext2fs_cg_verify_and_initialize`.
  - Block allocation: `ext2fs_balloc`, `ext2fs_gop_alloc`.
  - Mapping: `ext2fs_bmap`.
  - Inode lifecycle: size/block count helpers, update, truncate, inactive.
  - Lookup/directory operations.
  - Subroutines and time updates.
  - VFS operations.
  - Read/write operations.
  - Vnode operations.
  - HTree hash/index operations.
- `IS_EXT2_VNODE` tag check.
- External vnode operation vectors.

Dependencies:
- Assumes UFS/VFS kernel context where `VFS_PROTOS`, `IN_*` flags, and vnode operation declarations exist.

Design notes:
- This header ties the ext2fs implementation files together and exposes the filesystem’s VFS/VOP surface to the rest of the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_hash.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_hash.c

This file implements directory-name hashing for ext3/ext4 HTree indexed directories.

Key public function:
- `ext2fs_htree_hash`: computes major/minor hash values for a name using the requested HTree hash version.

Supported hash algorithms:
- Legacy signed/unsigned hash.
- Half-MD4 signed/unsigned hash.
- TEA signed/unsigned hash.

Key internal helpers:
- `ext2fs_prep_hashbuf`: prepares padded 32-bit word buffers from file names.
- `ext2fs_legacy_hash`: Linux-compatible legacy directory hash.
- `ext2fs_half_md4`: modified half-MD4 transform.
- `ext2fs_tea`: Tiny Encryption Algorithm based hash transform.

Important behavior:
- Name length must be 1..255.
- Major hash has its low collision bit cleared.
- `EXT2_HTREE_EOF << 1` is avoided by reducing to the previous value.
- Optional hash seed overrides the default MD4 initialization constants.

Dependencies:
- `ext2fs_htree.h` for hash version constants.
- `ext2fs_hash.h` for MD4 primitive macros.
- Kernel string/mount/vnode includes.

Design notes:
- Compatibility with Linux HTree hashing is the main concern; changes here directly affect indexed directory lookup interoperability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_hash.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_hash.h

This small header defines primitive macros used by the HTree half-MD4 hash implementation.

Definitions:
- `F`, `G`, `H`: MD4 Boolean functions.
- `ROTATE_LEFT`: 32-bit left rotation macro.

Dependencies:
- Assumes 32-bit arithmetic operands.

Design notes:
- Used by `ext2fs_hash.c` only for MD4-style hash transformations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_htree.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_htree.c

This file implements ext3/ext4 HTree indexed directory lookup and insertion support.

Key public functions:
- `ext2fs_htree_has_idx`: checks whether a directory has HTree indexing enabled.
- `ext2fs_htree_lookup`: looks up a name through the HTree and scans candidate leaf directory blocks.
- `ext2fs_htree_create_index`: converts a full single-block directory into an indexed directory.
- `ext2fs_htree_add_entry`: adds a directory entry through an existing HTree, splitting leaf and index blocks as needed.

Key internal helpers:
- Accessors/mutators for HTree entry hash, block, count, and limit.
- `ext2fs_htree_find_leaf`: traverses root and optional second-level index to find the leaf block for a hash.
- `ext2fs_htree_check_next`: handles hash collisions by advancing to adjacent leaves.
- `ext2fs_htree_split_dirblock`: sorts directory entries by hash, moves roughly half to a new block, computes split hash, and inserts the new entry.
- `ext2fs_htree_insert_entry*`: inserts index entries.
- `ext2fs_htree_append_block`: appends a full directory block through `VOP_WRITE`.
- `ext2fs_htree_writebuf` and `ext2fs_htree_release`: write or release traversal buffers.

Important behavior:
- Only up to one indirect HTree level is supported; deeper indexes return errors.
- Root initialization preserves `.` and `..`, sets `EXT2_INDEX`, initializes root info, and creates entries for blocks 1 and 2.
- If a target index node is full, insertion may split the index node or create a second HTree level.
- If the root index is full at two levels, insertion fails with `EIO`.
- Lookup falls back to scanning next leaves when the collision bit or equal hash indicates possible matches beyond the first target block.

Dependencies:
- Directory layout from `ext2fs_dir.h`.
- Hashing from `ext2fs_hash.c`.
- Vnode/buffer APIs, `ext2fs_blkatoff`, `ext2fs_search_dirblock`, `ext2fs_add_entry`.
- Kernel heap sort and temporary malloc.

Notable implementation risks:
- Directory split/append operations update several blocks and index buffers without journaling; crash consistency is classic ext2-style.
- The code assumes valid directory record lengths while walking blocks.
- Multi-level index support is intentionally limited.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_htree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_htree.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_htree.h

This header defines ext3 HTree directory-index constants and structures.

Key definitions:
- Hash version constants: legacy, half-MD4, TEA, and unsigned variants.
- `EXT2_HTREE_EOF`
- `struct ext2fs_fake_direct`: fake directory entry header used in HTree nodes.
- `struct ext2fs_htree_count`: count/limit overlay for the first entry slot.
- `struct ext2fs_htree_entry`: hash-to-block index entry.
- `struct ext2fs_htree_root_info`: root metadata including hash version, info length, and index levels.
- `struct ext2fs_htree_root`: directory block 0 format containing fake `.`/`..`, root info, and entries.
- `struct ext2fs_htree_node`: non-root index node format.
- `struct ext2fs_htree_lookup_level` and `struct ext2fs_htree_lookup_info`: traversal state for up to two levels.
- `struct ext2fs_htree_sort_entry`: temporary descriptor used when splitting directory blocks.

Dependencies:
- Uses fixed-width integer types and `struct buf`.

Design notes:
- The fixed `h_levels[2]` traversal state matches the implementation’s maximum supported HTree depth.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_htree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_inode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_inode.c

This file implements ext2fs inode size/block-count helpers, inactive handling, inode disk updates, and truncation/freeing of direct and indirect blocks.

Key public functions:
- `ext2fs_size`: returns inode size, combining high size bits for regular files.
- `ext2fs_setsize`: updates inode size and enables `LARGEFILE` feature when needed.
- `ext2fs_nblock`: returns block count, handling ext4 huge-file encoding.
- `ext2fs_setnblock`: stores block count, using huge-file encoding when needed and supported.
- `ext2fs_inactive`: handles last vnode reference, truncating unlinked files and marking deletion time.
- `ext2fs_update`: writes the in-memory inode to its on-disk inode table slot.
- `ext2fs_truncate`: grows or shrinks files and frees blocks beyond EOF.

Key internal function:
- `ext2fs_indirtrunc`: recursively frees blocks referenced by single, double, or triple indirect blocks.

Important behavior:
- Character/block devices, FIFOs, and sockets ignore truncation.
- Short symlinks stored in the inode block array are cleared directly when truncated to zero.
- File growth allocates the last byte through `ufs_balloc_range` and updates UVM vnode size.
- File shrink zeroes the post-EOF region in a partial final block, updates inode size before freeing, writes pointer removals before block frees, truncates buffers, then frees indirect and direct blocks.
- Crash safety follows traditional UFS/ext2 ordering: remove pointers from inode/indirect blocks before returning blocks to the free bitmap.
- `ext2fs_indirtrunc` reads indirect blocks using known disk block numbers because bmap may no longer resolve metadata after pointers are cleared.

Dependencies:
- UFS inode and mount structures.
- Ext2fs allocation/freeing and update helpers.
- NetBSD buffer cache, UVM vnode sizing, and vnode lifecycle APIs.

Notable implementation risks:
- Triple indirect support is explicitly noted as untested.
- Truncation logic depends on careful temporary restoration of old block pointers while freeing blocks.
- Extent-backed inode truncation is not separately handled in this file; this is classic block-pointer truncation logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_inode.c -->