# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc.h

## Purpose
This header declares the public and shared interfaces for XFS free-space allocation, freeing, AGFL manipulation, AGF reading/logging, allocator queries, deferred extent frees, and allocator work/cache lifecycle.

## Important Types, Flags, and APIs
- `struct xfs_alloc_arg` is the central allocation request/result object containing transaction, mount, AG/perag, target block, min/max length, alignment, locality bounds, reservation type, owner info, datatype flags, and outputs.
- Freelist flags include `TRYLOCK`, `FREEING`, `NORMAP`, `NOSHRINK`, `CHECK`, and `TRYFLUSH`.
- Datatype flags describe user data, initial user data, and no-busy constraints.
- Allocation entry points are `xfs_alloc_vextent_this_ag`, `near_bno`, `exact_bno`, `start_ag`, and `first_ag`.
- Freeing entry points include `__xfs_free_extent`, inline `xfs_free_extent`, `xfs_free_extent_later`, and `xfs_free_extent_fix_freelist`.
- AGF/AGFL functions include `xfs_alloc_read_agf`, `xfs_read_agf`, `xfs_alloc_read_agfl`, `xfs_alloc_fix_freelist`, `xfs_alloc_get_freelist`, `xfs_alloc_put_freelist`, and `xfs_alloc_log_agf`.
- Query and validation functions include `xfs_alloc_get_rec`, `xfs_alloc_check_irec`, `xfs_alloc_query_range`, `xfs_alloc_query_all`, `xfs_alloc_has_records`, `xfs_agfl_walk`, and `xfs_validate_ag_length`.
- `struct xfs_extent_free_item` records deferred free intent state, owner, block range, group, flags, and reservation type.
- Autoreap helpers schedule, cancel, or commit crash-recovery-backed freeing for newly allocated unwritten space.

## Control Flow and Integration
Callers populate `xfs_alloc_arg` and choose an allocation mode; the implementation validates, prepares an AG, allocates, updates rmap/accounting, and returns `fsbno/len` or `NULLFSBLOCK`. Free callers pass a perag plus AG-relative extent to `xfs_free_extent`, or schedule a deferred free through `xfs_free_extent_later`. Scrub/repair code uses query helpers and AGFL walking to inspect free-space state.

## State and Persistence Behavior
The header exposes interfaces that mutate AGF/AGFL/free-space btrees, rmap btrees, superblock counters, deferred intent log items, and in-core perag counters. `struct xfs_extent_free_item` is transient memory but represents work that can be logged as persistent EFI/EFD recovery state.

## Dependencies and Integration Points
It depends on transactions, btree cursors, perag references, owner info, reservation types, deferred ops, realtime/free flags, and buffer handling. It is included broadly by XFS bmap, inode, grow/shrink, scrub, repair, and log recovery code.

## Risks and Edge Cases
`xfs_alloc_arg` has many fields with mode-specific meaning; uninitialized alignment, min/max, reservation, or owner data can cause ENOSPC, corruption assertions, or rmap/accounting errors. Deferred free flags must distinguish realtime, discard skipping, attr fork, bmbt, and cancelled items correctly. Free extents must be AG-valid and non-null.

## Test Signals
Compile API consumers, allocation mode tests, deferred free recovery tests, rmap owner validation, realtime free flag handling, AGFL walk/query tests, and debug assertions for malformed `xfs_alloc_arg` fields are useful signals.
