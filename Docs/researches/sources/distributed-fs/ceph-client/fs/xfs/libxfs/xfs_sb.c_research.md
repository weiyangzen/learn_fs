# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_sb.c

Purpose: Provides shared superblock validation, feature decoding, disk/incore conversion, verifier ops, mount geometry initialization, superblock logging/sync, secondary superblock update/read helpers, filesystem geometry export, and stripe/realtime geometry checks.

Important APIs, types, and functions: Exports `xfs_sb_good_version`, `xfs_sb_version_to_features`, `xfs_validate_rt_geometry`, `xfs_compute_rgblklog`, `xfs_sb_quota_from_disk`, `xfs_sb_from_disk`, `xfs_sb_to_disk`, `xfs_sb_buf_ops`, `xfs_sb_quiet_buf_ops`, `xfs_sb_mount_rextsize`, `xfs_mount_sb_set_rextsize`, `xfs_sb_mount_common`, `xfs_log_sb`, `xfs_sync_sb`, `xfs_update_secondary_sbs`, `xfs_sync_sb_buf`, `xfs_fs_geometry`, `xfs_sb_read_secondary`, `xfs_sb_get_secondary`, `xfs_validate_stripe_geometry`, and `xfs_compute_rextslog`.

Control flow: Read verification optionally checks CRC, converts the disk superblock without quota normalization, validates common geometry and feature masks, then enforces read-only/incompat feature policy. Write verification reconverts from disk, repeats common checks, validates summary counters and log LSN, stamps the buffer LSN, and updates CRC. Mount initialization caches block/sector/AG/RTG/btree geometry into `struct xfs_mount`. Logging recomputes lazy counters, writes incore state to the primary superblock buffer, and logs the full disk superblock.

State and persistence: Persistent state is the primary/secondary `xfs_dsb`, including v4/v5 feature masks, quota inode fields, metadir/rtgroup fields, zoned fields, summary counters, UUIDs, and CRC/LSN. Incore state normalizes old quota fields, derives `sb_meta_uuid`, zeros legacy rt bitmap inode numbers for metadir filesystems, and initializes rtgroup geometry and btree max records.

Dependencies and integration points: Central to mount, log recovery, growfs, quota, rtgroups, zoned realtime, metadir, xfsrepair-compatible secondary superblocks, transaction logging, buffer cache verification, and userspace geometry ioctls.

Risks and test signals: Risks include accepting unsupported feature combinations, writing bad summary counters, v4/v5 quota conversion regressions, metadir rtgroup geometry mismatches, zoned alignment mistakes, stale secondary superblocks, and CRC/LSN validation ordering. Test v4 and v5 mounts, unknown compat/ro-compat/incompat bits, metadir+rtgroups+zoned combinations, external/internal log mismatch, stripe mount-option repair, growfs secondary updates, quota inode normalization, and geometry ioctl versions 1-5.
