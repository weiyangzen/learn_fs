# sources/distributed-fs/ceph-client/fs/xfs/Makefile

## Purpose
This Makefile defines how the XFS kernel module or built-in object is assembled. It sets include paths for trace events and libxfs, orders trace compilation first, builds common libxfs components, high-level VFS integration, transaction/log recovery code, optional quota/realtime/ACL/compat/exportfs objects, and online scrub/repair objects under their Kconfig gates.

## Important Build Groups
- `obj-$(CONFIG_XFS_FS) += xfs.o` ties all `xfs-y` fragments into the XFS object.
- `xfs_trace.o` is first because trace macro expansion can be fragile.
- `libxfs/` objects include allocation group, allocator, btrees, metadata formats, directory, inode, rmap, refcount, realtime group, and transaction reservation code shared conceptually with userspace libxfs.
- High-level objects include VFS I/O, buffers, inode cache, ioctl, iomap, reflink, mount/super, sysfs, xattrs, and health monitoring.
- Transaction/log objects include log, CIL, item formats, recovery, AIL, and transaction buffer handling.
- Conditional groups cover quota, realtime, POSIX ACL, sysctl, compat ioctls, pNFS block export, DAX memory failure notification, hooks/drain/memory buffer/in-memory btree, scrub, scrub stats, and repair.

## Control Flow and Integration
The file has no runtime control flow, but the object ordering shapes link-time availability. The early libxfs group makes core metadata code available to higher layers; optional scrub/repair objects are only compiled under nested `ifeq` gates. It mirrors `Kconfig` symbols and therefore is the concrete build integration point for feature selection.

## State and Persistence Behavior
No runtime state is stored here. Build selections determine which runtime subsystems exist and therefore whether certain persistent on-disk features can be serviced.

## Dependencies and Integration Points
The Makefile integrates with Kbuild, Kconfig symbols, XFS trace headers, `libxfs` include paths, memory failure/DAX support, realtime code, quota, ACL, online scrub/repair, and exportfs block operations.

## Risks and Edge Cases
Object omission or ordering mistakes can break link dependencies, trace generation, or optional feature builds. Conditional blocks must remain consistent with Kconfig selects: for example repair depends on scrub and adds in-memory btree code; realtime scrub/repair objects require `CONFIG_XFS_RT`; quota scrub/repair requires `CONFIG_XFS_QUOTA`.

## Test Signals
Build all Kconfig combinations that toggle `XFS_QUOTA`, `XFS_RT`, `XFS_POSIX_ACL`, `CONFIG_COMPAT`, `CONFIG_SYSCTL`, `CONFIG_XFS_ONLINE_SCRUB`, and `CONFIG_XFS_ONLINE_REPAIR`. Link failures, missing symbols, modpost warnings, trace build failures, and xfstests feature skips are primary signals.
