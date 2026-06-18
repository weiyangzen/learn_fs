# Group Research: group_1876_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_bmap_c_sources_local__2e4db75d4c51

Scope: `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bmap.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bmap.c

## Purpose

`xfs_bmap.c` is the core XFS block mapping implementation in `libxfs`. It manages logical file block to physical filesystem block mappings for inode forks, including data, attribute, and CoW forks. It covers reading mappings, allocating blocks, converting delayed allocations, converting unwritten extents, unmapping extents, remapping shared extents, shifting extents for collapse/insert range, splitting extents, and maintaining the extent-list versus bmap-btree fork formats.

This file is central to XFS metadata mutation. It updates incore extent maps, on-disk bmap btrees, inode block/extents accounting, quota counters, reverse mappings, refcount/reflink state, realtime metadata, and deferred bmap intents.

## Main Concepts

- XFS inode forks can store mappings in local, extent, or btree format.
- Real extents map file offsets to filesystem blocks.
- Delayed allocation extents use null startblocks that encode reserved indirect-block counts.
- Holes are represented externally with `HOLESTARTBLOCK`.
- Unwritten extents reserve disk blocks without exposing initialized file data as written.
- CoW fork extents are incore-only until remapped to the data fork.
- Bmap btrees are used when extent count exceeds inode inline extent capacity.
- Reverse mappings and refcount btrees are maintained alongside map changes.

## Key Data Flows

### Mapping Reads

`xfs_bmapi_read` validates fork format, loads btree extents into the incore map via `xfs_iread_extents`, walks the extent tree from the requested logical offset, synthesizes holes, trims returned records to the caller range, and coalesces adjacent returned mappings when possible.

Important helpers:

- `xfs_trim_extent`
- `xfs_bmapi_trim_map`
- `xfs_bmapi_update_map`
- `xfs_bmap_validate_ret` in debug builds

### Mapping Writes and Allocation

`xfs_bmapi_write` is the main allocation/conversion path. It walks existing mappings, decides whether a hole or delayed allocation requires real allocation, calls `xfs_bmapi_allocate`, optionally converts unwritten extents, and returns the resulting mappings.

Important helpers:

- `xfs_bmapi_allocate`
- `xfs_bmap_btalloc`
- `xfs_bmap_rtalloc` through external realtime allocation integration
- `xfs_bmap_add_extent_delay_real`
- `xfs_bmap_add_extent_hole_real`
- `xfs_bmap_add_extent_unwritten_real`
- `xfs_bmapi_convert_unwritten`
- `xfs_bmapi_finish`

Allocation chooses placement using:

- EOF and adjacent extent heuristics
- stripe alignment
- extent size hints
- CoW extent size hints
- filestream AG selection
- low-space fallback allocation
- realtime inode handling
- debug error tag forcing for minimum-length allocation

### Delayed Allocation Conversion

`xfs_bmapi_convert_delalloc` loops around `xfs_bmapi_convert_one_delalloc` until the returned iomap covers the requested byte offset. It converts an existing delayed allocation extent into real blocks, usually allocating from the start of the delalloc extent to create larger contiguous disk extents.

For page-cache writeback safety, data fork delayed allocations are allocated as unwritten extents first, then converted after I/O succeeds. CoW fork allocations are also initially unwritten and later remapped.

### Unmapping

`xfs_bunmapi` wraps `__xfs_bunmapi`, which walks mappings backwards over a requested range. It handles real extents, delayed extents, realtime alignment constraints, unwritten conversion for partial realtime extents, and btree-to-extents conversion after deletions.

Important helpers:

- `xfs_bmap_del_extent_real`
- `xfs_bmap_del_extent_delay`
- `xfs_bmap_del_extent_cow`
- `xfs_bmap_free_rtblocks`
- `xfs_bunmapi_range`

`xfs_bmap_del_extent_real` updates the incore extent list and optional bmap btree, removes rmaps, frees or refcount-decrements blocks, adjusts inode block counts, and updates quota counters.

### Remapping

`xfs_bmapi_remap` inserts an existing physical extent into a hole without normal allocation accounting. It is used by deferred bmap operations and reflink/remap flows. It asserts that the target range is a hole, updates inode accounting, inserts the extent, and performs any necessary btree-to-extents conversion.

### Extent Shifting and Splitting

The file implements higher-level file offset transformations:

- `xfs_bmap_collapse_extents` shifts extents left to fill a hole.
- `xfs_bmap_insert_extents` shifts extents right to create a hole.
- `xfs_bmap_can_insert_extents` checks for file offset overflow before right shifting.
- `xfs_bmap_split_extent` splits a real extent at a requested file offset.

Shift operations update bmap records and reverse mappings. Collapse can merge adjacent extents when shifted extents become contiguous.

### Fork Format Conversion

The file handles transitions among local, extent, and btree fork formats:

- `xfs_bmap_local_to_extents_empty`
- `xfs_bmap_local_to_extents`
- `xfs_bmap_extents_to_btree`
- `xfs_bmap_btree_to_extents`
- `xfs_bmap_add_attrfork`
- `xfs_bmap_add_attrfork_local`
- `xfs_bmap_add_attrfork_extents`
- `xfs_bmap_add_attrfork_btree`

`xfs_bmap_needs_btree` decides when extent format must become btree format. `xfs_bmap_wants_extents` decides when a small btree can collapse back to extent format.

### Btree Extent Loading

`xfs_iread_extents` loads records from a btree-format fork into the incore extent cache. It uses `xfs_btree_visit_blocks` and `xfs_iread_bmbt_block`, validates each record, inserts it into the incore extent map, and clears `if_needextents` with release semantics.

If loading fails, the fork extent cache is destroyed and the fork is marked sick when appropriate.

### Deferred Bmap Intents

The file defines and processes deferred mapping operations:

- `xfs_bmap_map_extent`
- `xfs_bmap_unmap_extent`
- `xfs_bmap_finish_one`
- `xfs_bmap_intent_init_cache`
- `xfs_bmap_intent_destroy_cache`

Deferred intents skip holes, delayed allocations, and unsupported forks. Finish processing remaps or unmaps one extent at a time.

## Important Validation and Integrity Checks

The code aggressively validates metadata state:

- `xfs_bmap_validate_extent_raw` verifies file extent ranges, physical block ranges, realtime ranges, and unwritten-state restrictions.
- `xfs_bmap_validate_extent` applies inode context.
- `xfs_bmap_complain_bad_rec` emits detailed corruption warnings.
- Debug-only btree leaf checks verify ordering and duplicate child pointers.
- Many paths mark bmap btrees or forks sick on corruption.
- Shutdown state returns `-EIO`.
- Error tags can force corruption or allocation behavior in debug/test builds.

## Accounting Responsibilities

Allocation, conversion, and deletion paths update:

- `ip->i_nblocks`
- `ip->i_delayed_blks`
- fork extent counts
- delayed allocation global counters
- free data blocks
- free realtime extents
- quota block or realtime block counters
- transaction inode logging flags
- btree cursor allocated-block counters
- reverse map and refcount side structures

`xfs_bmap_alloc_account` centralizes much of the post-allocation inode/quota accounting, with special treatment for CoW fork allocations.

## Dependencies and Collaborators

Major collaborators include:

- `xfs_bmap_btree.c` and `xfs_bmap_btree.h` for bmap btree operations.
- `xfs_iext_*` incore extent list APIs.
- `xfs_alloc_*` allocation APIs.
- `xfs_rmap_*` reverse mapping updates.
- `xfs_refcount_*` reflink and CoW accounting.
- `xfs_rtbitmap`, `xfs_rtgroup`, and realtime allocation/free logic.
- transaction and quota code.
- directory and symlink conversion helpers for local-to-remote fork conversion.
- `iomap` for writeback mapping returns.

## Notable Invariants

- CoW fork does not use bmap btree format conversion here.
- Attribute fork cannot carry unwritten extents.
- Returned maps from `xfs_bmapi_read/write` must be ordered and contiguous in returned logical range.
- Real extent merges require logical contiguity, physical contiguity, matching state, max length limits, and realtime group compatibility.
- Delayed allocation records carry indirect reservation state in the encoded null startblock.
- Btree mutations are mirrored in the incore extent cache.
- Reverse mappings must be removed and re-added when file offsets shift.
- Realtime extents often cannot be partially freed unless aligned to realtime extent boundaries.

## Research Notes

This file is the behavioral hub for XFS extent mapping. The most important maintenance risk is that each mapping mutation has several synchronized side effects: incore extents, btree records, inode counters, quota, reverse mapping, refcount/reflink state, realtime metadata, and transaction logging must remain consistent. The many switch statements over left/right fill and contiguity states encode the extent merge/split matrix and are the highest-density correctness logic in the file.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bmap.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bmap.h

## Purpose

`xfs_bmap.h` declares the public block mapping interface used by `libxfs` and other XFS subsystems. It defines allocation argument state, bmapi flags, special extent startblock values, extent update state flags, deferred bmap intent structures, validation helpers, and prototypes for mapping, unmapping, remapping, conversion, and query operations.

## Main Types

### `struct xfs_bmalloca`

This is the central allocation work structure passed through bmap allocation helpers. It carries:

- transaction and inode
- previous and current/next extent records
- requested logical offset and length
- allocated block number
- optional btree cursor and incore extent cursor
- number of allocations performed
- inode logging flags
- total/minimum allocation constraints
- EOF and allocation-mode booleans
- allocation datatype
- bmapi flags

This structure ties allocation placement, extent insertion, accounting, and btree updates together.

### `struct xfs_bmap_intent`

Represents a deferred bmap operation. It records:

- intent list linkage
- map or unmap type
- target fork
- owning inode
- optional group pointer
- extent record to map or unmap

Deferred intents are consumed by `xfs_bmap_finish_one`.

## Flags

### `XFS_BMAPI_*`

These flags control read/write/remap/unmap behavior:

- `XFS_BMAPI_ENTIRE`: return entire extents instead of trimming.
- `XFS_BMAPI_METADATA`: map metadata rather than user data.
- `XFS_BMAPI_ATTRFORK`: operate on attr fork.
- `XFS_BMAPI_PREALLOC`: allocate unwritten preallocation.
- `XFS_BMAPI_CONTIG`: require a single contiguous extent.
- `XFS_BMAPI_CONVERT`: convert written/unwritten state.
- `XFS_BMAPI_ZERO`: zero allocated or converted data extents.
- `XFS_BMAPI_REMAP`: map/unmap without ordinary block/refcount/quota changes.
- `XFS_BMAPI_COWFORK`: operate on CoW fork.
- `XFS_BMAPI_NODISCARD`: skip online discard for freed extents.
- `XFS_BMAPI_NORMAP`: skip reverse map updates.
- `XFS_BMAPI_EXTSZALIGN`: try extent-size-hint alignment.

Inline helpers map between flags and fork identifiers:

- `xfs_bmapi_aflag`
- `xfs_bmapi_whichfork`

### Special Startblocks

- `DELAYSTARTBLOCK`: externally visible delayed allocation marker.
- `HOLESTARTBLOCK`: externally visible hole marker.

### `BMAP_*` State Flags

These describe neighboring extent state during add/delete/convert operations:

- left/right contiguity
- left/right fill of an old extent
- left/right delayed allocation
- left/right neighbor validity
- attribute fork
- CoW fork

They are used internally to drive merge/split case analysis.

## Inline Extent Predicates

- `xfs_bmap_is_real_extent`: true for allocated physical extents.
- `xfs_bmap_is_written_extent`: true for allocated non-unwritten extents.
- `xfs_valid_startblock`: rejects block zero except for realtime inodes.

## Public Operations

The header exposes:

- attribute fork creation and local-to-extent conversion
- maximum btree level computation
- first/last extent offset lookup
- mapping read and write
- unmap and unmap range
- delayed allocation and CoW deletion helpers
- collapse/insert range support
- split extent support
- delayed allocation conversion to iomap
- unwritten extent conversion
- min-left reservation calculation
- low-space allocation helper
- remap helper
- deferred map/unmap operations
- bmap btree query helper
- extent-size hint accessors

## Validation Interface

The header declares:

- `xfs_bmap_validate_extent_raw`
- `xfs_bmap_validate_extent`
- `xfs_bmap_complain_bad_rec`

These are used when reading btree records and when external code needs to validate mapping records.

## Research Notes

This header defines the control surface for XFS block mapping. The flags are especially important because many operations share the same underlying mutation machinery but differ sharply in accounting and side effects. `XFS_BMAPI_REMAP`, `XFS_BMAPI_COWFORK`, and `XFS_BMAPI_NORMAP` are the most semantically sensitive flags because they intentionally bypass or redirect normal ownership/accounting behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bmap_btree.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bmap_btree.c

## Purpose

`xfs_bmap_btree.c` implements the bmap btree-specific adapter for XFS generic btree code. It handles bmap btree block initialization, root conversion between dinode and incore formats, packed extent record encode/decode, btree cursor allocation, block allocation/free callbacks, record/key comparison, verifier operations, root reallocation, staged btree commit, owner changes, btree size calculation, and cursor cache lifecycle.

## Btree Block Initialization

`xfs_bmbt_init_block` initializes either a buffer-backed btree block or an incore block using `xfs_btree_init_buf` or `xfs_btree_init_block`. The inode number is supplied as the owner for bmap btree blocks.

## Root Format Conversion

Bmap btree roots live inside inode forks in a compact on-disk `xfs_bmdr_block` layout, but are manipulated incore as normal btree blocks.

- `xfs_bmdr_to_bmbt` converts dinode root format to incore btree root format.
- `xfs_bmbt_to_bmdr` converts incore btree root format back to dinode root format.

The conversion copies level, record count, keys, and pointers. CRC filesystems verify magic, uuid, null block number, and null siblings before converting back.

## Packed Extent Records

Bmap extent records are stored as two big-endian 64-bit words.

- `xfs_bmbt_disk_get_all` unpacks start offset, start block, block count, and unwritten state.
- `xfs_bmbt_disk_get_blockcount` extracts block count.
- `xfs_bmbt_disk_get_startoff` extracts logical start offset.
- `xfs_bmbt_disk_set_all` packs an incore `xfs_bmbt_irec` into disk format.

The packed layout stores:

- one high-bit unwritten flag
- logical file offset
- physical start block
- block count

Assertions ensure fields fit their on-disk bit widths and state is either normal or unwritten.

## Generic Btree Operations

The file defines `xfs_bmbt_ops`, an `xfs_btree_ops` instance for bmap btrees. It supplies:

- cursor duplication and update
- block allocation and free
- max/min record calculations
- dmax record calculation for inode-root capacity
- key initialization from records
- high-key initialization
- record initialization from cursor
- key comparison
- buffer verifier operations
- key/record ordering predicates
- key contiguity predicate
- inode root reallocation callback

This is the bridge between generic btree algorithms and bmap-specific record semantics.

## Block Allocation and Freeing

`xfs_bmbt_alloc_block` allocates one filesystem block for a bmap btree split. It sets rmap owner info for inode bmbt ownership, respects delayed allocation context through `XFS_BTREE_BMBT_WASDEL`, handles no-reservation cases, uses `minleft` when no AG has been selected yet, and can fall back to low-space mode. On success it increments cursor allocation count, inode block count, logs inode core, and updates quota.

`xfs_bmbt_free_block` schedules a bmap btree block for deferred freeing, decrements inode block count, logs inode core, and updates quota.

## Record Capacity

Capacity helpers include:

- `xfs_bmbt_get_minrecs`
- `xfs_bmbt_get_maxrecs`
- `xfs_bmbt_get_dmaxrecs`
- `xfs_bmbt_maxrecs`
- `xfs_bmdr_maxrecs`
- `xfs_bmbt_maxlevels_ondisk`
- `xfs_bmbt_calc_size`

Root capacity depends on inode fork space, while non-root block capacity depends on filesystem block size and btree block header size. CRC-enabled filesystems use larger btree headers.

## Verification

The buffer ops `xfs_bmbt_buf_ops` provide read/write/struct verification for bmap btree blocks.

`xfs_bmbt_verify` checks:

- btree magic
- CRC header fields when applicable
- level bounded by maximum data/attr bmap levels
- generic fsblock btree structure and record count

Read verification also checks CRC; write verification recalculates CRC after structural validation.

## Root Reallocation

`xfs_bmap_broot_realloc` resizes the incore inode btree root buffer based on target record count. It handles:

- freeing the root when record count becomes zero
- initial allocation
- growth by moving pointer arrays to their new offset
- shrink by moving pointer arrays before reallocating

Bmap root records are packed after the header, while pointers live after the key array, so pointer movement is required whenever root capacity changes.

## Cursor Lifecycle

`xfs_bmbt_init_cursor` allocates a generic btree cursor configured for bmap btrees. It rejects CoW fork cursors, supports staging cursors, initializes maximum levels, stores inode/fork context, and derives current btree level count from the fork root.

`xfs_bmbt_init_cur_cache` and `xfs_bmbt_destroy_cur_cache` manage the slab cache for bmap btree cursors sized to the maximum possible on-disk level count.

## Staged Btree Commit

`xfs_bmbt_commit_staged_btree` replaces a real inode fork with a staged fake-root fork after rebuilding mappings. It destroys the old fork resources, shallow-copies the staged fork, logs the correct inode fields based on extent or btree format, and commits staged btree blocks.

## Owner Changes

`xfs_bmbt_change_owner` walks a btree-format fork to change btree block owner metadata. It supports either transactional modification or recovery-style buffer-list output, but not both simultaneously.

## Research Notes

This file is intentionally narrow: it does not decide mapping policy, but it makes generic btree machinery understand XFS bmap records. The most important correctness surfaces are packed record encoding, root reallocation pointer movement, block allocation accounting, and verifier strictness.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bmap_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bmap_btree.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bmap_btree.h

## Purpose

`xfs_bmap_btree.h` declares the bmap btree interface and defines inline layout helpers for bmap btree records, keys, pointers, inode-root sizing, and btree root reallocation. It is the companion API used by `xfs_bmap.c` and generic btree code to manipulate XFS inode block mapping btrees.

## Main Definitions

- `XFS_BM_MAXLEVELS(mp,w)` returns the computed maximum bmap btree depth for a fork.
- Prototypes cover root conversion, record packing/unpacking, capacity calculation, owner changes, cursor creation, staged-tree commit, btree size calculation, cache lifecycle, and block initialization.

## Record Packing API

The header declares:

- `xfs_bmbt_disk_set_all`
- `xfs_bmbt_disk_get_blockcount`
- `xfs_bmbt_disk_get_startoff`
- `xfs_bmbt_disk_get_all`

These convert between incore extent records and the compact disk record format.

## Capacity API

The header declares and defines helpers for record capacity:

- `xfs_bmbt_get_maxrecs`
- `xfs_bmdr_maxrecs`
- `xfs_bmbt_maxrecs`
- `xfs_bmbt_maxlevels_ondisk`
- `xfs_bmbt_calc_size`

These are used to size bmap btree blocks, inode roots, and cursor caches.

## Layout Helpers

The file provides inline address calculators for incore and ondisk bmap btree layouts:

- `xfs_bmbt_block_len` returns CRC or non-CRC btree block header length.
- `xfs_bmbt_rec_addr` locates records in a btree block.
- `xfs_bmbt_key_addr` locates keys in a btree block.
- `xfs_bmbt_ptr_addr` locates pointers in a btree block.
- `xfs_bmdr_rec_addr` locates records in an inode-root disk layout.
- `xfs_bmdr_key_addr` locates keys in an inode-root disk layout.
- `xfs_bmdr_ptr_addr` locates pointers in an inode-root disk layout.
- `xfs_bmap_broot_ptr_addr` locates pointers in an incore inode root when only root size is known.

The layout model is header first, then records for leaf blocks, or keys followed by pointers for internal/root blocks.

## Root Sizing Helpers

- `xfs_bmap_broot_space_calc` computes incore root bytes for a given record count.
- `xfs_bmap_broot_space` computes incore root space from an ondisk bmdr root.
- `xfs_bmdr_space_calc` computes ondisk inode-root bytes for a record count.
- `xfs_bmap_bmdr_space` computes ondisk space from an incore root.

These helpers are used when converting fork format and checking whether a btree root fits in an inode fork.

## Mutable Root API

`xfs_bmap_broot_realloc` resizes an inode fork's incore bmap btree root to a requested number of records. It is implemented in `xfs_bmap_btree.c` and used by both format conversion and generic btree split/shrink operations.

## Research Notes

This header is mostly structural, but it encodes important disk and memory layout assumptions. Any changes to btree block headers, bmap record size, key size, pointer size, or inode fork sizing must remain consistent with these address and space calculations.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_bmap_btree.h -->