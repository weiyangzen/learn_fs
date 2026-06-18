# sources/distributed-fs/ceph-client/include/uapi/linux/nfs4_mount.h

## Purpose

`nfs4_mount.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs4_mount`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 72 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `nfs_string`, `nfs4_mount_data`, `sockaddr`. Macros expose `_LINUX_NFS4_MOUNT_H`, `NFS4_MOUNT_VERSION`, `NFS4_MOUNT_SOFT`, `NFS4_MOUNT_INTR`, `NFS4_MOUNT_NOCTO`, `NFS4_MOUNT_NOAC`, `NFS4_MOUNT_STRICTLOCK`, `NFS4_MOUNT_UNSHARED`, `NFS4_MOUNT_FLAGMASK`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: linux/include/linux/nfs4_mount.h; Copyright (C) 2002  Trond Myklebust; structure passed from user-space to kernel-space during an nfsv4 mount.
