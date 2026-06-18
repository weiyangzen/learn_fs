# Group Research: group_345_e2fsprogs_sources_local_fs_e2fsprogs_lib_ext2fs_bitops_c_sources_loc_830b545790d4

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/e2fsprogs`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bitops.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bitops.c

Implements portable byte-addressed bitmap primitives used by libext2fs. The public functions set, clear, and test single bits for both 32-bit offsets (`ext2fs_set_bit`, `ext2fs_clear_bit`, `ext2fs_test_bit`) and 64-bit offsets (`ext2fs_set_bit64`, `ext2fs_clear_bit64`, `ext2fs_test_bit64`).

The functions operate little-bit-first within each byte and return the previous bit value for set/clear/test style callers. `ext2fs_warn_bitmap` conditionally reports bitmap misuse through `com_err` unless `OMIT_COM_ERR` is defined.

The file also provides `ext2fs_bitcount`, which counts set bits in a byte range using local `popcount8` and `popcount32` helpers. It aligns to a 32-bit boundary, processes 32-bit words, then handles trailing bytes.

Dependencies: `config.h`, `ext2_fs.h`, `ext2fs.h`; uses `uintptr_t`, `__u32`, and `__u64`.

Implementation notes:
- No bounds checking is performed here; callers must ensure the bit offset is inside the backing allocation.
- The bit ordering is intentionally portable across endian variants because it manipulates bytes directly.
- The `while (nbytes > 4)` loop processes only when more than four bytes remain, leaving exactly four bytes to the byte tail path.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bitops.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bitops.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bitops.h

Defines endian conversion macros, bitmap API declarations, and inline wrappers around generic 32-bit and 64-bit bitmap operations. It is the central public/internal header for libext2fs bitmap bit manipulation.

The endian section maps CPU/LE/BE conversions to no-ops or `ext2fs_swab16/32/64` depending on `WORDS_BIGENDIAN`. The inline section defines fast bit setters/clearers, byte-swap helpers, and typed wrappers for block and inode bitmaps.

The header preserves compatibility with `NO_INLINE_FUNCS` and `INCLUDE_INLINE_FUNCS`: when inlining is disabled it declares external functions, otherwise it emits `_INLINE_` functions. 32-bit bitmap wrappers call `ext2fs_mark_generic_bitmap`, `ext2fs_unmark_generic_bitmap`, and `ext2fs_test_generic_bitmap`; 64-bit wrappers call the generic bmap variants.

Key API groups:
- Raw bit operations: `ext2fs_set_bit`, `ext2fs_clear_bit`, `ext2fs_test_bit`, and 64-bit forms.
- Typed bitmap operations: mark/unmark/test block and inode bitmaps.
- Range operations and first-set/first-zero scans for block and inode bitmaps.
- Generic bitmap/bmap start/end and padding helpers.
- Byte swap helpers and endian conversion macros.

Implementation notes:
- This header is a compatibility bridge between older 32-bit bitmap APIs and newer 64-bit bmap APIs.
- Duplicate declarations for `ext2fs_test_block_bitmap_range2` appear in the extern section.
- Inline “fast” typed bitmap functions still route through generic bitmap functions; “fast” mostly means no old-style warning path or previous-value contract at the typed wrapper layer.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/blkmap64_ba.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/blkmap64_ba.c

Implements the flat bitarray backend for `ext2fs_generic_bitmap_64`. The backend stores one contiguous byte array in `struct ext2fs_ba_private_struct` and exports it through `ext2fs_blkmap64_bitarray`.

Core operations allocate, free, copy, resize, mark, unmark, test, range mark/unmark, clear-range test, set/get raw ranges, clear the whole bitmap, print optional stats, and find first set/zero bits.

Behavior details:
- Allocation size is `((real_end - start) / 8) + 1`.
- Mark/test/unmark subtract `bitmap->start` before accessing raw bits.
- Resize clears newly exposed bits when growing and resizes backing memory when `real_end` changes.
- `ba_test_clear_bmap_extent` checks partial first/last bytes and uses `ext2fs_mem_is_zero` for full bytes.
- First-set and first-zero scans optimize alignment, then scan 64-bit chunks, bytes, and trailing bits.

Dependencies: `ext2fsP.h`, `bmap64.h`, raw bitops from `bitops.c/h`, libext2fs memory allocation helpers.

Implementation notes:
- `ba_set_bmap_range` and `ba_get_bmap_range` copy raw packed bitmap bytes starting at `start >> 3`; callers are expected to pass range offsets in the backend’s expected coordinate system.
- This backend is memory-heavy but simple and fast for dense bitmaps.
- It is selected through the `struct ext2_bitmap_ops` vtable with type `EXT2FS_BMAP64_BITARRAY`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/blkmap64_ba.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/blkmap64_rb.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/blkmap64_rb.c

Implements the red-black-tree extent backend for sparse 64-bit bitmaps. Set bits are represented as non-overlapping extents (`start`, `count`) stored in an rbtree, with read/write cursors for locality.

Core structures:
- `struct bmap_rb_extent`: rbtree node plus extent start/count.
- `struct ext2fs_rb_private`: rbtree root, write cursor, read cursor, next read cursor, optional stats counters.

Core behavior:
- `rb_insert_extent` inserts a set-bit extent, merging adjacent or overlapping neighbors.
- `rb_remove_extent` clears a range, truncating, deleting, or splitting extents.
- `rb_test_bit` checks cursor hits first, then searches the rbtree.
- `rb_set_bmap_range` converts a packed bit array into extents.
- `rb_get_bmap_range` emits packed bits from matching extents.
- `rb_find_first_zero` and `rb_find_first_set` search within inclusive bounds.
- `rb_resize_bmap` truncates extents beyond the new end and marks padding beyond logical end to real end.

The exported `ext2fs_blkmap64_rbtree` vtable implements the same `ext2_bitmap_ops` contract as the bitarray backend.

Dependencies: `ext2fsP.h`, `bmap64.h`, `rbtree.h`, raw bitops, libext2fs allocators.

Implementation notes:
- This backend is optimized for sparse maps, especially large filesystems with long runs.
- Debug-only `check_tree` validates sorted, non-overlapping, nonzero extents.
- `rb_get_new_extent` aborts on allocation failure rather than returning an error, unlike most libext2fs allocation paths.
- `rb_find_first_zero` returns `ENOENT` for an empty tree, which treats an all-zero sparse bitmap differently than the intuitive “start is zero”; callers need to account for backend semantics or generic wrappers.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/blkmap64_rb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/blknum.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/blknum.c

Provides 64-bit block-number and group-descriptor accessor helpers. It centralizes low/high field composition for ext2/ext4 superblock counters, group descriptor block pointers, counts, flags, checksums, and inode size/ACL fields.

Major API groups:
- Group geometry: `ext2fs_group_of_blk2`, `ext2fs_group_first_block2`, `ext2fs_group_last_block2`, `ext2fs_group_blocks_count`.
- Inode block counts: `ext2fs_inode_data_blocks2`, `ext2fs_inode_i_blocks`, `ext2fs_get_stat_i_blocks`.
- Superblock counters: blocks, reserved blocks, free blocks get/set/add.
- Descriptor access: `ext2fs_group_desc` and internal `ext4fs_group_desc`.
- Group descriptor fields: bitmap locations/checksums, inode table location, free counts, used dirs, unused inode table count, flags, checksum.
- Inode fields: `ext2fs_file_acl_block`, `ext2fs_file_acl_block_set`, `ext2fs_inode_size_set`.

Behavior details:
- 64-bit high halves are only used when the filesystem has the 64bit feature.
- `ext2fs_group_desc` can index an in-memory descriptor table or lazily read a descriptor block into a static buffer if `gdp` is NULL.
- `ext2fs_inode_size_set` updates `large_file` or `largedir` features when needed, updates dynamic revision if necessary, marks the superblock dirty, and rejects oversized non-regular/non-directory files.

Implementation notes:
- The static lazy descriptor buffer in `ext2fs_group_desc` is process-global and not thread-safe.
- Several setters intentionally leave high fields untouched when 64bit is not enabled.
- `ext2fs_inode_data_blocks2` subtracts external ACL cluster sectors from `i_blocks`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/blknum.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/block.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/block.c

Implements inode block iteration for direct, indirect, double-indirect, triple-indirect, extent-based, and HURD translator blocks. The primary API is `ext2fs_block_iterate3`; older `ext2fs_block_iterate2` and `ext2fs_block_iterate` are compatibility wrappers.

The iterator callback receives filesystem, mutable block number, logical block count, referring block, reference offset, and private data. Return flags such as `BLOCK_CHANGED`, `BLOCK_ABORT`, and `BLOCK_ERROR` control mutation and traversal termination.

Traversal modes:
- Direct block array entries are visited first for classic block-mapped inodes.
- Indirect levels are handled by `block_iterate_ind`, `block_iterate_dind`, and `block_iterate_tind`.
- Extent inodes use `ext2fs_extent_open2`, `ext2fs_extent_get`, `ext2fs_extent_replace`, and `ext2fs_extent_set_bmap`.
- `BLOCK_FLAG_APPEND` visits sparse holes to allow allocation/appending.
- `BLOCK_FLAG_DEPTH_TRAVERSE` changes when metadata blocks are reported.
- `BLOCK_FLAG_DATA_ONLY` suppresses indirect/extent metadata callbacks.
- `BLOCK_FLAG_READ_ONLY` rejects callbacks that try to change blocks.

Safety behavior:
- Invalid indirect block numbers outside filesystem bounds return specific bad-indirect errors.
- Inline-data inodes return `EXT2_ET_INLINE_DATA_CANT_ITERATE`.
- `BLOCK_FLAG_NO_LARGE` rejects large non-directory old-style iteration.
- Changed indirect buffers and inode blocks are written back before return.

Implementation notes:
- The file maintains logical block count carefully across sparse indirect ranges.
- Extent traversal handles uninitialized extents and append allocation through `ext2fs_extent_set_bmap`.
- Compatibility wrappers downcast 64-bit block numbers to 32-bit callback signatures.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/block.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bmap.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bmap.c

Maps a logical file block to a physical filesystem block and optionally allocates, sets, or zeroes the mapping. The primary API is `ext2fs_bmap2`; `ext2fs_bmap` is the legacy 32-bit wrapper.

Classic block mapping:
- Direct blocks are read or updated from `inode->i_block`.
- Single, double, and triple indirect mappings use `block_ind_bmap`, `block_dind_bmap`, and `block_tind_bmap`.
- Missing indirect blocks can be allocated when `BMAP_ALLOC` is set.
- `BMAP_SET` writes a caller-provided physical block and errors if the required indirect block is absent.
- Big-endian builds swap indirect block entries on read/write.

Extent mapping:
- Extent inodes are handled by `extent_bmap`.
- Existing extents are found through `ext2fs_extent_goto` and `EXT2_EXTENT_CURRENT`.
- `BMAP_ALLOC` can allocate a new block and install it with `ext2fs_extent_set_bmap`.
- `BMAP_UNINIT` preserves uninitialized extent state.
- `BMAP_RET_UNINIT` is returned through `ret_flags`.

Bigalloc behavior:
- `implied_cluster_alloc` maps unallocated logical blocks to an already allocated physical cluster sibling.
- `ext2fs_map_cluster_block` exposes cluster-relative lookup for bigalloc extent files.

Validation and updates:
- `ext2fs_file_block_offset_too_big` rejects offsets past classic indirect addressing limits or the kernel 32-bit logical block cutoff.
- Inline-data inodes return `EXT2_ET_INLINE_DATA_NO_BLOCK`.
- Allocations update inode block counts via `ext2fs_iblk_add_blocks` and write the inode.
- `BMAP_ZERO` zeroes the mapped physical block after successful lookup/allocation.

Implementation notes:
- The function can read the inode itself if the caller passes NULL.
- It allocates two block buffers when none is supplied.
- Legacy `ext2fs_bmap` returns `EOVERFLOW` if the resulting physical block does not fit in 32 bits.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bmap64.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bmap64.h

Defines the private 64-bit generic bitmap structure and backend operation table used by libext2fs. This header is the common contract implemented by `blkmap64_ba.c` and `blkmap64_rb.c`.

Key structures:
- `struct ext2_bmap_statistics`: optional bitmap operation counters and locality statistics.
- `struct ext2fs_struct_generic_bitmap_64`: magic, filesystem pointer, backend ops, flags, logical start/end, real end, cluster bits, description, private backend data, and base error code.
- `struct ext2_bitmap_ops`: backend vtable for allocation, free, copy, resize, mark/unmark/test, extent operations, raw range import/export, clear, stats, and first-set/first-zero search.

Macros:
- `EXT2FS_IS_32_BITMAP`
- `EXT2FS_IS_64_BITMAP`

Exports:
- `ext2fs_blkmap64_bitarray`
- `ext2fs_blkmap64_rbtree`

Implementation notes:
- Backends may leave first-set/first-zero NULL so generic code can provide fallback behavior.
- `real_end` allows padding bits beyond logical `end`.
- `cluster_bits` lets bitmap users represent cluster-addressed maps.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bmap64.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bmove.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bmove.c

Implements `ext2fs_move_blocks`, which relocates file blocks away from reserved blocks. It scans all inodes, iterates their blocks, copies block contents to free locations, and updates block pointers through the block iterator callback.

The callback `process_block` checks whether a block is marked in the reserve bitmap. If so, it searches forward, wrapping at filesystem end, for a block absent from both the reserve bitmap and allocation map. It reads the old block, writes it to the new block, updates the block number, marks the allocation map, and returns `BLOCK_CHANGED`.

`EXT2_BMOVE_GET_DBLIST` causes the move pass to rebuild `fs->dblist` by adding directory blocks as they are encountered.

Dependencies: inode scan API, block iterator, block bitmap APIs, IO channel read/write, directory block list APIs.

Implementation notes:
- The provided `alloc_map` defaults to `fs->block_map`.
- It skips unlinked inodes and inodes without valid blocks.
- Error handling stores callback errors in `pb.error` and aborts iteration.
- Several early-return error paths after allocations/scans do not clean up all intermediate resources in this old code path.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bmove.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/brel.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/brel.h

Declares the block relocation table abstraction. A relocation entry maps an old block to a new block and records reference metadata describing whether the owner is a block reference or inode reference.

Key types:
- `struct ext2_block_relocate_entry`: new block, offset, flags, and owner union.
- `ext2_brel`: pointer to `struct ext2_block_relocation_table`.
- `struct ext2_block_relocation_table`: magic, name, iterator cursor, private data, and method table.

Operations:
- `put`, `get`
- `start_iter`, `next`
- `move`, `delete`
- `free`

Macros wrap method calls as `ext2fs_brel_put`, `ext2fs_brel_get`, etc.

The header declares `ext2fs_brel_memarray_create`, implemented in `brel_ma.c`.

Implementation notes:
- `RELOCATE_TYPE_REF` masks reference type bits.
- The abstraction is backend-oriented, but this group includes only the memory-array backend.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/brel.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/brel_ma.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/brel_ma.c

Implements the memory-array backend for block relocation tables. The file comments note it should be rewritten to avoid a direct array and that the module was not really used at the time.

`ext2fs_brel_memarray_create` allocates the public table, copies the name, allocates backend private state, and allocates `max_block + 1` relocation entries. It wires the table methods to local `bma_*` functions.

Backend behavior:
- `bma_put` stores an entry at index `old`.
- `bma_get` returns `ENOENT` if the entry’s `new` field is zero.
- `bma_start_iter` resets the cursor to zero.
- `bma_next` scans forward for entries with nonzero `new`; returns old block zero when exhausted.
- `bma_move` copies an entry from old to new and clears old.
- `bma_delete` clears the old entry’s `new` field.
- `bma_free` frees entries, private state, name, and table.

Implementation notes:
- Direct indexing by block number makes memory usage proportional to maximum block number.
- Some array indexes cast `blk64_t` to `unsigned`, limiting practical safety for very large values despite 64-bit parameters.
- `bma_next` uses `< ma->max_block`, so an entry exactly at `max_block` is not returned by iteration.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/brel_ma.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/check_desc.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/check_desc.c

Implements `ext2fs_check_desc`, a sanity check for ext2/ext4 group descriptors. It verifies descriptor size, metadata block placement, and collisions among superblock/GDT reservations, block bitmaps, inode bitmaps, and inode tables.

Algorithm:
- Verify descriptor size is a power of two.
- Allocate a subcluster bitmap named `check_desc map`.
- Reserve superblock and group descriptor blocks for every group.
- For each group, choose allowed block range. Without `flex_bg`, the range is the group’s own first/last block; with `flex_bg`, the broader filesystem data range is allowed.
- Check block bitmap location is in range and not already reserved/used.
- Check inode bitmap location similarly.
- Check inode table range fits and does not collide with existing marks.
- Mark each accepted structure block in the temporary bitmap.

Returns specific descriptor errors such as bad block map, bad inode map, or bad inode table.

Dependencies: block bitmap allocation, descriptor accessors from `blknum.c`, super/GDT reservation helpers.

Implementation notes:
- The function frees the temporary bitmap on all exit paths.
- It relies on bitmap collision detection to catch overlapping metadata structures.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/check_desc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/closefs.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/closefs.c

Handles filesystem flush and close operations, backup superblock/GDT placement, sparse-super rules, dynamic revision updates, and final resource release.

Major APIs:
- `ext2fs_bg_has_super`: determines whether a group has a backup superblock, supporting sparse_super and sparse_super2.
- `ext2fs_super_and_bgd_loc2`: computes superblock, old descriptor, meta_bg descriptor, and used-block locations for a group.
- `ext2fs_super_and_bgd_loc`: legacy 32-bit wrapper that returns an approximate free block count.
- `ext2fs_update_dynamic_rev`: upgrades old revision superblocks to dynamic revision defaults.
- `ext2fs_flush` / `ext2fs_flush2`: writes dirty bitmaps, descriptors, backup superblocks, and primary superblock.
- `ext2fs_close`, `ext2fs_close2`, `ext2fs_close_free`: flush, stop MMP, free filesystem handles.

Flush behavior:
- Writes bitmaps first because bitmap checksums live in descriptors.
- Temporarily clears valid state and journal recovery state while writing backups.
- Handles big-endian swapping through shadow superblock and descriptor buffers.
- Writes backup superblocks/descriptors unless `EXT2_FLAG_MASTER_SB_ONLY` or journal device rules suppress them.
- Writes the primary superblock last, preserving selected original fields when byte-write support exists.
- Updates `s_kbytes_written` from IO stats on close.

Implementation notes:
- `write_primary_superblock` tries byte-range writes of changed superblock words and falls back to full superblock write if unsupported.
- `ext2fs_flush2` restores the in-memory filesystem state after write attempts.
- External journal devices skip descriptor and backup-super writes.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/closefs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/compiler.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/compiler.h

Small compiler-compatibility header. It defines `__GNUC_PREREQ` when missing and provides `container_of`.

For GCC, `container_of` uses `__typeof__` to type-check the member pointer before subtracting `offsetof(type, member)`. For non-GCC compilers, it uses a simpler cast-based implementation.

Dependencies: `<stddef.h>` for `offsetof`.

Implementation notes:
- Header guard is `_EXT2FS_COMPILER_H`.
- This is infrastructure used by intrusive data structures and other low-level helpers.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/compiler.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/crc16.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/crc16.c

Implements table-driven CRC-16 using polynomial `0x8005`. The exported function is `ext2fs_crc16`.

The file contains a 256-entry CRC table and updates the CRC byte by byte. It stores the CRC in `crc16_t`, which is an unsigned int typedef from `crc16.h`, to avoid sign-extension issues observed on PowerPC with `__u16`.

Dependencies: `config.h`, optional `sys/types.h`, `ext2fs/ext2_types.h`, `crc16.h`.

Usage in this group: old group descriptor checksums in `csum.c`.

Implementation notes:
- The function accepts a previous CRC seed so callers can compute incrementally.
- It masks to 16 bits after each step.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/crc16.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/crc16.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/crc16.h

Declares the CRC-16 interface and documents the algorithm parameters: width 16, polynomial `0x8005`, initial value 0.

Defines:
- `typedef unsigned int crc16_t`
- `extern crc16_t ext2fs_crc16(crc16_t crc, const void *buffer, unsigned int len)`

Implementation note:
- The unsigned int typedef intentionally avoids platform sign-extension problems with 16-bit integer types.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/crc16.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/crc32c.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/crc32c.c

Implements CRC32C and big-endian CRC32 routines reused from kernel-derived/public-domain lineage and relicensed under GPLv2. The exported functions are `ext2fs_crc32c_le` and `ext2fs_crc32_be`.

Algorithm behavior:
- Includes generated/static tables from `crc32c_table.h`.
- Supports selectable bit widths via `CRC_LE_BITS` and `CRC_BE_BITS`, defaulting to 64.
- Uses slicing-by-4 or slicing-by-8 in `crc32_body` for wide table modes.
- Handles byte alignment before word-at-a-time processing.
- Provides bitwise, 2-bit, 4-bit, 8-bit, 32-bit, and 64-bit paths depending on compile-time definitions.
- Converts CRC state to/from CPU endian for wide table processing.

Dependencies: `crc32c_defs.h`, `crc32c_table.h`, `ext2fs.h`, endian macros from bitops.

Unit-test code under `UNITTEST` defines test buffers and expected CRCs for both LE CRC32C and BE CRC32.

Implementation notes:
- `ext2fs_crc32c_le` uses Castagnoli polynomial through `CRC32C_POLY_LE`.
- `ext2fs_crc32_be` uses Ethernet CRC32 polynomial through `CRCPOLY_BE`.
- The function takes a seed and does not force a final xor, leaving policy to callers.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/crc32c.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/crc32c_defs.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/crc32c_defs.h

Defines CRC polynomial constants, compile-time table width controls, validation checks, constant byte-swap helper, and branch prediction macros for `crc32c.c`.

Constants:
- `CRCPOLY_LE` / `CRCPOLY_BE`: standard Ethernet CRC32 polynomial.
- `CRC32C_POLY_LE` / `CRC32C_POLY_BE`: Castagnoli CRC32C polynomial.

Configuration:
- `CRC_LE_BITS` defaults to 64.
- `CRC_BE_BITS` defaults to 64.
- Preprocessor checks reject invalid widths; valid values are 1, 2, 4, 8, 32, and 64.

Helpers:
- `___constant_swab32`
- `likely`
- `unlikely`

Implementation notes:
- The header assumes `uint32_t` is available from the includer.
- Wide CRC modes are intended for performance-sensitive code paths.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/crc32c_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/csum.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/csum.c

Implements ext2/ext4 metadata checksum support. It covers checksum seed initialization, MMP, superblock, extended attribute blocks, directory blocks, htree index blocks, extent blocks, inode/block bitmaps, inodes, group descriptors, and GDT checksum updates.

Major API groups:
- Seed/type: `ext2fs_init_csum_seed`, `ext2fs_verify_csum_type`.
- MMP: verify/set checksum over `struct mmp_struct`.
- Superblock: verify/set checksum over the superblock up to `s_checksum`.
- EA block: verify/set checksum using block number and UUID or checksum seed.
- Directory tails: locate/initialize dirent checksum tail and htree dx tail.
- Directory block checksum: verify/set normal dirent tail or htree dx checksum.
- Extent block checksum: verify/set extent tree tail checksum.
- Bitmap checksum: verify/set inode and block bitmap checksums in group descriptors.
- Inode checksum: verify/set inode checksum with optional high checksum field.
- Group descriptor checksum: compute, verify, set old crc16 or metadata_csum crc32c.
- GDT update: `ext2fs_set_gdt_csum` updates uninit flags, itable unused watermark, and descriptor checksums.

Important behavior:
- Metadata checksums use `fs->csum_seed`; old group descriptor checksums use CRC16 seeded by UUID and group.
- Directory checksum code distinguishes normal directory tails from htree dx tails.
- Inode checksum verification treats an all-zero base inode as valid despite mismatch.
- Big-endian descriptor checksums temporarily swab descriptor fields back to little-endian form for checksum calculation.
- `EXT2_FLAG_IGNORE_CSUM_ERRORS` suppresses some directory checksum failures.

Dependencies: CRC16, CRC32C, descriptor accessors, inode read, directory structures, extents, feature flags.

Implementation notes:
- Many setters are no-ops when the relevant checksum feature is disabled.
- Group descriptor checksum calculation intentionally zeros the checksum field during calculation.
- `ext2fs_set_gdt_csum` requires an inode bitmap and marks the superblock dirty if flags, unused counts, or checksums change.
- The file contains debug/unit-test code under `DEBUG`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/csum.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dblist.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dblist.c

Implements directory block list management. A dblist is a growable array of `struct ext2_db_entry2` records sorted by block, inode, and logical block count.

Core APIs:
- `ext2fs_init_dblist`
- `ext2fs_copy_dblist`
- `ext2fs_add_dir_block2`
- `ext2fs_set_dir_block2`
- `ext2fs_dblist_sort2`
- `ext2fs_dblist_iterate3`
- `ext2fs_dblist_iterate2`
- `ext2fs_dblist_count2`
- `ext2fs_dblist_get_last2`
- `ext2fs_dblist_drop_last`

Legacy 32-bit APIs wrap the 64-bit versions: `ext2fs_add_dir_block`, `ext2fs_set_dir_block`, `ext2fs_dblist_sort`, `ext2fs_dblist_iterate`, `ext2fs_dblist_count`, and `ext2fs_dblist_get_last`.

Behavior:
- Initial capacity is either caller-provided or roughly twice the directory count plus 12.
- Appending grows capacity by 100 entries for small lists or 50% for larger lists.
- Iteration sorts lazily if the list is dirty.
- `DBLIST_ABORT` from callbacks stops iteration without returning an error.

Implementation notes:
- Legacy `ext2fs_dblist_get_last` returns a pointer to a static converted 32-bit entry, so it is not reentrant.
- Sorting can use either the native 64-bit comparator or a caller-provided legacy comparator via a global `sortfunc32`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dblist.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dblist_dir.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dblist_dir.c

Connects directory block lists to directory entry iteration. `ext2fs_dblist_dir_iterate` walks a dblist and invokes a directory-entry callback for each directory block.

Behavior:
- Builds a `struct dir_context` with flags, buffer, callback, private data, and error field.
- Uses caller-supplied block buffer or allocates one filesystem block.
- Calls `ext2fs_dblist_iterate2` with `db_dir_proc`.
- `db_dir_proc` reads the directory inode, chooses inline-data iteration for `EXT4_INLINE_DATA_FL`, otherwise calls `ext2fs_process_dir_block`.

Dependencies: dblist APIs, inode read, directory iteration internals, inline data directory iterator.

Implementation notes:
- `ctx->dir` is updated for each dblist entry.
- If `ext2fs_process_dir_block` returns `BLOCK_ABORT` without setting `ctx->errcode`, dblist iteration aborts.
- The function returns `ctx.errcode` after successful dblist traversal.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dblist_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/digest_encode.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/digest_encode.c

Implements filename-safe digest encoding and decoding using a custom 64-character alphabet: uppercase letters, lowercase letters, digits, plus, and comma.

APIs:
- `ext2fs_digest_encode(const char *src, int len, char *dst)`
- `ext2fs_digest_decode(const char *src, int len, char *dst)`

Encoding packs input bytes into a little-endian bit accumulator and emits 6-bit symbols. Decoding reverses that process by finding each source character in the lookup table and emitting bytes whenever at least 8 bits are available.

Behavior:
- Encoded output is roughly 4/3 the input length.
- Decode returns `-1` for invalid characters or leftover nonzero accumulator bits.
- Functions return the number of bytes written and do not append a NUL terminator themselves.

Unit-test code under `UNITTEST` includes known digest vectors and command-line encode/decode helpers.

Implementation notes:
- The comment says `[a-zA-Z0-9_+]`, but the actual alphabet uses `+,` and no underscore.
- Decode uses `strchr`, making it simple but not constant-time.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/digest_encode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dir_iterate.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dir_iterate.c

Implements directory entry iteration and directory record length encoding helpers. The main API is `ext2fs_dir_iterate2`; `ext2fs_dir_iterate` is a legacy callback wrapper.

Record length helpers:
- `ext2fs_get_rec_len` decodes `dirent->rec_len`, including ext4 encodings for block sizes >= 64 KiB.
- `ext2fs_set_rec_len` validates and encodes record lengths, rejecting misaligned or oversized values.

Iteration behavior:
- `ext2fs_dir_iterate2` validates the inode as a directory, prepares a `dir_context`, and runs `ext2fs_block_iterate3` in read-only mode with `ext2fs_process_dir_block`.
- Inline-data directories are handled by `ext2fs_inline_data_dir_iterate` when block iteration reports inline data.
- `ext2fs_process_dir_block` reads a directory block, verifies record structure, invokes the callback, tracks changed entries, and writes back changed blocks.
- It can include empty, removed, checksum, or inline-data entries based on flags.
- Deleted-entry detection uses `ext2fs_validate_entry` to inspect slack space for plausible removed entries.

Error handling:
- Corrupt record lengths, bad name lengths, or out-of-block records set `EXT2_ET_DIR_CORRUPTED`.
- Changed inline data returns `BLOCK_INLINE_DATA_CHANGED` to notify the inline-data caller.
- Callback `DIRENT_ABORT` stops processing.

Dependencies: block iterator, directory block read/write, metadata checksum support, inline data support.

Implementation notes:
- Checksum tail entries are normally skipped unless `DIRENT_FLAG_INCLUDE_CSUM` is set.
- The iterator distinguishes dot, dotdot, and other entries using entry ordinal state.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dir_iterate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dirblock.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dirblock.c

Provides directory block read/write wrappers with checksum verification/set and endian swapping. The primary APIs are `ext2fs_read_dir_block4` and `ext2fs_write_dir_block4`; older 3/2/no-suffix variants wrap them.

Read behavior:
- Reads one block via `io_channel_read_blk64`.
- Verifies directory block checksum unless `EXT2_FLAG_IGNORE_CSUM_ERRORS` is set.
- On big-endian builds, swabs directory entries into host order.
- Returns `EXT2_ET_DIR_CSUM_INVALID` if checksum verification failed and no read/swap error occurred.

Write behavior:
- On big-endian builds, copies the input buffer and swabs directory entries out.
- Sets directory block checksum with `ext2fs_dir_block_csum_set`.
- Writes one block via `io_channel_write_blk64`.

Implementation notes:
- The 3/2/legacy variants pass inode zero, which limits checksum contexts for callers that do not know the inode.
- Big-endian error paths rely on freeing the temporary buffer after checksum/write handling.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dirblock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dirhash.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dirhash.c

Implements ext2/ext4 directory filename hashing for htree indexes. It supports legacy, half-MD4, and TEA hash variants, with signed and unsigned character modes.

Core helpers:
- `TEA_transform`: keyed 32-bit TEA-based Davis-Meyer transform.
- `halfMD4Transform`: cut-down MD4 transform returning hash state.
- `dx_hack_hash`: old legacy directory hash.
- `str2hashbuf`: packs filename bytes into 32-bit words with length-based padding.

APIs:
- `ext2fs_dirhash`: hashes raw filename bytes with optional seed.
- `ext2fs_dirhash2`: optionally casefolds/normalizes through an `ext2fs_nls_table` before calling `ext2fs_dirhash`.

Behavior:
- All-zero seed uses the default MD4 initialization constants.
- Unsupported hash versions return `EXT2_ET_DIRHASH_UNSUPP`.
- Returned primary hash has its low bit cleared.
- Minor hash is returned for hash versions that produce one.
- `ext2fs_dirhash2` falls back to opaque byte hashing if casefolding returns `-EINVAL`.

Implementation notes:
- Casefolding uses a fixed `PATH_MAX` stack buffer.
- The function itself does not perform normalization unless `ext2fs_dirhash2` is used with charset and `EXT4_CASEFOLD_FL`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dirhash.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dosio.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dosio.c

Implements a legacy DOS BIOS-backed libext2fs I/O manager. It exposes `dos_io_manager`, whose methods open DOS-accessible Linux-style device names, read and write sectors through BIOS INT 13h style calls, and close channels.

Core components:
- Global error state: `_dio_error`, `_dio_hw_error`.
- Cached partition table: `partitions`, `npart`, `active`.
- I/O manager methods: `dos_open`, `dos_close`, `dos_set_blksize`, `dos_read_blk`, `dos_write_blk`, `dos_flush`.
- Address conversion: `lba2chs`.
- Partition scanning: `scan_partition_table`.
- Channel allocation: `alloc_io_channel`.

Open behavior:
- Accepts paths under `/dev`, with `hd`, `sd`, or `fd` style names.
- Maps hard disk letters to BIOS physical drives starting at `0x80`.
- Does not support floppy access despite parsing `fd`.
- Reads drive geometry, reads MBR sector, scans for Linux ext2 partition type `0x83`, and rejects Linux swap type `0x82`.
- Caches partition metadata and returns a libext2fs `io_channel`.

Read/write behavior:
- Converts block number and channel block size into byte offset, then CHS.
- Uses `biosdisk` read/write commands.
- Negative `count` means byte count rather than block count, matching libext2fs IO convention.
- `dos_flush` is a no-op because there is no buffering.

Implementation notes:
- The source mutates the `dev` string temporarily despite receiving `const char *`, which is unsafe if passed immutable storage.
- `realloc(partitions, sizeof(PARTITION) * npart)` appears to size by struct rather than pointer and does not allocate room for the new entry when `npart` is current count.
- Extended partitions are explicitly unsupported for partition numbers >= 5, despite the header comment claiming extended traversal.
- The file is platform-specific and depends on DOS headers such as `<bios.h>` and `<io.h>`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dosio.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dosio.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dosio.h

Declares legacy DOS disk I/O structures, constants, error globals, and helper macros for the DOS libext2fs I/O manager.

Key structures:
- `CHS`: cylinder/head/sector plus byte offset.
- `PARTITION`: Linux-style device name, BIOS drive number, LBA start, sector length, partition number, and geometry.
- `PTABLE_ENTRY`: packed PC partition table entry.

Constants:
- BIOS operation codes: read, write, get geometry, ready.
- Module error codes: bad device, hardware, unsupported, not ext2fs, empty partition, Linux swap.
- Hardware status macros such as `HW_OK`, `HW_WRITE_PROT`, `HW_NO_SECTOR`, and others.

Exports:
- `_dio_error`
- `_dio_hw_error`
- `open_partition(char *dev)`

Implementation notes:
- The header requires Turbo C large memory model when `__TURBOC__` is defined.
- The documented `open_partition` behavior claims extended partition traversal, but `dosio.c` does not implement it.
- `open_partition` is declared here but not implemented in the paired `dosio.c` shown in this group.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dosio.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dupfs.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dupfs.c

Implements `ext2fs_dup_handle`, which duplicates an `ext2_filsys` handle while deep-copying owned filesystem metadata and sharing reference-counted IO/cache state.

Duplication behavior:
- Allocates a new `struct_ext2_filsys` and shallow-copies the source.
- Clears pointers that must be independently allocated.
- Bumps IO channel reference count.
- Increments inode cache refcount when present.
- Deep-copies device name, superblock, original superblock, group descriptors, inode bitmap, block bitmap, badblocks list, dblist, MMP buffers, and MMP comparison buffer.
- Duplicates `mmp_fd` with `dup` when present.

Error handling:
- On any allocation/copy failure, calls `ext2fs_free` on the partially built handle and returns the error.
- Returns `EXT2_ET_MMP_OPEN_DIRECT` if duplicating the MMP file descriptor fails.

Implementation notes:
- The duplicate shares the same `io_channel` after bumping its count.
- `mmp_fd` is reset to `-1` before optional duplication so cleanup can distinguish ownership.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/dupfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/e2image.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/e2image.h

Defines `struct ext2_image_hdr`, the on-disk/header format for e2image output.

Fields capture:
- Magic number and descriptor string.
- Source filesystem host/network/device identity.
- Filesystem UUID and block size.
- Image file device, inode, and creation time low/high words.
- Offsets to superblock/descriptors, inode table data, inode bitmap data, and block bitmap data.
- Reserved fields for future extension.

Implementation notes:
- The comment notes this format uses POSIX IO interfaces unlike most libext2fs code.
- The header contains only the structure definition and no functions.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/e2image.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/expanddir.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/expanddir.c

Implements `ext2fs_expand_dir`, which grows a directory by one block. It uses block iteration in append mode to find or create a hole, allocate a new block, initialize it, update inode size, and update block counts.

Callback behavior in `expand_dir_proc`:
- Existing blocks update the allocation goal.
- Empty block slots allocate a new block near the goal, respecting bigalloc cluster placement when possible.
- For logical block zero, it zeroes the new block.
- For later blocks, it creates a new empty directory block with `ext2fs_new_dir_block` and writes it with `ext2fs_write_dir_block4`.
- Marks block allocation stats and returns `BLOCK_CHANGED`, aborting once a usable directory block is added.

Top-level validation:
- Requires a read-write filesystem.
- Requires a block bitmap.
- Verifies the inode is a directory.
- Handles inline-data directories by delegating to `ext2fs_inline_data_expand`.

Post-update behavior:
- Re-reads the inode.
- Increases inode size by one filesystem block via `ext2fs_inode_size_set`.
- Adds allocated block count with `ext2fs_iblk_add_blocks`.
- Writes the inode.

Implementation notes:
- `es.newblocks` tracks newly allocated clusters/blocks for inode accounting.
- If append iteration does not add a directory block, returns `EXT2_ET_EXPAND_DIR_ERR`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/expanddir.c -->