# sources/distributed-fs/ceph-client/fs/nfsd/xdr.h

## Purpose

`xdr.h` defines server-side NFSv2 XDR argument/result storage types and encoder/decoder prototypes. It is mainly a typed bridge between SUNRPC XDR streams and the NFSD operation layer.

## Important APIs, Types, and Functions

Request structs include `nfsd_fhandle`, `nfsd_sattrargs`, `nfsd_diropargs`, `nfsd_readargs`, `nfsd_writeargs`, `nfsd_createargs`, `nfsd_renameargs`, `nfsd_linkargs`, `nfsd_symlinkargs`, and `nfsd_readdirargs`. Response structs include `nfsd_stat`, `nfsd_attrstat`, `nfsd_diropres`, `nfsd_readlinkres`, `nfsd_readres`, `nfsd_readdirres`, and `nfsd_statfsres`.

`union nfsd_xdrstore` sizes per-request scratch storage, and `NFS2_SVC_XDRSIZE` exposes that size to the RPC dispatch table. Decoder prototypes are named `nfssvc_decode_*`; encoder prototypes are `nfssvc_encode_*`. Helpers such as `nfssvc_encode_nfscookie()`, `nfssvc_encode_entry()`, `svcxdr_decode_fhandle()`, `svcxdr_encode_stat()`, and `svcxdr_encode_fattr()` are shared with NFSv2 ACL support.

## Control Flow

For each NFSv2 procedure, the RPC layer allocates argument/result storage using the union size, invokes the matching decode routine into one of these structs, executes a service operation, then calls the matching encode routine. Readdir responses carry an `xdr_stream`, `xdr_buf`, common readdir cursor data, and a cookie offset so directory entries can be encoded incrementally.

## State and Persistence Behavior

The structs are per-RPC transient state. Persistent changes occur only after decoded arguments are passed to VFS/service logic. Several fields hold filehandle references, page pointers, or XDR buffers that require release callbacks such as `nfssvc_release_attrstat()`, `nfssvc_release_diropres()`, and `nfssvc_release_readres()`.

## Dependencies and Integration Points

This header depends on Linux VFS types, `nfsd.h`, `nfsfh.h`, SUNRPC `xdr_stream`, `xdr_buf`, pages, and `svc_fh`. It feeds the NFSv2 dispatch implementation and helper code used by v2 ACL encoding.

## Risks and Edge Cases

NFSv2 uses 32-bit offsets and cookies, so handlers must guard truncation and maximum file sizes. Result structs that carry pages or filehandles need correct release functions to avoid leaks. Readdir encoding has tight buffer constraints and must report too-small/eof correctly.

## Test Signals

Run NFSv2 getattr/setattr/lookup/read/write/create/remove/rename/link/symlink/readdir/statfs tests, including oversized names, short reply buffers, 32-bit offset boundaries, readlink page handling, and filehandle release/leak checks.
