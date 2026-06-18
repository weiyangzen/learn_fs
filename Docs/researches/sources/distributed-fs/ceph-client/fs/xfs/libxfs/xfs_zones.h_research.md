# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_zones.h

Purpose: Defines zoned realtime reservation constants and declares the zone validation helper.

Important APIs, types, and functions: Defines `XFS_GC_ZONES`, `XFS_RESERVED_ZONES`, `XFS_MIN_ZONES`, `XFS_OPEN_GC_ZONES`, `XFS_MIN_OPEN_ZONES`, `XFS_DEFAULT_MAX_OPEN_ZONES`, and declares `xfs_validate_blk_zone`.

Control flow: Zoned allocation and mount code use the constants to preserve forward progress for garbage collection and user writes. The validation function is called while scanning block device zones.

State and persistence: Constants influence incore allocator policy and superblock/device acceptance. They do not persist state directly, but reservation policy affects free-space availability and GC behavior.

Dependencies and integration points: Integrates with zoned realtime allocator, rtgroup open-zone tracking, garbage collection, and device topology validation.

Risks and test signals: Risks include too-small reserved zone counts causing GC deadlock, too-large defaults reducing usable capacity, and mismatched open-zone assumptions on devices without explicit limits. Test minimum-zone mounts, max-open-zone limits, sustained writes with GC, and near-full zoned realtime filesystems.
