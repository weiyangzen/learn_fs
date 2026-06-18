# sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/msg-nfs3.h` declares the iovec-based NFSv3, mount, NLMv4, and ACL XDR wrapper API implemented by `msg-nfs3.c`. The source was read as a complete 219-line file for this report.

## Important APIs, Types, and Functions

The header declares decode helpers for NFS args (`xdr_to_getattr3args`, `xdr_to_setattr3args`, `xdr_to_lookup3args`, `xdr_to_read3args`, `xdr_to_write3args`, `xdr_to_write3args_nocopy`, directory operation args, fsstat/fsinfo/pathconf/commit args), encode helpers for NFS results, mount helpers, NLM helpers, and ACL helpers. It includes generated `xdr-nfs3.h`, `nlm4-xdr.h`, and `acl3-xdr.h`.

## Control Flow

There is no executable control flow in the header. It defines the compile-time contract used by GNFS RPC handlers to convert raw RPC iovec buffers to typed request/response structures.

## State and Persistence Behavior

No state is owned here. Function contracts imply caller-owned input/output iovecs and typed structures.

## Dependencies and Integration Points

This header integrates generated NFS/NLM/ACL XDR types with Gluster's NFS server code and `libgfxdr`. It depends on system `iovec` and type definitions.

## Risks and Edge Cases

Declaration drift between this header and `msg-nfs3.c` will break builds or cause incorrect function calls. Nocopy variants need clear caller discipline because payload ownership differs from normal decode helpers. Conditional `BUILD_GNFS` build logic must keep this header installed only when matching generated headers exist.

## Test Signals

Compile coverage with `BUILD_GNFS`, link coverage for every declared symbol, and RPC handler tests that include this header and call decode/encode helpers are the key signals.
