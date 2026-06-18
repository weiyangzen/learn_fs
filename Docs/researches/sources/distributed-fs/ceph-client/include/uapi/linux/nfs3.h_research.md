# sources/distributed-fs/ceph-client/include/uapi/linux/nfs3.h

## Purpose

`nfs3.h` defines NFS protocol, mount, idmapping, ACL, or server ABI constants for `nfs3`, including wire status values, file types, flags, ACLs, mount options, or upcall structures. The file is 104 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Exported structures include `nfs3_fh`. Enumerations include `nfs3_createmode`, `nfs3_ftype`, `nfs3_time_how`. Prominent attribute, command, flag, or constant names include `NFS3_CREATE_UNCHECKED`, `NFS3_CREATE_GUARDED`, `NFS3_CREATE_EXCLUSIVE`, `NF3NON`, `NF3REG`, `NF3DIR`, `NF3BLK`, `NF3CHR`, `NF3LNK`, `NF3SOCK`, `NF3FIFO`, `NF3BAD`, `DONT_CHANGE`, `SET_TO_SERVER_TIME`, `SET_TO_CLIENT_TIME`. Macros expose `_UAPI_LINUX_NFS3_H`, `NFS3_PORT`, `NFS3_MAXDATA`, `NFS3_MAXPATHLEN`, `NFS3_MAXNAMLEN`, `NFS3_MAXGROUPS`, `NFS3_FHSIZE`, `NFS3_COOKIESIZE`, `NFS3_CREATEVERFSIZE`, `NFS3_COOKIEVERFSIZE`, `NFS3_WRITEVERFSIZE`, `NFS3_FIFO_DEV`, `NFS3MODE_FMT`, `NFS3MODE_DIR`, `NFS3MODE_CHR`, `NFS3MODE_BLK`, `NFS3MODE_REG`, `NFS3MODE_LNK`, and 40 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

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

Source comments call out: NFSv3 protocol definitions; Flags for access() call; Flags for create mode.
