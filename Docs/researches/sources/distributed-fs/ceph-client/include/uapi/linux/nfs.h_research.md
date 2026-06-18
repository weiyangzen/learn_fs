# sources/distributed-fs/ceph-client/include/uapi/linux/nfs.h

## Purpose

`nfs.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 133 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Enumerations include `nfs_stat`, `nfs_ftype`. Prominent attribute, command, flag, or constant names include `NFS_OK`, `NFSERR_PERM`, `NFSERR_NOENT`, `NFSERR_IO`, `NFSERR_NXIO`, `NFSERR_ACCES`, `NFSERR_EXIST`, `NFSERR_XDEV`, `NFSERR_NODEV`, `NFSERR_NOTDIR`, `NFSERR_ISDIR`, `NFSERR_INVAL`, `NFSERR_FBIG`, `NFSERR_NOSPC`, `NFSERR_ROFS`, `NFSERR_MLINK`, `NFSERR_NAMETOOLONG`, `NFSERR_NOTEMPTY`, `NFSERR_DQUOT`, `NFSERR_STALE`, `NFSERR_REMOTE`, `NFSERR_WFLUSH`, and 57 more. Macros expose `_UAPI_LINUX_NFS_H`, `NFS_PROGRAM`, `NFS_PORT`, `NFS_RDMA_PORT`, `NFS_MAXDATA`, `NFS_MAXPATHLEN`, `NFS_MAXNAMLEN`, `NFS_MAXGROUPS`, `NFS_FHSIZE`, `NFS_COOKIESIZE`, `NFS_FIFO_DEV`, `NFSMODE_FMT`, `NFSMODE_DIR`, `NFSMODE_CHR`, `NFSMODE_BLK`, `NFSMODE_REG`, `NFSMODE_LNK`, `NFSMODE_SOCK`, and 5 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: NFS protocol definitions; This file contains constants mostly for Version 2 of the protocol,; but also has a couple of NFSv3 bits in (notably the error codes)..
