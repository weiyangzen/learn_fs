# sources/distributed-fs/ceph-client/include/uapi/linux/nfsacl.h

## Purpose

`nfsacl.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfsacl`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 33 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Macros expose `_UAPI__LINUX_NFSACL_H`, `NFS_ACL_PROGRAM`, `ACLPROC2_NULL`, `ACLPROC2_GETACL`, `ACLPROC2_SETACL`, `ACLPROC2_GETATTR`, `ACLPROC2_ACCESS`, `ACLPROC3_NULL`, `ACLPROC3_GETACL`, `ACLPROC3_SETACL`, `NFS_ACL`, `NFS_ACLCNT`, `NFS_DFACL`, `NFS_DFACLCNT`, `NFS_ACL_MASK`, `NFS_ACL_DEFAULT`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: File: linux/nfsacl.h; (C) 2003 Andreas Gruenbacher <agruen@suse.de>; Flags for the getacl/setacl mode.
