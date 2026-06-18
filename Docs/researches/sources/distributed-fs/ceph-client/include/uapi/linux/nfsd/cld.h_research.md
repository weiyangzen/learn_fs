# sources/distributed-fs/ceph-client/include/uapi/linux/nfsd/cld.h

## Purpose

`cld.h` defines NFSD userspace ABI constants and structures used by the NFS server control, recovery, export, debug, or statistics interfaces. The file is 97 lines and is part of the NFS/NFSD userspace ABI UAPI surface.

## Important APIs, Types, and Functions

It includes `linux/types.h`. Exported structures include `cld_name`, `cld_princhash`, `cld_clntinfo`, `cld_msg`, `cld_msg_v2`, `cld_msg_hdr`. Enumerations include `cld_command`. Macros expose `_NFSD_CLD_H`, `CLD_UPCALL_VERSION`, `NFS4_OPAQUE_LIMIT`, `SHA256_DIGEST_SIZE`. There are no executable functions in the header; it exports constants and data layouts that must remain stable for user/kernel compatibility.

## Control Flow

NFS control flow is split between RPC wire protocol values, mount ioctls, idmapping messages, ACL structures, and NFSD control files. The header supplies stable constants and structures used by those paths; actual RPC dispatch, mount parsing, export validation, and recovery handling live elsewhere.

## State and Persistence Behavior

The header stores no state. Values described here can become part of mounted-client state, NFS server export state, lock/recovery records, idmapping upcalls, or RPC payloads managed by NFS/NFSD code. Because these are UAPI definitions, field sizes and numeric values are effectively persistent ABI and must not be renumbered.

## Dependencies and Integration Points

It integrates with NFS client mount code, NFS protocol/RPC handlers, NFSD control and export paths, idmapping, ACL handling, and userspace nfs-utils. It directly includes `linux/types.h`.

## Risks and Edge Cases

Key risks are structure padding, alignment, and fixed-width integer interpretation must match between 32-bit and 64-bit user space; enum and attribute IDs must not be reused or renumbered; wire-protocol constants must stay synchronized with RPC/XDR encoders, mount helpers, and server export policy. Because this is UAPI, even small layout changes can break old binaries or saved configuration.

## Test Signals

Useful signals include UAPI header selftests or compile tests that include the header from C and C++ translation units; nfs-utils mount/export/idmap compatibility tests and NFS protocol regression tests; XDR or ioctl structure size checks across 32-bit and 64-bit builds; ABI comparison checks that numeric constants and struct sizes remain stable.

## Source Notes

Source comments call out: Upcall description for nfsdcld communication; Copyright (c) 2012 Red Hat, Inc.; Author(s): Jeff Layton <jlayton@redhat.com>.
