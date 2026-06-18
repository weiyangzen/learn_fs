# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag_resv.h

## Purpose
This header declares the per-AG reservation interface used by XFS allocation and metadata btree code. It exposes initialization, teardown, critical-space checks, needed-reservation calculation, allocation/free accounting, and a helper to select the reservation object inside `struct xfs_perag`.

## Important APIs
- `xfs_ag_resv_init` and `xfs_ag_resv_free` establish and tear down per-AG reservations.
- `xfs_ag_resv_critical` and `xfs_ag_resv_needed` provide reservation availability signals to allocation policy.
- `xfs_ag_resv_alloc_extent` and `xfs_ag_resv_free_extent` adjust reservation/global accounting as blocks are allocated or freed.
- `xfs_perag_resv` maps `XFS_AG_RESV_METADATA` and `XFS_AG_RESV_RMAPBT` to `pag_meta_resv` and `pag_rmapbt_resv`.

## Control Flow and Integration
Allocator paths include this header to query reservation pressure before allocation and to update accounting after extent allocation/free. Mount/grow/shrink paths include it to reset or reinitialize reservations around AG geometry changes.

## State and Persistence Behavior
The header exposes in-core reservation state only. The selected `struct xfs_ag_resv` fields are persisted only in memory and affect persistent superblock counters indirectly through transaction accounting.

## Dependencies and Risks
Callers must pass only supported reservation types to `xfs_perag_resv`; unsupported types return `NULL` and are guarded by assertions in the implementation. Misuse of reservation type can corrupt fdblocks accounting or allow metadata ENOSPC.

## Test Signals
Build coverage for all callers, assertion/error-path testing for invalid reservation types, and accounting tests for metadata and rmapbt reservations are the main signals.
