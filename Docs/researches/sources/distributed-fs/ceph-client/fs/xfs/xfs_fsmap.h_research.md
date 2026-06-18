# sources/distributed-fs/ceph-client/fs/xfs/xfs_fsmap.h

## Purpose
`xfs_fsmap.h` defines XFS-internal fsmap structures and declares the GETFSMAP ioctl handler.

## Important APIs, types, and functions
`struct xfs_fsmap` mirrors userspace `struct fsmap` in internal basic-block units. `struct xfs_fsmap_head` stores input flags, output flags, counts, and low/high keys. `struct xfs_fsmap_irec` represents an internal reverse-mapping record with disk address, length, owner, owner offset, rmap flags, and original rmapbt key. The header declares `xfs_ioc_getfsmap`.

## Control flow
The implementation converts userspace keys into these internal forms, scans device metadata, and converts the records back before copying results to userspace.

## State and persistence
The structures are temporary query state only and do not persist. They reflect durable reverse-map/free-space metadata read by `xfs_fsmap.c`.

## Dependencies and integration points
It depends on XFS block address types and Linux fsmap ABI types. It is used by ioctl and trace code.

## Risks and test signals
Risks are type-width and unit mismatches, especially physical/offset/length conversions. Test signals include compile coverage and GETFSMAP ABI round trips for large devices and high inode owner ids.
