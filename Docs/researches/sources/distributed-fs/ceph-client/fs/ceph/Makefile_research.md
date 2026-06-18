# sources/distributed-fs/ceph-client/fs/ceph/Makefile

## Purpose
This Makefile builds the CephFS client object and conditionally includes optional feature objects.

## Important APIs, Types, and Functions
`obj-$(CONFIG_CEPH_FS)` emits `ceph.o`. Core `ceph-y` objects include superblock, inode, directory, file, locks, address-space, ioctl, export, caps, snap, xattr, quota, io, MDS client/map, strings, fragments, debugfs, util, metrics, and subvolume metrics. Optional additions are `cache.o` for `CONFIG_CEPH_FSCACHE`, `acl.o` for `CONFIG_CEPH_FS_POSIX_ACL`, and `crypto.o` for `CONFIG_FS_ENCRYPTION`.

## Control Flow
There is no runtime flow. Kbuild assembles `ceph.o` from the selected objects based on Kconfig.

## State and Persistence Behavior
The selected objects determine which runtime subsystems exist in the CephFS client, including ACL xattr handling, FS-Cache integration, and encryption helpers.

## Dependencies and Integration Points
The Makefile integrates with CephFS Kconfig and the wider kernel build. `acl.o` corresponds to `acl.c` and is only present when POSIX ACL support is selected.

## Risks and Edge Cases
Adding calls to optional objects without Kconfig guards causes link failures in reduced builds. Object ordering and inclusion must stay aligned with declarations in Ceph headers and operation tables.

## Test Signals
Build CephFS with ACL, cache, and crypto options independently toggled, as module and built-in where dependencies allow. Link errors are the primary regression signal.
