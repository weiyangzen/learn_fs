# sources/distributed-fs/ceph-client/include/uapi/linux/nfs_mount.h

## Purpose

`nfs_mount.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs_mount`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 69 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/in.h`, `linux/nfs.h`, `linux/nfs2.h`, `linux/nfs3.h`. Exported structures include `nfs_mount_data`, `nfs2_fh`, `sockaddr_in`, `nfs3_fh`. Macros expose `_LINUX_NFS_MOUNT_H`, `NFS_MOUNT_VERSION`, `NFS_MAX_CONTEXT_LEN`, `NFS_MOUNT_SOFT`, `NFS_MOUNT_INTR`, `NFS_MOUNT_SECURE`, `NFS_MOUNT_POSIX`, `NFS_MOUNT_NOCTO`, `NFS_MOUNT_NOAC`, `NFS_MOUNT_TCP`, `NFS_MOUNT_VER3`, `NFS_MOUNT_KERBEROS`, `NFS_MOUNT_NONLM`, `NFS_MOUNT_BROKEN_SUID`, `NFS_MOUNT_NOACL`, `NFS_MOUNT_STRICTLOCK`, `NFS_MOUNT_SECFLAVOUR`, `NFS_MOUNT_NORDIRPLUS`, and 2 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/in.h`, `linux/nfs.h`, `linux/nfs2.h`, `linux/nfs3.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: linux/include/linux/nfs_mount.h; Copyright (C) 1992  Rick Sladkey; structure passed from user-space to kernel-space during an nfs mount.
