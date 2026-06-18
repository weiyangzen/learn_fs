# sources/distributed-fs/ceph-client/fs/xfs/scrub/rgsuper.c

## Purpose
`rgsuper.c` scrubs and repairs the realtime group superblock metadata. In the current implementation only rtgroup 0 has a superblock, so scrub mainly obtains the rtgroup, locks the realtime bitmap enough to stabilize the group, and cross-references the superblock block against realtime allocation/rmap metadata.

## Important APIs, types, and functions
The setup function is `xchk_setup_rgsuperblock`, which allocates a zero-block transaction. `xchk_rgsuperblock` performs the scrub. `xchk_rgsuperblock_xref` checks that realtime block zero is allocated and owned by filesystem metadata. With online repair enabled, `xrep_rgsuperblock` logs the superblock.

## Control flow
Scrub rejects any rtgroup number other than zero with `-ENOENT`. It obtains an existing rtgroup reference with `xchk_rtgroup_init_existing`, locks the bitmap in shared mode with `XFS_RTGLOCK_BITMAP_SHARED`, and relies on mount-time structural validation of the realtime superblock. It then runs cross-reference checks against rtbitmap and rtrmap. Repair asserts group zero and calls `xfs_log_sb` in the active transaction.

## State and persistence
Scrub records only corruption/xref flags in the scrub metadata. Repair persists by logging the filesystem superblock, not by reconstructing an independent per-group structure.

## Dependencies and integration points
It depends on rtgroup lookup/locking, realtime bitmap xref helper `xchk_xref_is_used_rt_space`, rtrmap helper `xchk_xref_is_only_rt_owned_by`, and generic scrub transaction setup. It integrates with realtime group scrub types and the repair dispatch table.

## Risks and test signals
Risks include future rtgroup formats where nonzero groups gain superblock-like data, races with group teardown, and xref behavior when rtrmap or rtbitmap cursors are unavailable. Tests should cover group zero, nonzero `-ENOENT`, missing rtgroup, shared bitmap locking, rmap owner mismatch for block zero, free block zero, and repair logging under online repair.
