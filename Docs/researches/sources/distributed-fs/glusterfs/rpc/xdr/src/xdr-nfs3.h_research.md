# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-nfs3.h

## Purpose

`xdr-nfs3.h` is the public XDR contract for GlusterFS's NFSv3 and mount protocol support. It defines the wire-sized scalar aliases, NFSv3 status/procedure enums, request and response structs, mount protocol structs, and encoder/decoder prototypes implemented in `xdr-nfs3.c`. Consumers such as `rpc/xdr/src/msg-nfs3.c`, `xlators/nfs/server/src/nfs3*.c`, ACL code, and mount service code include this header to marshal RPC arguments and replies.

## Important APIs, types, and constants

- Fixed protocol sizes: `NFS3_FHSIZE`, cookie/create/write verifier sizes, and size-estimation macros for readdir/write paths (`NFS3_ENTRY3_FIXED_SIZE`, `NFS3_READDIR_RESOK_SIZE`, `NFS3_WRITE3ARGS_SIZE`).
- Scalar aliases: `uint64`, `int64`, `uint32`, `filename3`, `nfspath3`, `fileid3`, `cookie3`, `uid3`, `gid3`, `size3`, `offset3`, `mode3`, and `count3`.
- Core NFSv3 enums: `nfsstat3`, `ftype3`, `time_how`, `stable_how`, and `createmode3`.
- Attribute and weak-cache-consistency types: `fattr3`, `post_op_attr`, `pre_op_attr`, `wcc_attr`, and `wcc_data`.
- Procedure structs for all NFSv3 calls: `getattr3*`, `setattr3*`, `lookup3*`, `access3*`, `readlink3*`, `read3*`, `write3*`, create/mkdir/symlink/mknod/remove/rmdir/rename/link, `readdir3*`, `readdirp3*`, `fsstat3*`, `fsinfo3*`, `pathconf3*`, and `commit3*`.
- Mount protocol types: `fhandle3`, `mountstat3`, `mountres3`, linked `mountlist`, `groups`, and `exports`.
- Program/procedure numbers: `NFS_PROGRAM`, `NFS_V3`, `NFS3_*`, `MOUNT_PROGRAM`, `MOUNT_V3`, `MOUNT_V1`, and `MOUNT*_PROC_COUNT`.
- XDR prototypes: one `xdr_*` function per scalar, enum, struct, list, and response union, plus optimized helpers `xdr_read3res_nocopy()` and `xdr_free_write3args_nocopy()`.

## Control flow and data model

This header has no executable control flow, but it encodes the discriminated-union model used by the generated/manual XDR routines. Most result structs begin with a status field and contain a union where success arms include full object/parent metadata while failure arms carry weak cache consistency or post-op attributes. Optional protocol fields use `bool_t` discriminants, for example `post_op_attr.attributes_follow`, `pre_op_attr.attributes_follow`, and `post_op_fh3.handle_follows`. Linked-list reply shapes (`entry3`, `entryp3`, `mountbody`, `groupnode`, `exportnode`) are recursive and rely on the matching XDR routines to allocate/free list nodes.

## State and persistence behavior

The types describe RPC wire state only. Persistent storage is outside the header; however, fields such as file handles, cookies, verifiers, weak-cache-consistency attributes, and write commit verifiers carry server state across client requests. The fixed-size constants are important because code in the NFS server sizes buffers and no-copy read/write paths around the NFSv3 wire representation.

## Dependencies and integration points

The header depends on SunRPC-style `XDR`/`bool_t` definitions from `<rpc/rpc.h>` and C integer types from `<sys/types.h>`. `rpc/xdr/src/Makefile.am` builds `xdr-nfs3.c` and `msg-nfs3.c` when GNFS is enabled. `msg-nfs3.c` uses the prototypes to serialize RPC messages and specifically references `xdr_read3res_nocopy()`. The NFS server stack includes this header via `nfs3.h`, `nfs3-fh.c`, `nfs3.c`, ACL code, and mount service sources.

## Risks and edge cases

- The file handle model permits variable-length `nfs_fh3`, but Gluster's comments and size macros assume returned handles are 64 bytes in some hot paths. A future shorter/longer file handle contract would require auditing buffer sizing and no-copy helpers.
- Recursive list types need correct ownership handling in XDR decode/free paths; leaks or double-frees are likely if callers bypass `xdr_free_exports_list()`, `xdr_free_mountlist()`, or XDR free semantics.
- Status-discriminated unions are valid only when encoders and decoders use the same `status` arm logic. Adding a status/procedure without updating `xdr-nfs3.c` would silently break the wire contract.
- `NFS3ERR_END_OF_LIST = -1` is not a normal RFC NFS status and must not leak to wire consumers that expect unsigned enum values.
- The header aliases integer types by short names (`uint64`, `uint32`) that can collide with other platform headers.

## Test signals

Good coverage comes from RPC encode/decode round trips for every procedure, NFSv3 interoperability tests against standard clients, readdir/readdirplus list/free stress tests, no-copy READ and WRITE memory ownership tests, and mount/export list serialization tests. Integration signals include successful GNFS builds, NFS server functional tests for all `NFS3_*` procedures, and ABI checks that struct/procedure definitions remain synchronized with `xdr-nfs3.c`.
