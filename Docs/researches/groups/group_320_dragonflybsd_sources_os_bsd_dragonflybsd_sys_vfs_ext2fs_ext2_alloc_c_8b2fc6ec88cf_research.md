# Group Research: group_320_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_ext2fs_ext2_alloc_c_8b2fc6ec88cf

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/dragonflybsd`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_alloc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_alloc.c

This file implements ext2 block and inode allocation/freeing for DragonFlyBSD, including group selection, bitmap updates, cluster accounting, lazy bitmap/table initialization, group descriptor counters, and sparse-superblock metadata layout helpers.

Key responsibilities:
- Allocate data blocks and metadata blocks with preferred-block and cylinder-group fallback policy.
- Allocate inodes, choose directory-preferred groups, initialize new vnode/inode state, and seed generation/birth time.
- Reallocate buffered clusters into contiguous disk ranges when `doreallocblks` is enabled.
- Maintain free block/inode counters in the superblock and group descriptors, including 64-bit descriptor fields.
- Initialize uninitialized ext4-style block/inode bitmaps and zero unused inode-table blocks.
- Verify/set block and inode bitmap checksums through `ext2_csum.c`.
- Free blocks and inodes, update directory counts, and maintain cluster summaries.

Important functions:
- `ext2_alloc`: Main block allocator. Checks reserved block limits, chooses a starting group, calls `ext2_hashalloc`, updates sequential allocation hints and `i_blocks`.
- `ext2_alloc_meta`: Allocates an extended-attribute metadata block near the inode.
- `ext2_reallocblks`: Attempts cluster relocation for contiguous allocation; rewrites inode/indirect block pointers, then frees old blocks.
- `ext2_valloc`: Allocates an inode from a preferred group, creates/initializes a vnode, initializes extent trees when enabled, and returns the locked vnode.
- `e2fs_gd_get_*` / `e2fs_gd_set_*`: Access low/high group descriptor fields for bitmaps, inode tables, free counters, directory counts, and unused inodes.
- `ext2_dirpref`: Chooses a directory inode group using average free inodes/blocks, directory density, root-directory spreading, and `e2fs_contigdirs`.
- `ext2_blkpref`: Computes preferred physical block from sequential hints, earlier block map entries, or inode group locality.
- `ext2_hashalloc`: Implements preferred group, quadratic rehash, then brute-force group search.
- `ext2_cg_number_gdb` and helpers: Count group descriptor backup blocks for normal, sparse, sparse-super2, and meta_bg layouts.
- `ext2_alloccg`: Reads and validates a block bitmap, initializes/checksums it when needed, allocates a preferred block or free run, and updates counters.
- `ext2_clusteralloc`: Allocates a contiguous run using cluster summary hints.
- `ext2_nodealloccg`: Reads and verifies an inode bitmap, handles uninitialized inode bitmaps/tables, allocates an inode, and updates counters/checksums.
- `ext2_blkfree` / `ext2_vfree`: Free a block or inode and update bitmaps, counters, checksums, and directory totals.
- `ext2_cg_has_sb`: Implements ext backup-superblock group selection.

Important interactions:
- Relies on `ext2_csum.c` for bitmap checksum verification and updates.
- Uses `ext2_alloc_vnode`, `ext2_vinit`, and `ext4_ext_tree_init` when allocating new inodes.
- Called by `ext2_balloc.c`, truncation paths in `ext2_inode.c`, and directory/vnode creation code.
- Requires the ext2 mount mutex for shared superblock/group accounting but drops it around blocking bitmap I/O.

Notable behavior and risks:
- `ext2_alloc` unlocks the mount mutex on ENOSPC paths, matching callers that enter with the lock held.
- New block numbers above `UINT_MAX` are rejected by indirect-block callers, since classic block maps are 32-bit.
- Lazy bitmap and inode-table initialization is tied to checksum-capable features.
- `ext2_clusteralloc` updates one bitmap bit per `e2fs_fpb`, which reflects the inherited fragment/block accounting assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_balloc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_balloc.c

This file allocates physical storage for logical file blocks in non-extent ext2 files. It handles direct blocks, indirect blocks, synchronous initialization of new indirect blocks, and buffer-cache return semantics.

Key responsibilities:
- Allocate or fetch a buffer for a requested logical block.
- Maintain sequential allocation hints used by `ext2_blkpref`.
- Populate direct block pointers in `i_db`.
- Allocate single/double/triple indirect metadata blocks as needed.
- Ensure newly allocated indirect blocks are zeroed and written before being referenced.
- Return existing or newly allocated data buffers, optionally cleared/read according to `BA_CLRBUF`.

Important functions:
- `ext2_balloc`: Main allocator. Rejects negative LBNs, updates sequential hints, dispatches extents to `ext2_ext_balloc`, handles direct block allocation, walks indirect paths from `ext2_getlbns`, allocates missing metadata/data blocks, and writes parent pointer blocks.
- `ext2_ext_balloc`: Stub for extent-backed allocation; currently returns `EINVAL`.

Important interactions:
- Calls `ext2_alloc`, `ext2_blkpref`, `ext2_blkfree`, and `ext2_getlbns`.
- Uses DragonFly buffer-cache calls such as `bread`, `getblk`, `bwrite`, `bdwrite`, and `cluster_read`.
- Works with `BA_CLRBUF`, `BA_SEQMASK`, and `IO_SYNC` flags declared in `ext2_extern.h`.

Notable behavior and risks:
- Extent-mode allocation is not implemented in this file; files with `IN_E4EXTENTS` fail allocation with `EINVAL`.
- If a newly allocated indirect block cannot be written, it is immediately freed to avoid persistent pointers to garbage.
- Direct and indirect block maps cannot store physical blocks above `UINT_MAX`; such allocations return `EFBIG`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_bmap.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_bmap.c

This file maps logical file offsets/blocks to physical device offsets for DragonFlyBSD ext2. The implemented path is the classic ext2 direct/indirect pointer tree; the ext4 extent bmap entry point is present but stubbed.

Key responsibilities:
- Implement VOP bmap conversion from logical file offset to disk byte offset.
- Return forward and backward contiguous run sizes in bytes.
- Traverse direct and indirect block pointer arrays.
- Compute indirect-block logical block paths for allocation and mapping callers.
- Read indirect blocks through vnode buffers with explicit disk offsets.

Important functions:
- `ext2_bmap`: VOP wrapper. Converts `a_loffset` to LBN, dispatches to extent or indirect mapping, converts disk blocks to byte offsets, and scales run counts to bytes.
- `ext4_bmapext`: Extent bmap placeholder; currently returns `EINVAL`.
- `readindir`: Reads an indirect block through `getblk` and strategy I/O when not cached.
- `ext2_bmaparray`: Traverses direct and indirect pointers, returns `-1` for holes, and computes sequential run lengths using `is_sequential`.
- `ext2_getlbns`: Builds the path of indirect logical blocks and offsets required to reach a data block or metadata block.

Important interactions:
- Used by buffer-cache and allocation code, especially `ext2_balloc` and truncation.
- Uses mount geometry from `ext2_mount.h` (`MNINDIR`, `blkptrtodb`, `is_sequential`).
- Reads block pointers as little-endian on-disk `e2fs_daddr_t` values.

Notable behavior and risks:
- Extent-backed bmap is not implemented, so `IN_E4EXTENTS` files return `EINVAL` here.
- `ext2_getlbns` uses 64-bit intermediate arithmetic to avoid overflow when computing triple-indirect ranges.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_csum.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_csum.c

This file implements checksum support for ext2/ext3/ext4 metadata structures used by the DragonFlyBSD ext2 driver: superblocks, directory blocks, htree nodes, extent blocks, group bitmaps, inodes, and group descriptors.

Key responsibilities:
- Establish the CRC32C seed from `csum_seed` or filesystem UUID.
- Verify and set superblock checksums.
- Detect and initialize directory checksum tails.
- Verify/set directory entry block and htree index checksums.
- Verify/set extent block checksums.
- Verify/set block and inode bitmap checksums stored in group descriptors.
- Verify/set inode checksums, including high checksum words when supported by `extra_isize`.
- Verify/set group descriptor checksums using CRC32C for metadata checksums or CRC16 for older `GDT_CSUM`.

Important functions:
- `ext2_sb_csum_set_seed`, `ext2_sb_csum_verify`, `ext2_sb_csum_set`: Superblock checksum seed and checksum maintenance.
- `ext2_init_dirent_tail`, `ext2_is_dirent_tail`, `ext2_dirent_get_tail`: Directory checksum tail helpers.
- `ext2_dirent_csum_verify` / `ext2_dirent_csum_set`: Directory block checksum handling using inode number and generation.
- `ext2_dx_csum_verify` / `ext2_dx_csum_set`: HTree root/node checksum handling.
- `ext2_dir_blk_csum_verify`: Dispatches a directory buffer to dirent-tail or htree checksum verification.
- `ext2_extent_blk_csum_verify` / `ext2_extent_blk_csum_set`: Extent block checksum handling.
- `ext2_gd_i_bitmap_csum_*` and `ext2_gd_b_bitmap_csum_*`: Bitmap checksum verification and update.
- `ext2_ei_csum_verify` / `ext2_ei_csum_set`: Inode checksum verification/update, with zeroed new inodes accepted.
- `ext2_gd_csum_verify` / `ext2_gd_csum_set`: Group descriptor checksum handling.

Important interactions:
- Called by allocation/free paths before and after bitmap modification.
- Called by `ext2_blkatoff`, lookup, and htree write paths for directory block validation/update.
- Called by inode conversion/update paths to validate and write dinode checksums.

Notable behavior and risks:
- Metadata checksums are silently bypassed when the feature bit is absent.
- Directory block verification treats either a dirent tail or an htree count structure as the checksum-bearing format.
- Superblock checksum verification rejects unsupported checksum types.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_csum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_dinode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_dinode.h

This header defines the ext2/ext3/ext4 on-disk inode layout and inode-related constants used by the DragonFlyBSD ext2 implementation.

Key responsibilities:
- Declare special inode numbers, including root, journal, resize, and first normal inode.
- Define ext2/ext3/ext4 inode flags mapped to DragonFly inode flags or internal state.
- Define timestamp extra-field bit layout for epoch and nanosecond storage.
- Define direct/indirect block pointer counts and maximum inline symlink length.
- Declare `struct ext2fs_dinode`, the little-endian on-disk inode format.

Important definitions:
- `EXT2_ROOTINO`, `EXT2_FIRSTINO`, and other reserved inode numbers.
- `EXT2_APPEND`, `EXT2_IMMUTABLE`, `EXT2_NODUMP`, `EXT3_INDEX`, `EXT4_EXTENTS`, `EXT4_HUGE_FILE`, and related flags.
- `E2DI_HAS_XTIME` and `E2DI_HAS_HUGE_FILE`: Feature-gated checks for extended timestamps and large block counts.
- `EXT2_NDIR_BLOCKS`, `EXT2_IND_BLOCK`, `EXT2_DIND_BLOCK`, `EXT2_TIND_BLOCK`, `EXT2_N_BLOCKS`, `EXT2_MAXSYMLINKLEN`.
- `struct ext2fs_dinode`: Mode, ownership, size, timestamps, deletion time, link count, block count, flags, block pointers/extents, generation, EA block, high UID/GID, checksum, extra timestamp, birth time, and project ID fields.

Important interactions:
- Used by inode conversion in `ext2_inode_cnv.c`, inode checksum code in `ext2_csum.c`, allocation and truncation code, and symlink handling elsewhere in ext2fs.

Notable behavior:
- The block array is reused as extent tree storage when `EXT4_EXTENTS` is set.
- Only selected ext4-era fields are represented; support depends on feature checks in mount and conversion code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_dir.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_dir.h

This header defines ext2 on-disk directory entry formats, directory insertion slot tracking, directory checksum tails, file type constants, and record-length alignment helpers.

Key responsibilities:
- Provide old and new ext2 directory entry structures.
- Represent lookup-discovered insertion slots with `struct ext2fs_searchslot`.
- Define metadata-checksum directory tail format.
- Define ext2 directory file type values and maximum link count.
- Provide record length rounding via `EXT2_DIR_REC_LEN`.

Important definitions:
- `struct ext2fs_direct`: Original entry format with 16-bit name length.
- `struct ext2fs_direct_2`: Newer format splitting name length and file type bytes.
- `enum slotstatus` and `struct ext2fs_searchslot`: Tracks whether lookup found no slot, a compactable range, or a directly usable range.
- `struct ext2fs_direct_tail`, `EXT2_FT_DIR_CSUM`, and `EXT2_DIRENT_TAIL`: Directory checksum tail support.
- `EXT2_FT_*`: On-disk file type values.
- `EXT2_DIR_PAD`, `EXT2_DIR_ROUND`, `EXT2_DIR_REC_LEN`: Four-byte directory entry alignment.

Important interactions:
- Used heavily by `ext2_lookup.c`, `ext2_htree.c`, and `ext2_csum.c`.
- File type values are translated to/from DragonFly `dirent` types in lookup/readdir code.

Notable behavior:
- Directory checksum tails masquerade as unused directory entries with a reserved file type.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extents.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extents.c

This file is a mostly stubbed ext4 extent implementation. It declares the expected extent helpers and trace provider, but the functional extent operations either return neutral values, `NULL`, cache miss, or `EINVAL`.

Key responsibilities:
- Provide symbols expected by the rest of the ext2fs code when ext4 extent feature bits are present.
- Define optional debug print hooks under `EXT2FS_PRINT_EXTENTS`.
- Stub tree initialization, lookup, cache, allocation, and truncate operations.

Important functions:
- `ext4_ext_tree_init`: No-op placeholder called for new regular files/directories when extents are supported.
- `ext4_ext_in_cache`: Always reports `EXT4_EXT_CACHE_NO`.
- `ext4_ext_find_extent`: Returns `EINVAL`.
- `ext4_ext_get_blocks`: Returns `EINVAL`.
- `ext4_ext_remove_space`: Returns `EINVAL`.
- Inline helpers such as `ext4_ext_inode_header`, `ext4_ext_block_header`, `ext4_ext_index_pblock`, and `ext4_ext_extent_pblock`: Return `NULL` or zero.

Important interactions:
- Called from `ext2_valloc`, `ext2_balloc`, `ext2_bmap`, and `ext2_truncate` when `IN_E4EXTENTS` is set.
- The checksum file supports extent block checksums even though this implementation does not manipulate extent trees.

Notable behavior and risks:
- Extent-backed files cannot be allocated, mapped, or truncated successfully through these stubs.
- The presence of `IN_E4EXTENTS` changes dispatch behavior elsewhere, so this file defines a clear unsupported path rather than falling back to indirect blocks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extents.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extents.h

This header defines ext4 extent on-disk structures, extent tree constants, cache state constants, path descriptors, and prototypes used by the DragonFlyBSD ext2 extent stubs/checksum code.

Key responsibilities:
- Define extent magic, maximum block/length/depth constants, and cache result states.
- Declare on-disk extent, index, header, and checksum tail structures.
- Provide macros for locating first/last/max extent or index entries and extent checksum tail position.
- Declare extent tree API prototypes used by allocation, bmap, truncate, and debug code.

Important definitions:
- `EXT4_EXT_MAGIC`, `EXT4_MAX_BLOCKS`, `EXT4_MAX_LEN`, `EXT4_EXT_DEPTH_MAX`.
- `EXT4_EXT_CACHE_NO`, `EXT4_EXT_CACHE_GAP`, `EXT4_EXT_CACHE_IN`.
- `struct ext4_extent_tail`, `struct ext4_extent`, `struct ext4_extent_index`, `struct ext4_extent_header`.
- `struct ext4_extent_cache` and `struct ext4_extent_path`.
- `EXT_FIRST_EXTENT`, `EXT_FIRST_INDEX`, `EXT_LAST_EXTENT`, `EXT_LAST_INDEX`, `EXT4_EXTENT_TAIL_OFFSET`, `EXT_HAS_FREE_INDEX`, `EXT_MAX_EXTENT`, `EXT_MAX_INDEX`.

Important interactions:
- Included by `ext2_extents.c`, `ext2_csum.c`, `ext2_subr.c`, and inode conversion/debug paths.

Notable behavior:
- The data structures are complete enough for checksum and flag representation, but `ext2_extents.c` does not implement real extent operations in this tree.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extents.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extern.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extern.h

This header declares the cross-file ext2fs API for allocation, mapping, directory operations, inode conversion, htree handling, checksum maintenance, inode hash management, and vnode operations.

Key responsibilities:
- Provide prototypes for ext2 block/inode allocation, freeing, mapping, truncation, and updates.
- Declare directory lookup, readdir, insertion, deletion, rewrite, emptiness, and ancestry checks.
- Declare htree lookup/add/create/hash helpers.
- Declare checksum functions for superblocks, directory blocks, htree nodes, extents, bitmaps, inodes, and group descriptors.
- Declare inode hash functions and vnode allocation.
- Define low-level allocation flags.
- Export vnode operation tables.

Important definitions:
- `BA_CLRBUF`: Caller will not overwrite the full block; newly allocated buffers must be cleared and existing buffers read.
- `BA_SEQMASK`, `BA_SEQSHIFT`, `BA_SEQMAX`: Sequential-read/allocation hint encoding.
- Extern vnode op tables: `ext2_vnodeops`, `ext2_specops`, `ext2_fifoops`.

Important interactions:
- This is the main internal contract among `ext2_alloc.c`, `ext2_balloc.c`, `ext2_bmap.c`, `ext2_csum.c`, `ext2_htree.c`, `ext2_inode.c`, `ext2_inode_cnv.c`, `ext2_lookup.c`, and `ext2_subr.c`.

Notable behavior:
- The header exposes both implemented and stubbed extent entry points, so callers must rely on runtime errors for unsupported extent operations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_hash.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_hash.c

This file implements ext2 htree directory name hashing compatible with Linux indexed directories. It supports legacy, TEA, and half-MD4 hash algorithms, including signed and unsigned character variants.

Key responsibilities:
- Implement the half-MD4 transform used by ext directory indexes.
- Implement TEA-based hashing.
- Implement legacy ext2 directory hash.
- Prepare padded hash input buffers using signed or unsigned character interpretation.
- Normalize and return major/minor htree hash values.

Important functions:
- `ext2_half_md4`: MD4-derived transform over 8-word data blocks.
- `ext2_tea`: TEA-style transform for directory hashing.
- `ext2_legacy_hash`: Older ext2 hash algorithm.
- `ext2_prep_hashbuf`: Packs filename bytes into 32-bit words with length-derived padding.
- `ext2_htree_hash`: Public dispatcher. Validates name length, applies optional hash seed, selects algorithm/version, clears the low collision bit in the major hash, avoids EOF sentinel collision, and returns major/minor hashes.

Important interactions:
- Used by `ext2_htree.c` for htree lookup, directory block splitting, and index creation.
- Hash version constants and structures come from `htree.h`.

Notable behavior:
- Invalid names or unknown hash versions return `-1` and zero output hashes.
- The major hash low bit is reserved for collision handling and is cleared before return.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_htree.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_htree.c

This file implements ext2 htree indexed-directory lookup and contains code for htree index creation and insertion/splitting. In this DragonFlyBSD source, the normal `ext2_direnter` path has htree insertion/index creation compiled out because of a documented lost-dirent issue, but existing indexes can still be used for lookup.

Key responsibilities:
- Detect indexed directories.
- Traverse htree root and optional second-level nodes to find candidate leaf blocks.
- Search candidate leaf directory blocks, including collision continuation.
- Create a new htree index from a one-block linear directory.
- Split full directory data blocks by name hash and insert new index entries.
- Split index nodes and create a second level when needed.
- Maintain directory and htree checksums.

Important functions:
- `ext2_htree_has_idx`: Checks directory hash-index feature plus inode `IN_E3INDEX`.
- `ext2_htree_find_leaf`: Reads root block, validates hash version and limits, computes name hash, binary-searches htree entries, and records traversal path.
- `ext2_htree_lookup`: Finds candidate leaf blocks and calls `ext2_search_dirblock`; follows collision chains with `ext2_htree_check_next`.
- `ext2_htree_append_block`: Appends a full directory block through `VOP_WRITE`.
- `ext2_htree_writebuf`: Writes all index buffers after setting htree checksums.
- `ext2_htree_split_dirblock`: Sorts entries by hash, moves roughly half to a new block, chooses split hash, handles collision bit, appends the new entry, and initializes dirent tails.
- `ext2_htree_create_index`: Rewrites block 0 as an htree root and appends two data blocks.
- `ext2_htree_add_entry`: Splits target leaf blocks and, if needed, index nodes.

Important interactions:
- Uses `ext2_htree_hash`, `ext2_blkatoff`, `ext2_search_dirblock`, `ext2_dirent_csum_set`, and `ext2_dx_csum_set`.
- Lookup is called from `ext2_lookup.c`.

Notable behavior and risks:
- HTree mutation code exists but is disabled in `ext2_direnter` with an explicit comment documenting reproducible lost entries.
- `ext2_htree_add_entry` falls back to linear `ext2_add_entry` when `ip->i_count != 0`, meaning lookup slot accounting can bypass splitting.
- Only up to one level of indirection is accepted by `ext2_htree_find_leaf`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_htree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_ihash.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_ihash.c

This file implements the in-core ext2 inode hash table keyed by device and inode number. It is adapted from UFS inode hashing and uses a DragonFly LWKT token for serialization.

Key responsibilities:
- Allocate and free the global inode hash table.
- Look up active inodes and safely acquire their vnodes.
- Insert newly loaded/allocated inodes.
- Remove reclaimed inodes from the hash.

Important functions:
- `ext2_ihashinit`: Allocates a zeroed hash table sized by `vfs_inodehashsize` and initializes `ext2_ihash_token`.
- `ext2_ihashuninit`: Frees the hash table under the token.
- `ext2_ihashget`: Searches by `cdev_t` and inode number, uses `vget` to lock the vnode, and revalidates after blocking.
- `ext2_ihashins`: Inserts an inode if no matching `(dev, ino)` exists; sets `IN_HASHED`.
- `ext2_ihashrem`: Removes a hashed inode and clears `IN_HASHED`.

Important interactions:
- Used by vnode allocation/loading and reclaim paths (`ext2_valloc`, `ext2_reclaim`, and mount/vnode code outside this group).

Notable behavior:
- The hash macro uses `minor(device) + inum`.
- `ext2_ihashget` loops to handle races where an inode is reclaimed or replaced while `vget` blocks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_ihash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_inode.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_inode.c

This file implements inode metadata update, indirect-block truncation, top-level truncation, inactive cleanup, and reclaim for DragonFlyBSD ext2.

Key responsibilities:
- Flush dirty inode timestamps/metadata to disk.
- Grow or shrink classic direct/indirect block files.
- Recursively free single/double/triple indirect block trees.
- Zero partial blocks when shrinking.
- Release blocks and free inodes when link count reaches zero.
- Remove reclaimed inodes from the inode hash and free memory.

Important functions:
- `ext2_update`: Applies pending times via `ext2_itimes`, reads the inode table block, converts inode to on-disk form with `ext2_i2ei`, and writes or delays the buffer.
- `ext2_indirtrunc`: Recursively zeros and frees indirect block pointers in LIFO order.
- `ext2_ind_truncate`: Handles file extension through `ext2_balloc`, shrink-to-length, inode pointer updates-before-free, buffer truncation, direct/indirect freeing, and `i_blocks` accounting.
- `ext2_ext_truncate`: Extent truncate placeholder; returns `EINVAL`.
- `ext2_truncate`: Dispatches short symlinks, no-op size updates, extent truncate, or indirect truncate.
- `ext2_inactive`: On last inactive reference, truncates and frees unlinked writable inodes; writes pending times.
- `ext2_reclaim`: Flushes lazy modifications, removes inode from ihash, releases device vnode, and frees the inode.

Important interactions:
- Calls `ext2_balloc`, `ext2_blkfree`, `ext2_vfree`, `ext2_i2ei`, `ext2_itimes`, and `ext2_ihashrem`.
- Uses VM vnode pager sizing and buffer truncation to keep cache state coherent.

Notable behavior and risks:
- Extent-backed truncation is unsupported and returns `EINVAL`.
- Truncation writes the shortened inode before freeing blocks to prefer leak-over-corruption crash behavior.
- Triple indirect truncation is marked as untested in a comment.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_inode_cnv.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_inode_cnv.c

This file converts between little-endian on-disk ext2 dinodes and DragonFlyBSD in-core `struct inode` fields, including extended timestamps, high UID/GID, huge-file block counts, flags, extents, and inode checksums.

Key responsibilities:
- Validate inode numbers, root inode type/link count, and extended inode size.
- Decode on-disk mode, link count, size, timestamps, flags, block counts, generation, ownership, EA block, and block pointers.
- Encode in-core inode state back to on-disk little-endian dinode fields.
- Translate ext2 append/immutable/nodump/index/extents flags to internal flags and back.
- Verify and set inode checksums.

Important functions:
- `ext2_decode_extra_time`: Adds high epoch bits and extracts nanoseconds from ext3 extra timestamp fields.
- `ext2_ei2i`: Converts disk inode to memory inode and calls `ext2_ei_csum_verify`.
- `ext2_encode_extra_time`: Packs epoch/nanosecond data for extra timestamp fields.
- `ext2_i2ei`: Converts memory inode to disk inode and calls `ext2_ei_csum_set`.
- `ext2_print_inode`: Optional debug printer under `EXT2FS_PRINT_EXTENTS`.

Important interactions:
- Called by inode loading code outside this group and by `ext2_update`.
- Uses definitions from `ext2_dinode.h` and checksum helpers from `ext2_csum.c`.

Notable behavior and risks:
- If link count is zero, `i_mode` is set to zero to mark the inode unused.
- Regular file size uses `e2di_size_high`; non-regular files do not.
- Huge-file accounting may convert block counts between filesystem blocks and disk blocks depending on `EXT4_HUGE_FILE`.
- The write path sets `e2di_dtime` based on link count and mtime.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_inode_cnv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_lookup.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_lookup.c

This file implements directory reading, pathname lookup, directory block scanning, directory entry insertion/removal/rewrite, empty-directory checks, and rename ancestry checks for DragonFlyBSD ext2.

Key responsibilities:
- Convert ext2 directory entries to DragonFly `dirent` records for `readdir`.
- Resolve pathname components through htree lookup or linear directory scans.
- Track insertion/removal offsets in directory inode fields (`i_offset`, `i_count`, `i_endoff`, `i_diroff`).
- Validate directory entries and report/panic on corruption depending on mount writability.
- Insert new entries into fresh blocks or compacted free slots.
- Remove and rewrite directory entries.
- Check directory emptiness and prevent invalid directory rename ancestry.

Important functions:
- `ext2_readdir`: Iterates directory blocks, validates record progress, converts inode/type/name fields, emits cookies, and updates EOF state.
- `ext2_lookup` / `ext2_lookup_ino`: Main lookup implementation with create/rename/delete slot accounting, htree fallback, lock handling, sticky-directory checks, and parent handling.
- `ext2_search_dirblock`: Scans one directory block, validates entries, finds name matches, and accumulates free/compactable slots.
- `ext2_dirbad` / `ext2_check_direntry`: Directory corruption reporting and validation.
- `ext2_add_first_entry`: Writes an entry into a fresh directory block, including checksum tail support.
- `ext2_direnter`: Builds the new ext2 directory entry and inserts it.
- `ext2_add_entry`: Compacts an existing slot range, inserts the new entry, updates checksum, and writes the block.
- `ext2_dirremove`: Removes an entry by zeroing first entry or merging with previous record.
- `ext2_dirrewrite`: Repoints an existing entry and updates file type.
- `ext2_dirempty`: Accepts only `.` and matching `..`.
- `ext2_checkpath`: Walks `..` to prevent moving a directory into its descendant.

Important interactions:
- Uses `ext2_blkatoff`, `ext2_htree_lookup`, `ext2_truncate`, and directory checksum helpers.
- Directory entry file types are translated using local `FTTODT` and `DTTOFT` tables.

Notable behavior and risks:
- HTree lookup is active, but HTree insertion/index creation in `ext2_direnter` is inside `#if 0` because of documented lost dirents.
- On writable mounts, `ext2_dirbad` panics for corrupted directories; read-only mounts emit an SDT probe.
- Metadata checksum tails are treated as unavailable space during slot accounting.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_mount.h

This header defines DragonFlyBSD ext2 mount arguments, the in-memory ext2 mount wrapper, locking macros, mount conversion macros, and geometry helpers used by mapping/allocation code.

Key responsibilities:
- Declare `struct ext2_args` for mount input.
- Declare `struct ext2mount`, which ties VFS mount state to device vnode, ext2 superblock state, buffer object, geom consumer, lock, and export data.
- Provide mount lock/unlock/assert access macros.
- Convert `struct mount` to `struct ext2mount`.
- Provide indirect-block geometry helpers for bmap.

Important definitions:
- `struct ext2_args`: Device path and export arguments.
- `struct ext2mount`: `um_mountp`, `um_dev`, `um_devvp`, `um_e2fs`, `um_nindir`, `um_bptrtodb`, `um_seqinc`, `um_lock`, `um_cp`, `um_bo`, and `um_export`.
- `EXT2_LOCK`, `EXT2_UNLOCK`, `EXT2_MTX`.
- `VFSTOEXT2`.
- `MNINDIR`, `blkptrtodb`, `is_sequential`.

Important interactions:
- Included by nearly every ext2fs implementation file.
- The mount lock protects shared filesystem/group accounting in allocation and related code.

Notable behavior:
- This is kernel-only under `_KERNEL`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_subr.c

This support file provides a guarded free wrapper, a block-at-offset directory/data helper, and cluster summary accounting used by allocation and reallocation.

Key responsibilities:
- Warn on attempts to free a null pointer through ext2 helper code.
- Read the filesystem block containing a file/directory offset and optionally return an in-buffer pointer.
- Verify directory block checksums after reading through `ext2_blkatoff`.
- Maintain per-cylinder-group cluster summary state for contiguous allocation.

Important functions:
- `ext2_free`: Prints the caller function name if asked to free `NULL`, otherwise calls `kfree`.
- `ext2_blkatoff`: Computes LBN and block size, reads the block with `bread`, verifies directory block checksum, returns optional offset pointer and buffer.
- `ext2_clusteracct`: Initializes and updates `e2fs_clustersum` and `e2fs_maxcluster` when blocks are allocated or freed.

Important interactions:
- `ext2_blkatoff` is used by lookup, htree, directory mutation, and other offset-based readers.
- `ext2_clusteracct` is called by `ext2_alloccg`, `ext2_clusteralloc`, and `ext2_blkfree`.

Notable behavior:
- `ext2_blkatoff` always invokes directory block checksum verification; checksum code returns success immediately when metadata checksums are not enabled.
- Cluster accounting lazily initializes summaries by scanning the bitmap on first use for a group.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_subr.c -->