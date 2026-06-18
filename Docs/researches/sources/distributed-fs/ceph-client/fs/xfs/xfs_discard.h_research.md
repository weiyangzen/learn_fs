# sources/distributed-fs/ceph-client/fs/xfs/xfs_discard.h

Purpose: Declares XFS discard and FITRIM entry points.

Important APIs, types, and functions: Forward-declares `struct fstrim_range`, `struct xfs_mount`, and `struct xfs_busy_extents`; declares `xfs_discard_extents()` and `xfs_ioc_trim()`.

Control flow: Callers submit prepared busy extent lists or dispatch userspace FITRIM requests through these functions.

State and persistence: No state is defined here.

Dependencies and integration points: Included by ioctl, extent-busy, and discard implementation code.

Risks and test signals: Risks are declaration drift and missing userspace pointer annotations. Test builds with realtime and non-realtime configurations.
