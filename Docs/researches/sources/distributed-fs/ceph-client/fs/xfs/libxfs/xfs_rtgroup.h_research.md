# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtgroup.h

Purpose: Defines the incore realtime group abstraction, realtime group metadata inode slots, lock flags, reference helpers, block/address conversion helpers, and public prototypes for rtgroup and realtime superblock operations.

Important APIs, types, and functions: Defines `enum xfs_rtg_inodes`, `struct xfs_rtgroup`, `XFS_RTG_FREE`, `XFS_RTGLOCK_*`, `to_rtg`, `rtg_group`, `rtg_mount`, `rtg_rgno`, `rtg_blocks`, `rtg_bitmap`, `rtg_summary`, `rtg_rmap`, `rtg_refcount`, passive/active ref helpers, rtgroup iterators, `xfs_verify_rgbno`, `xfs_verify_rgbext`, `xfs_rgbno_to_rtb`, `xfs_rtb_to_rgno`, `xfs_rtb_to_rgbno`, `xfs_rtb_to_daddr`, `xfs_daddr_to_rtb`, `xfs_rtginode_path`, `xfs_rtgs_to_rfsbs`, and `xfs_rtgroup_raw_size`.

Control flow: Callers use passive refs for cached access and active refs for objects that must remain live. Conversion helpers route through generic `xfs_group` math, but `xfs_rtb_to_daddr` and `xfs_daddr_to_rtb` handle the rtgroups case without device-address gaps by remapping sparse group block numbers to packed device offsets. `CONFIG_XFS_RT` gates real implementations; non-RT builds compile to no-op or unsupported stubs.

State and persistence: The structure stores metadata inode pointers, realtime extent count, a union for either bitmap summary cache or zoned open-zone state, and zoned GC reference count. It describes incore state only, but its conversion helpers encode assumptions about persisted realtime geometry in the superblock.

Dependencies and integration points: Included by realtime allocation, bitmap, rmap/refcount, scrub, growfs, mount, and zoned code. It depends on `xfs_group.h` for generic group lifetime and geometry primitives and on superblock-derived `m_groups[XG_TYPE_RTG]` geometry.

Risks and test signals: Risks include off-by-one iteration in `xfs_rtgroup_next`, incorrect raw size when `ZONE_GAPS` is active, packed vs gapped device address conversion errors, and using RGB verifiers on non-rtgroup filesystems. Test conversion round trips, first-group rtsb exclusion, non-power-of-two realtime extent sizes, gapped zoned layouts, `CONFIG_XFS_RT=n`, and lock flag combinations.
