# sources/distributed-fs/ceph-client/include/uapi/linux/nfs2.h

## Purpose

`nfs2.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs2`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 68 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `nfs2_fh`. Enumerations include `nfs2_ftype`. Prominent attribute, command, flag, or constant names include `NF2NON`, `NF2REG`, `NF2DIR`, `NF2BLK`, `NF2CHR`, `NF2LNK`, `NF2SOCK`, `NF2BAD`, `NF2FIFO`. Macros expose `_LINUX_NFS2_H`, `NFS2_PORT`, `NFS2_MAXDATA`, `NFS2_MAXPATHLEN`, `NFS2_MAXNAMLEN`, `NFS2_MAXGROUPS`, `NFS2_FHSIZE`, `NFS2_COOKIESIZE`, `NFS2_FIFO_DEV`, `NFS2MODE_FMT`, `NFS2MODE_DIR`, `NFS2MODE_CHR`, `NFS2MODE_BLK`, `NFS2MODE_REG`, `NFS2MODE_LNK`, `NFS2MODE_SOCK`, `NFS2MODE_FIFO`, `NFS2_VERSION`, and 18 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: NFS protocol definitions; This file contains constants for Version 2 of the protocol.; NFSv2 file types - beware, these are not the same in NFSv3.
