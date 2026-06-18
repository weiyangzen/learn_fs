# sources/distributed-fs/ceph-client/include/uapi/linux/nfs_idmap.h

## Purpose

`nfs_idmap.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs_idmap`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 65 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `idmap_msg`. Macros expose `_UAPINFS_IDMAP_H`, `IDMAP_NAMESZ`, `IDMAP_TYPE_USER`, `IDMAP_TYPE_GROUP`, `IDMAP_CONV_IDTONAME`, `IDMAP_CONV_NAMETOID`, `IDMAP_STATUS_INVALIDMSG`, `IDMAP_STATUS_AGAIN`, `IDMAP_STATUS_LOOKUPFAIL`, `IDMAP_STATUS_SUCCESS`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: include/uapi/linux/nfs_idmap.h; UID and GID to name mapping for clients.; Copyright (c) 2002 The Regents of the University of Michigan..
