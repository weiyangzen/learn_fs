# Group Research: group_855_linux_sources_os_linux_linux_fs_xfs_libxfs_xfs_bmap_c_sources_os_lin_295f155c2972

Scope: `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap.c

## Purpose

`xfs_bmap.c` is the main XFS inode block mapping implementation. It translates file-relative block offsets to filesystem blocks, allocates and frees mapped extents, converts delayed allocation and unwritten extents, maintains inode fork extent state, and coordinates those changes with bmap btrees, reverse mappings, refcount/reflink, quotas, realtime allocation, zoned realtime accounting, transaction logging, and deferred bmap intents.

This file is the behavioral center of XFS extent mapping. Almost every metadata-changing mapping operation must keep the in-core extent tree, optional bmap btree, inode counters, quota reservations, rmap/refcount state, free-space accounting, and transaction log flags synchronized.

## Major Responsibilities

- Compute maximum bmap btree levels and default attribute fork offsets.
- Convert inode forks between local, extent, and btree formats.
- Load btree-format fork extents into the in-core extent cache.
- Query first unused logical blocks, last mapped blocks, and last extents.
- Read mappings without allocation via `xfs_bmapi_read`.
- Allocate or convert mappings via `xfs_bmapi_write`.
- Convert delayed allocation extents for writeback via `xfs_bmapi_convert_delalloc`.
- Insert remapped extents into holes via `xfs_bmapi_remap`.
- Remove extents via `xfs_bunmapi` and `xfs_bunmapi_range`.
- Delete/split delayed, CoW, and real extents.
- Shift and split extents for collapse range, insert range, and extent splitting.
- Record and finish deferred bmap map/unmap intents.
- Validate extent records and expose btree query helpers.
- Calculate data and CoW extent size hints.

## Key Data Flows

### Fork Format Conversion

The file handles transitions among inode fork formats:

- `xfs_bmap_local_to_extents_empty`
- `xfs_bmap_local_to_extents`
- `xfs_bmap_extents_to_btree`
- `xfs_bmap_btree_to_extents`
- `xfs_bmap_add_attrfork`
- `xfs_bmap_add_attrfork_local`
- `xfs_bmap_add_attrfork_extents`
- `xfs_bmap_add_attrfork_btree`

`xfs_bmap_needs_btree` decides when a non-CoW extent-format fork exceeds inline capacity and must become btree format. `xfs_bmap_wants_extents` decides when a shallow btree can collapse back to extent format.

Conversion is not just a representation change. It allocates or frees bmap btree blocks, adjusts `i_nblocks`, updates quota, initializes or destroys inode-root btree data, and logs the correct inode fork fields.

### Extent Cache Loading

`xfs_iread_extents` loads btree-format fork records into the in-core extent cache. It initializes a bmap btree cursor, visits record blocks through the generic btree layer, decodes each `xfs_bmbt_rec`, validates it with `xfs_bmap_validate_extent`, inserts it into the in-core extent tree, and clears `if_needextents` with release semantics.

If loading fails, the extent cache is destroyed and the fork is marked sick when corruption-like errors are detected.

### Mapping Reads

`xfs_bmapi_read` maps logical file blocks without allocating storage. It validates fork state, loads btree extents if needed, walks the in-core extent tree from the requested offset, synthesizes hole mappings, trims records to the caller range unless `XFS_BMAPI_ENTIRE` is set, and coalesces adjacent returned mappings where possible.

Important helpers:

- `xfs_trim_extent`
- `xfs_bmapi_trim_map`
- `xfs_bmapi_update_map`
- `xfs_bmap_validate_ret` in debug builds

Returned mappings use `HOLESTARTBLOCK` for holes and `DELAYSTARTBLOCK` for delayed allocation records.

### Mapping Writes and Allocation

`xfs_bmapi_write` is the primary write mapping path. It walks existing mappings over the requested logical range, decides whether a hole or delayed allocation requires physical allocation, calls `xfs_bmapi_allocate`, optionally converts unwritten extents, records mappings to return to the caller, and finally collapses btree forks back to extent format if possible.

Key helpers:

- `xfs_bmapi_allocate`
- `xfs_bmap_btalloc`
- `xfs_bmap_rtalloc` through realtime allocation integration
- `xfs_bmap_add_extent_delay_real`
- `xfs_bmap_add_extent_hole_real`
- `xfs_bmap_add_extent_unwritten_real`
- `xfs_bmapi_convert_unwritten`
- `xfs_bmapi_finish`

Allocation selection considers EOF placement, adjacent extents, stripe alignment, extent size hints, CoW extent size hints, filestream AG selection, low-space fallback, realtime inodes, and debug minlen error injection.

### Delayed Allocation Conversion

`xfs_bmapi_convert_delalloc` repeatedly calls `xfs_bmapi_convert_one_delalloc` until the returned iomap covers the requested byte offset. Conversion intentionally starts at the beginning of the current delayed allocation extent to encourage large contiguous physical extents.

For writeback safety, data fork delayed allocations are allocated as unwritten extents and later converted after I/O succeeds. CoW fork allocations are also created unwritten and later remapped to the data fork.

### Extent State Machines

The densest correctness logic is in the add/convert/delete extent helpers. They compute state bits such as left/right fill, left/right contiguity, delayed neighbors, and fork type, then execute a case matrix that updates both the in-core extent list and optional bmap btree.

Important cases include:

- delayed allocation to real extent
- hole to real extent
- unwritten to written conversion
- written to unwritten conversion
- full deletion
- deletion from the left or right edge
- deletion from the middle, which splits one extent into two
- three-way merges when both neighbors are contiguous

Merges require logical adjacency, physical adjacency, matching extent state, maximum bmap extent length limits, and compatible realtime group placement.

### Unmapping

`xfs_bunmapi` wraps `__xfs_bunmapi`, which walks mappings backwards over the requested range. It removes delayed, CoW, and real extents differently and handles realtime alignment restrictions specially. Partial realtime extent deletion may convert written ranges to unwritten rather than freeing sub-realtime-extent fragments.

Key helpers:

- `xfs_bmap_del_extent_delay`
- `xfs_bmap_del_extent_cow`
- `xfs_bmap_del_extent_real`
- `xfs_bmap_free_rtblocks`
- `xfs_bunmapi_range`

`xfs_bmap_del_extent_real` removes rmaps, decreases refcounts for reflinked data fork extents, frees normal or realtime extents, applies no-discard flags for unwritten extents or explicit `NODISCARD`, adjusts `i_nblocks`, and updates quota unless the operation is a remap-only unmap.

Mainline-specific realtime behavior includes routing realtime frees through deferred free intents when rtgroups support rmap/refcount ordering, while legacy realtime frees still use `xfs_rtfree_blocks`.

### Remapping

`xfs_bmapi_remap` inserts an existing physical extent into a hole, primarily for reflink/remap and deferred bmap intent processing. It asserts that the destination range is a hole, adjusts inode block and delayed-block accounting, optionally creates an unwritten extent, inserts the mapping through the normal hole-to-real helper, and performs btree-to-extents conversion if possible.

`XFS_BMAPI_NORMAP` allows reconstruction paths to skip rmap updates.

### Extent Shifting and Splitting

The file supports higher-level file offset transformations:

- `xfs_bmap_collapse_extents` shifts extents left to fill a removed range.
- `xfs_bmap_insert_extents` shifts extents right to create a hole.
- `xfs_bmap_can_insert_extents` checks for file offset overflow before right shifting.
- `xfs_bmap_split_extent` splits one real extent into two at a file offset.

Shift operations update both bmap records and reverse mappings. Left shifts can merge with the preceding extent when logical and physical adjacency allow it. Right shifts warn if they encounter extents that would have been mergeable because insert-range should not create that condition.

### Deferred Bmap Intents

The file defines and processes deferred mapping operations:

- `xfs_bmap_map_extent`
- `xfs_bmap_unmap_extent`
- `xfs_bmap_finish_one`
- `xfs_bmap_intent_init_cache`
- `xfs_bmap_intent_destroy_cache`

Deferred bmap intents ignore unsupported forks, holes, and delayed allocations. Finish processing remaps or unmaps one extent at a time and uses an error tag hook for fault injection.

## Important Validation and Integrity Checks

- `xfs_bmap_validate_extent_raw` verifies file extent ranges, physical block ranges, realtime ranges, and unwritten-state restrictions.
- `xfs_bmap_validate_extent` adds inode context.
- `xfs_bmap_complain_bad_rec` reports corrupted bmap records with inode and fork context.
- Debug code verifies btree leaf order and duplicate child pointers.
- Many corruption branches mark btrees or forks sick before returning `-EFSCORRUPTED`.
- Shutdown state returns `-EIO`.
- Error tags inject bmap format, allocation, and finish-one failures for testing.

## Accounting Responsibilities

Mapping changes can update:

- `ip->i_nblocks`
- `ip->i_delayed_blks`
- fork extent counts
- global delayed allocation counters
- free data blocks
- free realtime extents
- zoned realtime availability
- quota block or realtime block counters
- transaction inode log flags
- btree cursor allocated-block counters
- reverse mapping records
- refcount records for reflink and CoW

`xfs_bmap_alloc_account` centralizes much post-allocation accounting. CoW fork allocations are treated as in-core quota reservations until remapped to the data fork.

## Notable Invariants

- CoW forks are not converted to bmap btree format through these helpers.
- Attribute fork extents cannot be unwritten.
- Returned mappings from `xfs_bmapi_read` and `xfs_bmapi_write` are ordered and contiguous in logical range.
- Delayed allocation records encode indirect block reservation in null startblocks.
- Btree mutations are mirrored in the in-core extent cache.
- Realtime extents often cannot be partially freed unless aligned to realtime extent boundaries.
- Rmap updates must track file offset changes during shifts and conversions.
- Data exposure safety requires newly allocated writeback extents to be unwritten until I/O completion.

## Dependencies and Collaborators

Major collaborators include:

- `xfs_bmap_btree.c` and `xfs_bmap_btree.h` for bmap btree operations.
- `xfs_iext_*` for in-core extent storage.
- `xfs_alloc_*` and filestream allocation for block placement.
- `xfs_rtbitmap`, `xfs_rtgroup`, and zoned allocation code for realtime files.
- `xfs_rmap_*` for reverse mappings.
- `xfs_refcount_*` for reflink and CoW accounting.
- transaction, quota, health, and error-tag subsystems.
- symlink and directory conversion helpers for local-to-remote fork transitions.
- iomap conversion helpers for writeback mappings.

## Research Notes

This file is high-risk because each mapping mutation has multiple synchronized side effects. The largest maintenance hazards are the extent merge/split state machines, delayed allocation reservation redistribution, realtime partial-free behavior, btree format transitions, and remap paths that intentionally suppress normal free/quota/refcount behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap.h

## Purpose

`xfs_bmap.h` declares the public block mapping interface used by XFS libxfs and higher-level filesystem code. It defines allocation state, bmapi flags, special startblock sentinels, extent update state flags, deferred bmap intent structures, validation helpers, and prototypes for mapping, unmapping, remapping, conversion, query, and extent-size hint operations.

## Main Types

### `struct xfs_bmalloca`

This is the central mutable allocation state passed through bmap allocation helpers. It carries:

- transaction and inode
- previous and current/next extent records
- requested logical offset and allocation length
- allocated filesystem block
- optional btree and in-core extent cursors
- allocation count and inode log flags
- total/minimum/minleft reservation constraints
- EOF, delayed-allocation, and conversion booleans
- allocation datatype
- bmapi flags

It ties allocation placement, extent insertion, btree updates, and accounting into one work object.

### `struct xfs_bmap_intent`

Represents a deferred bmap operation. It records the operation type, target fork, owner inode, optional group pointer, and the extent mapping to map or unmap later.

The intent types are:

- `XFS_BMAP_MAP`
- `XFS_BMAP_UNMAP`

## Important Flags

### `XFS_BMAPI_*`

These flags control mapping behavior:

- `ENTIRE`: return the whole extent rather than trimming to the request.
- `METADATA`: allocation is metadata rather than user data.
- `ATTRFORK`: operate on the attribute fork.
- `PREALLOC`: create or preserve unwritten preallocation.
- `CONTIG`: require a single contiguous allocation.
- `CONVERT`: convert extent state.
- `ZERO`: zero newly allocated or converted written extents.
- `REMAP`: map or unmap without normal allocation/free ownership semantics.
- `COWFORK`: operate on the CoW fork.
- `NODISCARD`: skip online discard for freed extents.
- `NORMAP`: skip rmap updates, used for reconstructing bmbt from rmapbt.
- `EXTSZALIGN`: try to align allocations to extent size hints.

### `BMAP_*`

These flags describe neighbor and fork state inside extent update state machines:

- left/right contiguity
- left/right filling
- left/right delayed allocation
- left/right validity
- attr fork
- CoW fork

## Special Startblocks

- `DELAYSTARTBLOCK` represents delayed allocation in returned mappings.
- `HOLESTARTBLOCK` represents holes in returned mappings.
- Null startblocks encode delayed allocation reservations internally.

The helper `xfs_bmap_is_real_extent` identifies allocated extents, and `xfs_bmap_is_written_extent` additionally excludes unwritten extents.

## Exported Operations

The header exposes:

- allocation accounting: `xfs_bmap_alloc_account`
- extent trimming: `xfs_trim_extent`
- fork conversion and attr fork setup
- btree max-level computation
- first/last logical extent queries
- read/write mapping: `xfs_bmapi_read`, `xfs_bmapi_write`
- unmapping: `xfs_bunmapi`, `xfs_bunmapi_range`
- delayed allocation and unwritten conversion helpers
- collapse/insert/split extent operations
- remapping: `xfs_bmapi_remap`
- deferred bmap intent helpers
- extent validation and corruption diagnostics
- bmap btree query helpers
- data and CoW extent size hint helpers

## Notable Invariants

- `xfs_bmapi_whichfork` gives precedence to `COWFORK`, then `ATTRFORK`, then data fork.
- `xfs_valid_startblock` rejects startblock zero for non-realtime inodes.
- `XFS_BMAP_MAX_NMAP` limits returned mappings to keep transactions bounded.
- Callers must combine flags carefully because `REMAP`, `PREALLOC`, `CONVERT`, `ZERO`, `NORMAP`, and `COWFORK` materially change quota, rmap, refcount, and data exposure semantics.

## Research Notes

This header is the contract for the whole XFS block mapping layer. Most correctness risk comes from flag combinations and from the shared `xfs_bmalloca` state object, which must remain consistent across allocation, extent insertion, btree conversion, and transaction logging.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap_btree.c

## Purpose

`xfs_bmap_btree.c` implements the btree backend for XFS inode block mappings. It supplies record encoding/decoding, root conversion, generic btree callbacks, block allocation/freeing, verifiers, inode-root reallocation, staged btree commit, owner changes, sizing helpers, and cursor cache lifecycle for bmap btrees.

The high-level bmap code uses this file when inode fork extent arrays outgrow inline extent format.

## Major Responsibilities

- Initialize bmap btree blocks with inode ownership.
- Convert between on-disk dinode-root format and in-core btree root format.
- Encode and decode packed bmap extent records.
- Provide `xfs_bmbt_ops` callbacks to the generic XFS btree layer.
- Allocate and free bmap btree blocks with inode and quota accounting.
- Verify bmap btree buffers, magic values, CRC headers, levels, and record counts.
- Resize in-core inode btree roots while moving pointer arrays.
- Commit staged rebuilt btrees into real inode forks.
- Change btree block owner values for fork swaps and recovery workflows.
- Calculate btree sizes and maximum levels.
- Initialize and destroy the bmap btree cursor slab cache.

## Record Encoding

Bmap extent records are packed across two 64-bit fields. Helpers include:

- `xfs_bmbt_disk_get_all`
- `xfs_bmbt_disk_get_blockcount`
- `xfs_bmbt_disk_get_startoff`
- `xfs_bmbt_disk_set_all`

The packed fields store extent state, file offset, start block, and block count. `xfs_bmbt_disk_set_all` asserts that state and bit widths fit the on-disk format.

## Root Conversion

`xfs_bmdr_to_bmbt` converts an on-disk dinode root into an in-core btree root. `xfs_bmbt_to_bmdr` converts the in-core root back to dinode-root format and checks CRC-era root invariants when applicable.

These conversions copy key and pointer arrays between layouts whose header sizes and pointer locations differ.

## Generic Btree Integration

`xfs_bmbt_ops` wires bmap btrees into the generic XFS btree implementation. It provides callbacks for:

- cursor duplication and update
- block allocation and freeing
- min/max record calculations
- root maximum record calculations
- key initialization and comparison
- record initialization
- buffer verifier operations
- key and record ordering checks
- key contiguity checks
- inode-root reallocation

`xfs_bmbt_init_cursor` creates cursors for data, attr, or staging forks. It rejects CoW forks and sizes staging cursors using the data fork maximum level.

## Block Allocation and Freeing

`xfs_bmbt_alloc_block` allocates one filesystem block for bmap btree growth, sets inode bmbt rmap owner information, observes delayed-allocation conversion state, handles zero block-reservation cases, and can activate transaction low-space mode. Successful allocation increments cursor allocation count, inode block count, quota, and inode log state.

`xfs_bmbt_free_block` schedules the btree block for freeing, decrements inode block count, logs the inode, and updates quota.

## Verification

`xfs_bmbt_verify` checks block magic, CRC-era block headers, maximum btree level, and generic btree block structure. Read and write verifiers wrap this with CRC verification or CRC calculation and emit btree corruption traces on failure.

`xfs_bmbt_keys_inorder` and `xfs_bmbt_recs_inorder` enforce strict key order and non-overlapping extent records.

## Inode Root Reallocation

`xfs_bmap_broot_realloc` grows, shrinks, or frees the in-core inode btree root according to a target record count. Because bmap root records and pointers are stored in separate arrays, pointer arrays must be moved when the root size changes.

This is layout-sensitive code: growing creates pointer holes for callers to fill, while shrinking compacts pointers before reallocating the root buffer.

## Staged Btree Commit

`xfs_bmbt_commit_staged_btree` replaces a real inode fork with a staged rebuilt fork, logs the appropriate extent or btree root fields, and commits the fake root through the generic btree staging layer. This is used by repair/rebuild style workflows that construct a replacement tree before making it live.

## Owner Changes and Sizing

`xfs_bmbt_change_owner` walks a btree-format fork and changes btree block owner metadata, either transactionally or by collecting buffers for recovery-style writeout.

Sizing helpers include:

- `xfs_bmbt_maxrecs`
- `xfs_bmbt_maxlevels_ondisk`
- `xfs_bmdr_maxrecs`
- `xfs_bmbt_calc_size`

## Notable Invariants

- CoW fork bmap btree cursors are not supported.
- Bmap btree blocks are owned as inode bmbt metadata.
- Btree block allocation is accounted to inode blocks and quota.
- Root and non-root block capacities are calculated differently.
- The inode root has in-core and on-disk layouts with different headers.
- Packed record fields must stay within their defined bit widths.
- Verifier level checks use the maximum of data and attr fork maxlevels because the verifier does not know the fork.

## Research Notes

This file is narrow but critical. Bugs in record packing, root pointer movement, max-record calculation, ownership changes, or verifier behavior can corrupt large-extent files and can break recovery, repair, or fork conversion paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap_btree.h

## Purpose

`xfs_bmap_btree.h` declares the bmap btree interface and inline layout helpers. It is the shared contract between the high-level block mapping code, inode fork code, and the bmap btree backend.

## Public Interfaces

The header declares:

- maximum bmap btree level access through `XFS_BM_MAXLEVELS`
- dinode-root to btree-root conversion
- packed bmap record get/set helpers
- btree-root to dinode-root conversion
- max-record and sizing helpers
- bmap btree owner changes
- cursor initialization
- staged btree commit
- cursor cache lifecycle
- btree block initialization
- in-core root reallocation

## Layout Helpers

Inline helpers compute addresses for:

- in-core bmap btree records, keys, and pointers
- on-disk dinode root records, keys, and pointers
- in-core inode btree root pointers
- CRC-aware btree block header length
- in-core btree root space
- on-disk dinode root space

Important helpers include:

- `xfs_bmbt_block_len`
- `xfs_bmbt_rec_addr`
- `xfs_bmbt_key_addr`
- `xfs_bmbt_ptr_addr`
- `xfs_bmdr_rec_addr`
- `xfs_bmdr_key_addr`
- `xfs_bmdr_ptr_addr`
- `xfs_bmap_broot_ptr_addr`
- `xfs_bmap_broot_space_calc`
- `xfs_bmdr_space_calc`

## Notable Invariants

- In-core btree blocks and on-disk dinode roots have different layouts.
- Header size depends on CRC support.
- Pointer arrays are positioned after the maximum key array for the chosen capacity.
- Root-space calculations must match inode fork sizing constraints.
- Callers must use the correct accessor family for the representation they are manipulating.

## Research Notes

This header is small but layout-sensitive. Any mistake in address calculation, header-size selection, root-space calculation, or max-record usage can corrupt inode-root bmap btrees during fork conversion, root growth/shrink, or btree staging.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap_btree.h -->