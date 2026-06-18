# sources/distributed-fs/ceph-client/include/uapi/linux/fsmap.h

This header defines the generic reverse-mapping ioctl ABI for filesystem space maps. It lets userspace query which owners occupy physical block ranges, primarily for filesystem diagnostics and scrub/repair tooling.

Important exports include `struct fsmap`, `struct fsmap_head`, device selector constants, owner constants for metadata/free/unknown/static filesystem regions, flag bits such as `FMR_OF_*`, and request flags such as `FMH_OF_DEV_T` where present. The ABI is consumed through `FS_IOC_GETFSMAP` in filesystem-specific ioctl dispatch.

Control flow is ioctl based: userspace provides low and high keys plus a record count; the filesystem walks its reverse mapping metadata and returns sorted `fsmap` records, updating the head with actual count and flags. State is a snapshot of allocator/reverse-map metadata and can race with concurrent allocation. Persistence is the filesystem allocation state being reported.

Dependencies include `linux/types.h`, generic VFS ioctl plumbing, and filesystems that implement reverse mapping such as XFS and Btrfs-like designs. Integration points include `xfs_io`, scrub tools, defragmentation/space accounting tools, and filesystem repair diagnostics.

Risks include exposing physical layout, inconsistent snapshots under concurrent writes, owner-code compatibility across filesystems, device ID ambiguity, and off-by-one range handling. Test signals include fsmap xfstests, low/high key iteration tests, multi-device filesystem tests, metadata owner validation, and permission checks.
