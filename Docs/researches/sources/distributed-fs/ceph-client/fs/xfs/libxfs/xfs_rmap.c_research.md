# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap.c

## Purpose
`xfs_rmap.c` implements reverse mapping btree record lookup, validation, mutation, deferred intent finishing, and query helpers. Reverse mappings record who owns physical blocks, enabling metadata repair, online scrub, reflink owner accounting, and correct tracking of metadata/file/COW extents.

## Important APIs, types, and functions
Exported low-level APIs include `xfs_rmap_lookup_le`, `xfs_rmap_lookup_eq`, `xfs_rmap_insert`, `xfs_rmap_get_rec`, `xfs_rmap_query_range`, `xfs_rmap_query_all`, `xfs_rmap_has_records`, `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`, and `xfs_rmap_map_raw`. Direct per-AG update wrappers are `xfs_rmap_alloc` and `xfs_rmap_free`.

Deferred high-level APIs include `xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, `xfs_rmap_convert_extent`, `xfs_rmap_alloc_extent`, `xfs_rmap_free_extent`, and `xfs_rmap_finish_one`. `struct xfs_rmap_intent` carries owner, fork, bmbt extent, group, realtime flag, and operation type. Owner constants such as `XFS_RMAP_OINFO_FS`, `XFS_RMAP_OINFO_REFC`, and `XFS_RMAP_OINFO_COW` provide canonical metadata owners.

Validation flows through `xfs_rmap_btrec_to_irec`, `xfs_rmap_check_irec`, and `xfs_rtrmap_check_irec`. The validators enforce legal block ranges, owner classes, offset/fork rules, unwritten restrictions, and realtime group constraints.

## Control flow
Mapping an extent unpacks owner info, chooses ordinary or shared behavior, searches for adjacent mergeable records, and either extends a left/right neighbor or inserts a new record. Unmapping finds the covering record, verifies owner and unwritten state unless the owner is unknown for EFI recovery, then deletes, trims, or splits the record. Conversion toggles the unwritten flag for a file data extent, using a state bitmask to decide whether to merge with left/right neighbors or split a previous record into up to three records.

Reflink-capable file data can overlap by physical block with different owners, so shared variants (`xfs_rmap_map_shared`, `xfs_rmap_unmap_shared`, `xfs_rmap_convert_shared`) use range queries plus delete/insert when key fields change. Non-overlapping metadata and ordinary mappings use simpler cursor-local updates. `__xfs_rmap_finish_intent` dispatches deferred operations to the correct implementation; `xfs_rmap_finish_one` creates or reuses an AG or RTG cursor, translates the bmbt startblock to group block number, applies the change, and calls live update hooks.

## State and persistence behavior
Persistent state is the AG or realtime reverse mapping btree. The record key is ordered by physical startblock, owner, and packed offset flags; unwritten is a record attribute that is masked out of key comparisons. Mutations happen inside transactions through generic btree update/insert/delete. Deferred rmap intents are allocated from `xfs_rmap_intent_cache` and logged by the rmap item layer. AG finishers refresh the freelist before changing the rmapbt because btree shape changes allocate from AGFL; RTG finishers lock/join the realtime group with `XFS_RTGLOCK_RMAP`.

## Dependencies and integration points
This file depends on btree operations, rmap btree cursor construction, realtime rmap btree cursors, transactions, allocation/free-list management, inode fork state, reflink feature detection, health marking, tracepoints, and optional live hooks. Bmap update paths enqueue file mapping changes; allocation code calls metadata map/free helpers; scrub/repair use range queries and owner-count helpers; refcount COW tracking calls rmap alloc/free with `XFS_RMAP_OWN_COW`.

## Risks and invariants
The most sensitive logic is interval trimming, logical offset adjustment, shared-overlap lookup, and key-field updates. Invariants include nonzero blockcount, valid owner IDs or metadata owner range, no offsets for non-inode owners, no unwritten metadata/attr/bmbt records, exact bmbt offset zero, and full coverage for unmap/convert operations. `XFS_RMAP_OWN_UNKNOWN` intentionally relaxes owner checks for log recovery; misuse outside recovery would hide mismatches.

## Test signals
Coverage should include metadata allocation/free, file map/unmap, unwritten conversion, reflink shared owner overlaps, EFI recovery unknown-owner frees, realtime rmap operations, live hook notification, and corruption paths that mark the btree sick. Scrub tests should validate `xfs_rmap_count_owners` and `xfs_rmap_has_other_keys` on shared and non-shareable owners.
