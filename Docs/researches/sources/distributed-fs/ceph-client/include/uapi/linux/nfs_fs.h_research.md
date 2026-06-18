# sources/distributed-fs/ceph-client/include/uapi/linux/nfs_fs.h

## Purpose

`nfs_fs.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs_fs`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 63 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/magic.h`. Macros expose `_UAPI_LINUX_NFS_FS_H`, `NFS_DEF_UDP_TIMEO`, `NFS_DEF_UDP_RETRANS`, `NFS_DEF_TCP_TIMEO`, `NFS_DEF_TCP_RETRANS`, `NFS_MAX_UDP_TIMEOUT`, `NFS_MAX_TCP_TIMEOUT`, `NFS_DEF_ACREGMIN`, `NFS_DEF_ACREGMAX`, `NFS_DEF_ACDIRMIN`, `NFS_DEF_ACDIRMAX`, `FLUSH_SYNC`, `FLUSH_STABLE`, `FLUSH_LOWPRI`, `FLUSH_HIGHPRI`, `FLUSH_COND_STABLE`, `NFSDBG_VFS`, `NFSDBG_DIRCACHE`, and 15 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/magic.h`.

## Risks and Edge Cases

Key risks are maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: linux/include/linux/nfs_fs.h; Copyright (C) 1992  Rick Sladkey; OS-specific nfs filesystem definitions and declarations.
