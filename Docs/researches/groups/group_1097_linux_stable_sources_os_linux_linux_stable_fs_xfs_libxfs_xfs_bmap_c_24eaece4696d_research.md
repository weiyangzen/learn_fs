# Group Research: group_1097_linux_stable_sources_os_linux_linux_stable_fs_xfs_libxfs_xfs_bmap_c_24eaece4696d

Scope: `Docs/research_subset_a.md`

This group covers the XFS block mapping layer in Linux stable: the high-level inode fork mapping implementation, its public interface, and the bmap btree implementation used when inode extent arrays outgrow inline extent format. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap.c

## Purpose

`xfs_bmap.c` is the core XFS logical-to-physical block mapping implementation. It translates file offsets to filesystem blocks, allocates and frees extents, converts delayed allocation and unwritten extents, maintains inode fork extent state, and coordinates bmap updates with reverse mapping, refcount, quota, realtime allocation, deferred operations, and transaction logging.

## Major Responsibilities

- Compute bmap btree maximum levels and default attribute fork offsets.
- Convert inode fork formats between local, extent, and btree representations.
- Load btree-format extents into the in-core extent cache.
- Query first/last mapped or unused logical blocks.
- Add extents for delayed allocation conversion, unwritten conversion, hole allocation, and reflink remap.
- Select and perform block allocations, including stripe alignment, extent size hints, filestream AG selection, low-space fallback, realtime allocation dispatch, and debug minlen injection.
- Map read ranges without allocation via `xfs_bmapi_read`.
- Map write ranges with allocation/conversion via `xfs_bmapi_write`.
- Convert individual delalloc extents for writeback via `xfs_bmapi_convert_delalloc`.
- Unmap ranges via `xfs_bunmapi` and `xfs_bunmapi_range`.
- Shift/split extents for collapse range, insert range, and extent splitting operations.
- Record and finish deferred bmap intent items.
- Validate extent records and expose btree query helpers.

## Key Functions and Behavior

- `xfs_bmap_compute_maxlevels` calculates mount-time max bmap btree height.
- `xfs_bmap_btree_to_extents` collapses a shallow btree fork back to inline extent format.
- `xfs_bmap_extents_to_btree` allocates a child btree block, builds the inode root, and copies extents into the leaf.
- `xfs_iread_extents` materializes validated btree records into the in-core extent tree.
- `xfs_bmap_add_extent_delay_real`, `xfs_bmap_add_extent_unwritten_real`, and `xfs_bmap_add_extent_hole_real` implement the main extent insertion/conversion state machines.
- `xfs_bmap_btalloc` selects alignment and allocation strategy before accounting for success.
- `xfs_bmapi_read` walks mappings and synthesizes hole records.
- `xfs_bmapi_write` allocates holes/delalloc extents, converts unwritten extents, and returns mappings.
- `xfs_bmap_del_extent_delay`, `xfs_bmap_del_extent_cow`, and `xfs_bmap_del_extent_real` remove or split delayed, CoW, and real extents.
- `xfs_bmap_finish_one` executes deferred bmap map/unmap intent work.

## Important Invariants

- CoW fork does not convert to btree format through these helpers.
- Extents remain sorted by logical offset and non-overlapping.
- Real extents merge only when logical adjacency, physical adjacency, state, max extent length, and realtime group constraints all permit it.
- Btree format collapses back to extents when extent count fits, except for CoW fork.
- Mutations update in-core extents, optional btree records, inode counts, quota, rmaps/refcounts, and log flags.

## Research Notes

This is a high-risk convergence point for allocation, delayed allocation, reflink, realtime, quota, logging, and btree format transitions. Behavioral changes need coverage for extent and btree forks, delalloc/unwritten transitions, ENOSPC paths, reflink remap, realtime files, and rmap/refcount interactions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap.h

## Purpose

`xfs_bmap.h` is the public interface for XFS block mapping operations. It declares allocation state, mapping flags, internal extent state flags, special startblock sentinels, exported bmap operations, deferred bmap intent structures, validation helpers, and query APIs.

## Key Types and Flags

- `struct xfs_bmalloca` carries mutable allocation state: transaction, inode, neighboring extents, logical offset, length, physical block, cursors, reservations, EOF/delalloc/conversion state, datatype, and flags.
- `DELAYSTARTBLOCK` denotes delayed allocation extents.
- `HOLESTARTBLOCK` denotes holes in returned mappings.
- `XFS_BMAPI_*` flags control read/write/remap behavior, including attr fork, CoW fork, preallocation, conversion, zeroing, remap, no-rmap, no-discard, and extent-size alignment.
- `BMAP_*` flags describe neighbor and fork state during extent update state machines.
- `struct xfs_bmap_intent` records deferred map or unmap work.

## Exported Operations

The header exposes mapping (`xfs_bmapi_read`, `xfs_bmapi_write`, `xfs_bmapi_remap`), unmapping (`xfs_bunmapi`, `xfs_bunmapi_range`), delalloc conversion, fork conversion, attr fork setup, extent shift/split helpers, allocation helpers, deferred mapping helpers, validation, diagnostics, btree query, and extent-size hint helpers.

## Research Notes

The flag combinations define much of the valid behavioral surface. Callers must choose `REMAP`, `PREALLOC`, `CONVERT`, `COWFORK`, `NORMAP`, and `ZERO` carefully because they alter quota, rmap, refcount, and data exposure semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap_btree.c

## Purpose

`xfs_bmap_btree.c` implements the btree backend for XFS inode block mappings. It provides block initialization, root conversion, packed extent record encoding/decoding, generic btree callbacks, block allocation/freeing, verifier operations, inode-root reallocation, staged btree commit, owner changes, sizing helpers, and cursor slab lifecycle.

## Major Responsibilities

- Encode and decode compact bmap extent records with `xfs_bmbt_disk_get_all` and `xfs_bmbt_disk_set_all`.
- Convert between on-disk dinode-root form and in-core btree root form.
- Provide `xfs_bmbt_ops` callbacks to the generic XFS btree layer.
- Allocate and free bmap btree blocks with inode block/quota accounting.
- Verify bmap btree buffers, levels, magic values, CRC state, and record limits.
- Resize in-core inode btree roots while moving pointer arrays correctly.
- Commit staged rebuilt btrees into real inode forks.
- Change btree block ownership for fork swaps or recovery contexts.
- Initialize and destroy the `xfs_bmbt_cur` cursor cache.

## Important Invariants

- CoW fork btree cursors are rejected.
- Btree blocks are owned as inode bmbt metadata and accounted against inode blocks/quota.
- Inode-root and non-root block capacities differ and are calculated separately.
- Packed record fields must fit their on-disk bit widths.
- Verifiers enforce generic btree structure plus bmap-specific level limits.

## Research Notes

This file is narrow but critical. Bugs in packed record encoding, root pointer movement, max-record calculations, or verifier behavior can break large-extent files, repair, recovery, and mapping lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap_btree.h

## Purpose

`xfs_bmap_btree.h` declares the bmap btree interface and inline layout helpers. It is the shared contract between high-level bmap code, inode fork code, and the bmap btree backend.

## Public Interfaces

The header declares root conversion, packed record conversion, capacity helpers, cursor initialization, staged tree commit, owner changes, cache lifecycle, block initialization, and in-core root resizing.

## Layout Helpers

It provides address helpers for:

- In-core bmap btree blocks: records, keys, pointers.
- On-disk dinode btree roots: records, keys, pointers.
- In-core inode btree roots.
- CRC-aware btree block header sizing.
- In-core and on-disk root space calculations.

## Important Invariants

- In-core and on-disk root layouts differ, so callers must use the correct accessor family.
- Pointer arrays are positioned after the maximum key array for the current capacity.
- Header size depends on CRC support.
- Layout or space-calculation mistakes can silently corrupt inode-root btrees.

## Research Notes

This header is small but layout-sensitive. Changes to address calculations, space calculations, or max-record declarations can corrupt root key/pointer copying during fork conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap_btree.h -->