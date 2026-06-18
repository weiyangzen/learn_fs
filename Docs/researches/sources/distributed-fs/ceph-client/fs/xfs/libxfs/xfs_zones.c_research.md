# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_zones.c

Purpose: Validates block-layer zone descriptors against XFS zoned realtime geometry and extracts write pointers for sequential zones.

Important APIs, types, and functions: Exports `xfs_validate_blk_zone`. Internal helpers `xfs_validate_blk_zone_seq` and `xfs_validate_blk_zone_conv` validate sequential-write-required and conventional zones respectively.

Control flow: Top-level validation checks that zone capacity equals expected realtime group capacity and zone length equals expected raw group size. Conventional zones are accepted only with `BLK_ZONE_COND_NOT_WP`. Sequential zones map empty to write pointer zero, open/closed/active states to `wp - start` after bounds checks, full zones to capacity, and reject not-write-pointer, offline, readonly, or unknown conditions.

State and persistence: No persistent state is written. The returned `write_pointer` is derived incore state used by zoned realtime allocation/open-zone tracking. Validation enforces superblock rtgroup geometry against device-reported topology.

Dependencies and integration points: Depends on Linux `blk_zone`, XFS mount block conversions, warning logging, and zoned realtime mount/device scan code.

Risks and test signals: Risks include accepting non-uniform last-zone capacity, write pointer conversion errors, unsupported conventional zone states, and mismatch between gapped raw zone size and allocatable capacity. Test empty/open/closed/active/full sequential zones, offline/readonly rejection, conventional zones, capacity/length mismatch, and write pointers at start/end/out-of-range.
