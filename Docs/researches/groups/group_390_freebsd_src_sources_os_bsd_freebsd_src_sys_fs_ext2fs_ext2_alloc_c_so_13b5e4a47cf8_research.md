# Group Research: group_390_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_ext2fs_ext2_alloc_c_so_13b5e4a47cf8

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_alloc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_alloc.c

This file implements FreeBSD ext2/ext3/ext4 block and inode allocation, freeing, group accounting, allocation preferences, lazy bitmap/table initialization, and backup-superblock placement logic.

Key responsibilities:
- Allocate file data blocks and external metadata blocks with preferred-block, quadratic rehash, and brute-force group fallback.
- Reallocate clustered indirect-map blocks into contiguous physical ranges when `vfs.ext2fs.doreallocblks` is enabled.
- Allocate vnodes/inodes, pick directory-preferred groups, initialize generation/birth time, and initialize ext4 extent roots when needed.
- Maintain superblock and group descriptor free block/inode/directory counters, including 64-bit group descriptor high fields.
- Validate, initialize, checksum, and update block/inode bitmaps.
- Free blocks and inodes, update cluster summaries, and maintain directory totals.
- Calculate sparse-superblock/meta_bg group descriptor backup block counts.

Important functions:
- `ext2_alloc`: Main block allocator; enforces reserved block policy, calls `ext2_hashalloc`, updates sequential allocation hints and `i_blocks`.
- `ext2_alloc_meta`: Allocates external metadata blocks, used by xattrs and extent index blocks.
- `ext2_reallocblks`: Moves a cluster of logical blocks to a contiguous allocation and rewrites direct/indirect pointers.
- `ext2_valloc`: Allocates an inode and new vnode, initializes extents or block pointers, and inserts into the vnode hash.
- `e2fs_gd_get_*` / setters: Read and write split low/high group descriptor fields.
- `ext2_dirpref`, `ext2_blkpref`, `ext2_hashalloc`: Directory group choice, block preference, and group fallback policy.
- `ext2_cg_block_bitmap_init`, `ext2_alloccg`, `ext2_clusteralloc`, `ext2_nodealloccg`: Bitmap initialization and allocation internals.
- `ext2_blkfree`, `ext2_vfree`, `ext2_cg_has_sb`, `ext2_cg_number_gdb`: Freeing and metadata layout helpers.

Important interactions:
- Uses `ext2_csum.c` for bitmap checksum verification/set operations.
- Called by `ext2_balloc.c`, `ext2_extents.c`, `ext2_inode.c`, extattr code, and directory create paths.
- Uses the ext2 mount mutex around shared accounting, dropping it for bitmap I/O.

Notable risks:
- Several allocation paths return `EFBIG` in callers if a 64-bit allocation cannot fit a 32-bit classic block pointer; callers must free or avoid unusable high blocks.
- Lazy bitmap initialization depends on checksum feature bits and must stay aligned with group descriptor flags.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_balloc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_balloc.c

This file allocates or fetches buffers for logical file blocks. It supports both ext4 extent-backed files and classic ext2 direct/single/double/triple indirect block maps.

Key responsibilities:
- Convert a logical block request into an allocated physical block and returned buffer.
- Maintain sequential allocation hints used by `ext2_blkpref`.
- Allocate direct blocks, indirect metadata blocks, and indirect-referenced data blocks.
- Zero and synchronously write newly allocated indirect metadata before linking it from parent pointers.
- Honor `BA_CLRBUF`, `BA_SEQMASK`, and `IO_SYNC` buffer semantics.
- Dispatch extent-backed files to the extent allocator.

Important functions:
- `ext2_ext_balloc`: Uses `ext4_ext_get_blocks` to map/allocate extent-backed blocks, then returns a vnode buffer or reads existing contents.
- `ext2_balloc`: Main classic allocator. Handles direct blocks first, then uses `ext2_getlbns` to walk/allocate indirect chains and final data blocks.

Important interactions:
- Calls `ext2_alloc`, `ext2_blkpref`, `ext2_blkfree`, `ext2_getlbns`, `ext4_ext_get_blocks`, `bread`, `getblk`, `bwrite`, `bdwrite`, and `cluster_read`.
- Updates inode block arrays and inode change/update flags when new pointers are installed.

Notable risks:
- Classic indirect maps store 32-bit block numbers, so newly allocated blocks above `UINT_MAX` return `EFBIG`.
- Error paths after high-block allocation should be audited because allocation has already occurred before the 32-bit compatibility check.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_bmap.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_bmap.c

This file maps logical ext2 file blocks to physical disk blocks and implements `SEEK_DATA` support for sparse files.

Key responsibilities:
- Implement VOP bmap for classic indirect files and extent-backed files.
- Return physical block numbers plus forward/backward run lengths.
- Read indirect blocks via vnode buffers and explicit device offsets.
- Build indirect-block traversal paths for mapping, allocation, and truncation.
- Locate the next allocated data block for `SEEK_DATA`.

Important functions:
- `ext2_bmap`: VOP wrapper that chooses extent or indirect mapping and returns the underlying device buffer object.
- `ext4_bmapext`: Finds the containing/nearby extent and computes mapped block and run lengths.
- `readindir`: Reads indirect blocks through the buffer cache, strategy I/O, and RACCT accounting when enabled.
- `ext2_bmaparray`: Walks direct/indirect pointers, returns `-1` for holes, and computes sequential runs.
- `ext2_bmap_seekdata`: Scans direct and indirect mappings to advance an offset to the next allocated data block.
- `ext2_getlbns`: Computes the logical metadata-block path and offsets for indirect addressing.

Important interactions:
- Used by VM/buffer-cache paths, `ext2_balloc`, and truncation.
- Depends on `ext4_ext_find_extent`, `ext4_ext_path_free`, and classic inode block arrays.

Notable risks:
- Extent mapping depends on valid extent tree headers and path allocation from `ext2_extents.c`.
- `ext2_getlbns` uses 64-bit intermediate arithmetic for large triple-indirect ranges.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_csum.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_csum.c

This file implements metadata checksum calculation, verification, and update for FreeBSD ext2/ext3/ext4 structures.

Key responsibilities:
- Establish the CRC32C seed from `csum_seed` or filesystem UUID.
- Verify and write superblock checksums.
- Verify and write external xattr block checksums.
- Detect, verify, initialize, and update directory entry checksum tails.
- Verify and update HTree node/root checksums.
- Verify and update extent block checksums.
- Verify and update block/inode bitmap checksums stored in group descriptors.
- Verify and write inode checksums and group descriptor checksums.

Important functions:
- `ext2_sb_csum_set_seed`, `ext2_sb_csum_verify`, `ext2_sb_csum_set`.
- `ext2_extattr_blk_csum_verify`, `ext2_extattr_blk_csum_set`.
- `ext2_init_dirent_tail`, `ext2_is_dirent_tail`, `ext2_dirent_get_tail`, `ext2_dirent_csum_verify`, `ext2_dirent_csum_set`.
- `ext2_dx_csum_verify`, `ext2_dx_csum_set`, `ext2_dir_blk_csum_verify`.
- `ext2_extent_blk_csum_verify`, `ext2_extent_blk_csum_set`.
- `ext2_gd_i_bitmap_csum_*`, `ext2_gd_b_bitmap_csum_*`, `ext2_ei_csum_*`, `ext2_gd_csum_*`.

Important interactions:
- Allocation/free paths call bitmap checksum functions.
- Directory lookup/update and htree mutation paths call directory/htree checksum functions.
- Inode conversion/update calls inode checksum functions.
- Extattr and extent implementations call their block checksum functions.

Notable behavior:
- Most checksum work is bypassed unless metadata checksum feature bits are present.
- Zeroed first-use inodes are accepted even when the computed inode checksum does not match.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_csum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_dinode.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_dinode.h

This header defines ext2/ext3/ext4 on-disk inode constants and the FreeBSD representation of the disk inode layout.

Key responsibilities:
- Define reserved inode numbers, including root, journal, resize, exclude, and first normal inode.
- Define ext2/ext3/ext4 inode flags used for FreeBSD flags and internal state.
- Define extended timestamp epoch/nanosecond bit fields.
- Define direct/indirect block pointer counts and inline symlink capacity.
- Declare `struct ext2fs_dinode`.

Important definitions:
- `EXT2_BADBLKINO`, `EXT2_ROOTINO`, `EXT2_FIRSTINO`, and related reserved inode constants.
- `EXT2_APPEND`, `EXT2_IMMUTABLE`, `EXT2_NODUMP`, `EXT3_INDEX`, `EXT4_EXTENTS`, `EXT4_HUGE_FILE`, `EXT4_INLINE_DATA`, and related flags.
- `E2DI_HAS_XTIME`, `E2DI_HAS_HUGE_FILE`.
- `EXT2_NDIR_BLOCKS`, `EXT2_IND_BLOCK`, `EXT2_DIND_BLOCK`, `EXT2_TIND_BLOCK`, `EXT2_N_BLOCKS`, `EXT2_MAXSYMLINKLEN`.
- `struct ext2fs_dinode`: mode, ownership, size, timestamps, link count, block count, flags, block/extent array, generation, xattr block, high UID/GID, checksum, extra timestamp, birth time, and project ID fields.

Important interactions:
- Used by inode conversion, checksum, allocation, extents, extattrs, and truncation code.
- The `e2di_blocks` array is reused as extent root storage when `EXT4_EXTENTS` is set.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_dir.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_dir.h

This header defines ext2 on-disk directory entry formats, directory slot tracking, checksum tails, file type constants, and record alignment helpers.

Key responsibilities:
- Define old and new ext2 directory entry structures.
- Represent lookup insertion slot state.
- Define metadata-checksum directory tails.
- Define ext2 file type values and maximum link count.
- Provide record length alignment via `EXT2_DIR_REC_LEN`.

Important definitions:
- `struct ext2fs_direct`: Legacy directory entry with 16-bit name length.
- `struct ext2fs_direct_2`: Directory entry with 8-bit name length and file type.
- `enum slotstatus` and `struct ext2fs_searchslot`: Tracks discovered free/compactable insertion space.
- `struct ext2fs_direct_tail`, `EXT2_FT_DIR_CSUM`, `EXT2_DIRENT_TAIL`.
- `EXT2_FT_*` file type constants.
- `EXT2_DIR_PAD`, `EXT2_DIR_ROUND`, `EXT2_DIR_REC_LEN`.

Important interactions:
- Used by directory lookup/update code, HTree indexing, directory checksum handling, and readdir type translation.

Notable behavior:
- Directory checksum tails masquerade as special unused directory entries at the end of a block.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extattr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extattr.c

This file implements extended attribute list/get/set/delete/free operations for in-inode ext4 xattrs and external xattr blocks.

Key responsibilities:
- Translate Linux ext4 xattr namespaces/names to FreeBSD extattr namespaces and POSIX.1e ACL names.
- Validate attribute names and xattr entry lists.
- List and retrieve attributes from in-inode storage and external xattr blocks.
- Delete attributes, compact entries/values, and free storage when the last external attribute is removed.
- Set or replace attributes in in-inode storage or external xattr blocks.
- Clone shared external xattr blocks before modification.
- Maintain xattr entry hashes, block hashes, metadata checksums, inode `i_facl`, `i_blocks`, and inode updates.
- Free external xattr blocks during inode deletion.

Important functions:
- Namespace/name helpers: `ext2_extattr_attrnamespace_to_bsd`, `ext2_extattr_name_to_bsd`, `ext2_extattr_attrnamespace_to_linux`, `ext2_extattr_name_to_linux`, `ext2_extattr_valid_attrname`.
- Validation: `ext2_extattr_check`, `ext2_extattr_block_check`.
- Read paths: `ext2_extattr_inode_list`, `ext2_extattr_block_list`, `ext2_extattr_inode_get`, `ext2_extattr_block_get`.
- Mutation helpers: `ext2_extattr_delete_value`, `ext2_extattr_delete_entry`, `ext2_extattr_block_clone`, `ext2_extattr_set_exist_entry`, `ext2_extattr_set_new_entry`.
- Write/delete/free paths: `ext2_extattr_inode_delete`, `ext2_extattr_block_delete`, `ext2_extattr_inode_set`, `ext2_extattr_block_set`, `ext2_extattr_free`.

Important interactions:
- Uses `ext2_alloc_meta`, `ext2_blkfree`, `ext2_update`, and extattr checksum functions from `ext2_csum.c`.
- Directly reads inode table blocks for in-inode xattrs.
- External xattr blocks use `i_facl` and support shared block refcounts.

Notable risks:
- In-inode set returns `ENOSPC` if no in-inode xattr header exists; external-block set can create a new block.
- Shared xattr blocks are copy-on-write cloned before mutation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extattr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extattr.h

This header defines ext4 extended attribute namespace constants, disk structures, alignment macros, iteration macros, and exported extattr operations.

Key responsibilities:
- Define Linux xattr namespace indexes.
- Define xattr block magic and maximum name length.
- Define xattr name/value/block hash shifts.
- Declare external xattr block headers, in-inode xattr headers, and xattr entries.
- Provide alignment, size, first-entry, next-entry, and terminator macros.
- Declare inode/block list/get/set/delete/free operations.

Important definitions:
- `EXT4_XATTR_INDEX_USER`, `EXT4_XATTR_INDEX_SYSTEM`, POSIX ACL indexes, and other Linux namespace indexes.
- `EXTATTR_MAGIC`, `EXT2_EXTATTR_NAMELEN_MAX`.
- `struct ext2fs_extattr_header`, `struct ext2fs_extattr_dinode_header`, `struct ext2fs_extattr_entry`.
- `EXT2_IFIRST`, `EXT2_HDR`, `EXT2_ENTRY`, `EXT2_FIRST_ENTRY`, `EXT2_IS_LAST_ENTRY`.
- `EXT2_EXTATTR_LEN`, `EXT2_EXTATTR_SIZE`, `EXT2_EXTATTR_NEXT`.

Important interactions:
- Used by `ext2_extattr.c` for storage manipulation and by `ext2_csum.c` for external xattr block checksum coverage.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extents.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extents.c

This file implements FreeBSD ext4 extent tree support for ext2fs: extent validation, lookup, caching, insertion, tree splitting/growth, allocation, mapping support, and truncation/removal.

Key responsibilities:
- Initialize inode extent roots and cache state.
- Decode/store physical block fields in extent and index entries.
- Validate extent headers, extents, indexes, block ranges, ordering, and checksums.
- Find the path to an extent through root and index blocks.
- Cache mapped extents.
- Insert new extents, merge adjacent extents, correct parent indexes, split full leaves/indexes, and grow tree depth.
- Allocate extent metadata and data blocks.
- Remove extent ranges during truncation and free empty leaf/index blocks.
- Optionally print/walk extent trees under `EXT2FS_PRINT_EXTENTS`.

Important functions:
- `ext4_ext_tree_init`, `ext4_ext_in_cache`, `ext4_ext_find_extent`, `ext4_ext_path_free`.
- `ext4_ext_check_header`, `ext4_validate_extent_entries`, `ext4_ext_binsearch_index`, `ext4_ext_binsearch_ext`.
- `ext4_ext_dirty`, `ext4_ext_insert_index`, `ext4_ext_split`, `ext4_ext_grow_indepth`, `ext4_ext_create_new_leaf`.
- `ext4_ext_insert_extent`, `ext4_new_blocks`, `ext4_ext_get_blocks`.
- `ext4_ext_remove_space`, `ext4_ext_rm_leaf`, `ext4_ext_rm_index`, `ext4_read_extent_tree_block`.

Important interactions:
- Called by `ext2_balloc.c`, `ext2_bmap.c`, `ext2_inode.c`, and inode allocation.
- Uses `ext2_alloc`, `ext2_alloc_meta`, `ext2_blkfree`, `ext2_update`, and extent checksum helpers.
- Maintains `ip->i_ext_cache` and inode `IN_E4EXTENTS` state.

Notable limitations and risks:
- `ext4_new_blocks` only allocates a single block; multi-block requests currently fail to allocate as a run.
- Removal supports tail cleanup and whole extent removal but rejects middle/head-only cases.
- Extent metadata is copied into path-owned memory and written back explicitly through `ext4_ext_dirty`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extents.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extents.h

This header defines ext4 extent on-disk structures, constants, cache state, path state, helper macros, and exported extent APIs.

Key responsibilities:
- Define extent magic, maximum logical range constants, and maximum depth.
- Define cache result constants.
- Declare extent tail, extent, extent index, extent header, extent cache, and extent path structures.
- Provide macros for locating first/last/max extent/index entries and checksum tail offsets.
- Declare extent tree operations used by allocation, mapping, truncation, and debug code.

Important definitions:
- `EXT4_EXT_MAGIC`, `EXT4_MAX_BLOCKS`, `EXT_INIT_MAX_LEN`, `EXT4_MAX_LEN`, `EXT4_EXT_DEPTH_MAX`.
- `EXT4_EXT_CACHE_NO`, `EXT4_EXT_CACHE_GAP`, `EXT4_EXT_CACHE_IN`.
- `struct ext4_extent_tail`, `struct ext4_extent`, `struct ext4_extent_index`, `struct ext4_extent_header`.
- `struct ext4_extent_cache`, `struct ext4_extent_path`.
- `EXT_FIRST_EXTENT`, `EXT_FIRST_INDEX`, `EXT_LAST_EXTENT`, `EXT_LAST_INDEX`, `EXT4_EXTENT_TAIL_OFFSET`, `EXT_HAS_FREE_INDEX`.

Important interactions:
- Included by extent implementation, bmap/balloc/truncate paths, checksum code, and inode conversion/debug paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extents.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extern.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extern.h

This header declares the cross-file ext2fs API used by allocation, mapping, inode conversion, directory operations, htree indexing, checksums, and vnode operations.

Key responsibilities:
- Export block/inode allocation, freeing, mapping, truncation, and update functions.
- Export directory lookup, readdir, insertion, deletion, rewrite, emptiness, and path-check functions.
- Export HTree lookup/add/create/hash helpers.
- Export checksum functions for superblocks, extattrs, directories, htree nodes, extents, bitmaps, inodes, and group descriptors.
- Export group descriptor accessors and sparse-superblock helpers.
- Define low-level block allocation flags.

Important definitions:
- Allocation/mapping prototypes: `ext2_alloc`, `ext2_balloc`, `ext2_blkfree`, `ext2_blkpref`, `ext2_bmap`, `ext4_bmapext`, `ext2_bmap_seekdata`.
- Inode lifecycle/conversion prototypes: `ext2_ei2i`, `ext2_i2ei`, `ext2_truncate`, `ext2_update`, `ext2_valloc`, `ext2_vfree`, `ext2_inactive`, `ext2_reclaim`.
- Directory/HTree prototypes: `ext2_lookup`, `ext2_readdir`, `ext2_htree_*`.
- Checksum prototypes: `ext2_sb_csum_*`, `ext2_extattr_blk_csum_*`, `ext2_dirent_csum_*`, `ext2_dx_csum_*`, `ext2_extent_blk_csum_*`, bitmap/inode/group descriptor checksum helpers.
- `BA_CLRBUF`, `BA_SEQMASK`, `BA_SEQSHIFT`, `BA_SEQMAX`.

Important interactions:
- Serves as the main private header connecting the ext2fs implementation units in this group with lookup, vnode, mount, and subr files outside this group.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_hash.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_hash.c

This file implements ext2/ext3/ext4 directory HTree hash algorithms compatible with Linux indexed directories.

Key responsibilities:
- Provide half-MD4, TEA, and legacy directory name hashing.
- Support signed and unsigned character variants.
- Prepare padded hash input buffers in Linux-compatible form.
- Apply filesystem hash seeds when present.
- Normalize major hash values for HTree ordering and EOF collision avoidance.

Important functions:
- `ext2_half_md4`: Modified half-MD4 transform used by Linux dirindex.
- `ext2_tea`: Tiny Encryption Algorithm based hash transform.
- `ext2_legacy_hash`: Original ext2 legacy name hash.
- `ext2_prep_hashbuf`: Converts name bytes into padded 32-bit hash words.
- `ext2_htree_hash`: Public dispatcher for `EXT2_HTREE_TEA`, `LEGACY`, `HALF_MD4`, and unsigned variants; returns major/minor hash values.

Important interactions:
- Called by `ext2_htree.c` to find leaves, split directory blocks, create indexes, and add indexed entries.
- Uses HTree constants from `htree.h` and trace probes for unexpected hash versions.

Notable behavior:
- Returns `-1` and zeroes output hashes for invalid names or unsupported hash versions.
- Clears the low collision bit in the major hash and avoids the HTree EOF sentinel value.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_htree.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_htree.c

This file implements ext3/ext4 HTree indexed directory lookup, index creation, and indexed directory insertion.

Key responsibilities:
- Detect HTree-indexed directories.
- Traverse one- or two-level HTree indexes to find target leaf directory blocks.
- Handle hash collisions by checking adjacent leaves when required.
- Search leaf directory blocks with the normal ext2 directory scanner.
- Convert a linear directory block into indexed root plus leaf blocks.
- Split full directory blocks by hash order and insert the new entry into the correct half.
- Split full index nodes or create a second HTree level.
- Maintain directory and htree checksums when metadata checksums are enabled.

Important functions:
- `ext2_htree_has_idx`: Checks feature and inode flag.
- `ext2_htree_find_leaf`: Reads root, validates hash version/limits, computes hash, and walks index levels.
- `ext2_htree_lookup`: Searches selected and collision-adjacent leaf blocks.
- `ext2_htree_create_index`: Converts a directory to HTree format and appends two leaf blocks.
- `ext2_htree_add_entry`: Splits full leaves and indexes, appends new blocks, and writes updated index buffers.
- `ext2_htree_split_dirblock`: Sorts entries by hash, moves roughly half to a new block, and computes split hash.
- `ext2_htree_insert_entry`, `ext2_htree_writebuf`, `ext2_htree_check_next`: Index manipulation and write helpers.

Important interactions:
- Uses `ext2_htree_hash` from `ext2_hash.c`, directory structures from `ext2_dir.h`, and checksum functions from `ext2_csum.c`.
- Calls `ext2_blkatoff`, `ext2_search_dirblock`, `ext2_add_entry`, `VOP_WRITE`, and buffer-cache writes.

Notable risks:
- Lookup intentionally avoids `.` and `..`.
- Directory index depth is limited to at most one indirect level beyond the root in this implementation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_htree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_inode.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_inode.c

This file handles inode updates, truncation, inactive cleanup, and vnode reclamation for FreeBSD ext2fs.

Key responsibilities:
- Flush changed inode state to disk.
- Update timestamps before inode writeback.
- Truncate or extend classic direct/indirect block files.
- Truncate or extend extent-backed files.
- Recursively free indirect blocks and data blocks.
- Remove extent ranges through the extent implementation.
- Free extended attributes and data for unlinked inactive inodes.
- Return inode numbers to the inode bitmap and reclaim vnode-private inode memory.

Important functions:
- `ext2_update`: Converts in-memory inode to disk inode and writes/buffers the inode table block.
- `ext2_indirtrunc`: Recursively clears and frees indirect block subtrees.
- `ext2_ind_truncate`: Handles grow/shrink for classic block-map files.
- `ext2_ext_truncate`: Handles grow/shrink for extent-backed files via `ext4_ext_remove_space`.
- `ext2_truncate`: Dispatches symlink, no-op, extent, or indirect truncation.
- `ext2_inactive`: For zero-link inodes, frees extattrs, truncates data, clears mode, and calls `ext2_vfree`.
- `ext2_reclaim`: Flushes lazy modifications, removes vnode hash entry, and frees inode memory.

Important interactions:
- Uses `ext2_balloc`, `ext2_blkfree`, `ext2_i2ei`, `ext2_extattr_free`, `ext4_ext_remove_space`, and vnode pager/buffer truncation APIs.
- Inactive path coordinates xattr cleanup, block freeing, and inode bitmap freeing.

Notable risks:
- Triple indirect truncation is explicitly noted as untested.
- Extent truncation delegates range removal to `ext2_extents.c`, which has partial-range limitations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_inode_cnv.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_inode_cnv.c

This file converts ext2/ext3/ext4 on-disk inodes to FreeBSD in-memory `struct inode` objects and back.

Key responsibilities:
- Validate inode numbers, root inode structure, and extra inode size.
- Decode mode, link count, size, timestamps, flags, block counts, xattr block pointers, generation, UID/GID, device numbers, and block/extent pointers.
- Decode ext4 extra timestamp epoch/nanosecond fields and birth time.
- Encode FreeBSD inode state back to little-endian disk format.
- Encode large block counts with `EXT4_HUGE_FILE` when needed.
- Preserve extent root bytes when `IN_E4EXTENTS` is set.
- Verify and set inode metadata checksums.

Important functions:
- `ext2_print_inode`: Optional debug printer under `EXT2FS_PRINT_EXTENTS`.
- `ext2_old_valid_dev`, `ext2_old_encode_dev`, `ext2_old_decode_dev`, `ext2_new_encode_dev`, `ext2_new_decode_dev`: Device number format conversion.
- `ext2_decode_extra_time`, `ext2_encode_extra_time`: ext4 timestamp extension conversion.
- `ext2_ei2i`: Disk-to-memory inode conversion and checksum verification.
- `ext2_i2ei`: Memory-to-disk inode conversion and checksum update.

Important interactions:
- Called by inode read/update paths and `ext2_update`.
- Uses constants from `ext2_dinode.h` and checksum helpers from `ext2_csum.c`.
- Maps disk flags to FreeBSD `SF_APPEND`, `SF_IMMUTABLE`, `UF_NODUMP`, `IN_E3INDEX`, and `IN_E4EXTENTS`.

Notable behavior:
- Zero-link disk inodes are exposed with `i_mode = 0`.
- Regular files can use high size bits; non-regular files do not.
- Huge-file block count encoding depends on filesystem feature support.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_inode_cnv.c -->