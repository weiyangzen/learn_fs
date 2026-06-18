# sources/distributed-fs/ceph-client/fs/xfs/xfs_verify_media.c

## Purpose
`xfs_verify_media.c` implements the privileged XFS media verification ioctl. It reads a caller-selected device range, advances the user-visible cursor over verified sectors, and can report real data loss to health monitoring and affected file owners when medium or protection errors occur.

## Important APIs, types, and functions
The exported entry point is `xfs_ioc_verify_media`. Internal helpers include `xfs_verify_media`, `xfs_verify_iosize`, `xfs_verify_alloc_folio`, `xfs_verify_media_error`, `xfs_verify_report_losses`, and `xfs_verify_report_data_lost`. It uses `struct xfs_verify_media`, `struct xfs_buftarg`, `struct bio`, rmap btree cursors, AG/RT group iteration, and `fserror_report_data_lost`.

## Control flow
The ioctl checks `CAP_SYS_ADMIN`, validates padding, flags, and target device, copies the request, and calls `xfs_verify_media`. Verification resolves data/log/realtime buftarg, clamps the end to the device size, checks logical-sector alignment, allocates a folio and one-bvec bio, and submits synchronous reads until done, interrupted, or a bio error occurs. Reportable errors trigger tracepoints, healthmon notifications, and if rmapbt exists, reverse-map walks to identify file extents whose data overlapped the failed media range.

## State and persistence
The operation is mostly stateless. It mutates the user request by updating `me_start_daddr`, possibly `me_end_daddr`, and `me_ioerror`. Persistent filesystem metadata is not changed except for health/sick markers when rmap records reveal damaged bmbt blocks, attr forks, or xattrs.

## Dependencies and integration points
It integrates with the block layer, XFS healthmon, reverse mapping btrees, AG and realtime group metadata, inode cache lookup, file-error reporting, and tracepoints. It depends on rmapbt for file-level data-loss attribution.

## Risks and test signals
Risks include off-by-one conversion between daddr, FSB, RTB, and group block numbers, false attribution when `xfs_iget` fails, alignment rejection, large allocation fallback, and interruption semantics. Test signals include unaligned requests, ranges past device end, data/log/rt devices, injected `BLK_STS_MEDIUM`, `BLK_STS_PROTECTION`, and transient errors, rmapbt on/off, realtime ranges, and fatal signal interruption.
