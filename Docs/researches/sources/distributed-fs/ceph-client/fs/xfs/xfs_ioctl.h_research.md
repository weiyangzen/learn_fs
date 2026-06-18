## sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl.h

Purpose: declares the native ioctl-facing XFS APIs shared by file operations, compat ioctl handling, and bulk inode formatting code.

Important APIs and types: it forward-declares `struct xfs_bstat`, `struct xfs_ibulk`, and `struct xfs_inogrp`. It exposes `xfs_ioc_swapext` for extent swapping, `xfs_fileattr_get` and `xfs_fileattr_set` for VFS fileattr integration, `xfs_file_ioctl` and `xfs_file_compat_ioctl` as ioctl entry points, and the legacy formatter helpers `xfs_fsbulkstat_one_fmt` and `xfs_fsinumbers_fmt`.

Control flow: the header itself has no runtime flow, but it defines the handoff points. VFS file operations call `xfs_file_ioctl`; compat dispatch calls `xfs_file_compat_ioctl`; compat code can reuse native bulkstat formatters when native layout is appropriate, such as x32 ABI handling.

State and persistence behavior: no state is stored here. The declared APIs may mutate filesystem state through swapext, file attribute changes, labels, growfs, and other ioctl operations implemented in `xfs_ioctl.c`.

Dependencies and integration: consumers need XFS and VFS types already visible from surrounding includes. This header links ioctl code to inode operations (`fileattr_get/set`), file operations (`ioctl/compat_ioctl`), and itable formatting.

Risks and test signals: ABI stability depends on keeping prototypes synchronized with implementations and avoiding type drift in formatter callbacks. Build coverage with native and compat ioctl enabled is the main signal; runtime coverage comes from fileattr, swapext, and bulkstat ioctl tests.
