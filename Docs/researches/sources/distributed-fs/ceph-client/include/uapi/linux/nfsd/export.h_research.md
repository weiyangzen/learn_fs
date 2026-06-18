# sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/export.h

## Purpose

`export.h` defines NFSD userspace ABI constants and structures used by the NFS server control, recovery, export, debug, or statistics interfaces. The file is 79 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

Macros expose `_UAPINFSD_EXPORT_H`, `NFSCLNT_IDMAX`, `NFSCLNT_ADDRMAX`, `NFSCLNT_KEYMAX`, `NFSEXP_READONLY`, `NFSEXP_INSECURE_PORT`, `NFSEXP_ROOTSQUASH`, `NFSEXP_ALLSQUASH`, `NFSEXP_ASYNC`, `NFSEXP_GATHERED_WRITES`, `NFSEXP_NOREADDIRPLUS`, `NFSEXP_SECURITY_LABEL`, `NFSEXP_SIGN_FH`, `NFSEXP_NOHIDE`, `NFSEXP_NOSUBTREECHECK`, `NFSEXP_NOAUTHNLM`, `NFSEXP_MSNFS`, `NFSEXP_FSID`, and 11 more. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It has no direct include dependencies beyond compiler-visible UAPI context.

## Risks and Edge Cases

Key risks are maximum-name, option, or attribute limits need bounds checks in producers and parsers; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: include/linux/nfsd/export.h; Public declarations for NFS exports. The definitions for the; syscall interface are in nfsctl.h.
