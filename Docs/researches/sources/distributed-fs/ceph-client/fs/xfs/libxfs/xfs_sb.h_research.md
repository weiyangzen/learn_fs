# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_sb.h

Purpose: Declares the superblock manipulation API shared by kernel and libxfs userspace code.

Important APIs, types, and functions: Declares logging/sync helpers `xfs_log_sb`, `xfs_sync_sb`, `xfs_sync_sb_buf`; mount geometry helpers `xfs_sb_mount_common`, `xfs_sb_mount_rextsize`, `xfs_mount_sb_set_rextsize`; disk conversion helpers `xfs_sb_from_disk`, `xfs_sb_to_disk`, `xfs_sb_quota_from_disk`; feature helpers `xfs_sb_good_version`, `xfs_sb_version_to_features`; secondary superblock helpers; geometry export via `xfs_fs_geometry`; validation helpers `xfs_validate_stripe_geometry`, `xfs_validate_rt_geometry`; and realtime log calculators `xfs_compute_rextslog`, `xfs_compute_rgblklog`.

Control flow: Consumers include mount, growfs, repair, log recovery, sync, and ioctl paths. `XFS_FS_GEOM_MAX_STRUCT_VER` caps geometry ABI versioning for `xfs_fs_geometry`.

State and persistence: The header itself has no state, but every function operates on persistent superblock fields or mount caches derived from them.

Dependencies and integration points: Depends on forward declarations for mount, superblock, disk superblock, transaction, geometry, and per-AG types; it is included broadly across XFS metadata code.

Risks and test signals: Risks are ABI drift in exported prototypes and mismatched userspace/kernel expectations. Test libxfs builds, all geometry ioctl versions, mount/growfs callers, and feature combinations that exercise both validation helpers.
