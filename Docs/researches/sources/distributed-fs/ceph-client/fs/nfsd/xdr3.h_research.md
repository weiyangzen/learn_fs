# sources/distributed-fs/ceph-client/fs/nfsd/xdr3.h

## Purpose

`xdr3.h` defines NFSD's NFSv3 XDR argument/result structs and the NFSv3 encoder/decoder API. Compared with NFSv2 it adds 64-bit offsets/cookies, ACCESS, COMMIT, weak cache consistency result shapes, FSINFO/PATHCONF, and optional POSIX ACL operations.

## Important APIs, Types, and Functions

Argument types include `nfsd3_sattrargs` with guard time, `nfsd3_diropargs`, `nfsd3_accessargs`, `nfsd3_readargs`, `nfsd3_writeargs` with stable mode and verifier payload, `nfsd3_createargs`, `nfsd3_mknodargs`, `nfsd3_renameargs`, `nfsd3_linkargs`, `nfsd3_symlinkargs`, `nfsd3_readdirargs`, `nfsd3_commitargs`, `nfsd3_getaclargs`, and `nfsd3_setaclargs`.

Response types include `nfsd3_attrstat`, `nfsd3_diropres`, `nfsd3_accessres`, `nfsd3_readlinkres`, `nfsd3_readres`, `nfsd3_writeres`, `nfsd3_renameres`, `nfsd3_linkres`, `nfsd3_readdirres`, `nfsd3_fsstatres`, `nfsd3_fsinfores`, `nfsd3_pathconfres`, `nfsd3_commitres`, and `nfsd3_getaclres`. `union nfsd3_xdrstore` defines request scratch size as `NFS3_SVC_XDRSIZE`.

The declared routines are `nfs3svc_decode_*`, `nfs3svc_encode_*`, release helpers, `nfs3svc_encode_cookie3()`, `nfs3svc_encode_entry3()`, `nfs3svc_encode_entryplus3()`, and ACL helper codecs.

## Control Flow

NFSv3 dispatch decodes requests into these structs, runs the corresponding service/VFS function, and encodes responses with post-op attributes and WCC data. Readdir and readdirplus use the embedded stream/buffer/common cursor fields and scratch filehandle to encode entries and optional attributes. Write and commit results carry write verifiers used by client cache consistency.

## State and Persistence Behavior

All data structures here are per-request. They hold filehandles, decoded ACL pointers, pages, XDR payload buffers, write verifiers, stat/statfs snapshots, and readdir encoding cursors. Persistent filesystem effects come from downstream operations, while release functions clean transient filehandle and ACL/page references.

## Dependencies and Integration Points

`xdr3.h` includes `xdr.h` and shares base NFSv2 helpers. It integrates with `svc_fh`, `kstat`, `kstatfs`, `xdr_stream`, `xdr_buf`, POSIX ACLs, and NFSv3 service procedure tables.

## Risks and Edge Cases

Guarded setattr must compare ctime correctly. Readdirplus has more buffer pressure because each entry can include handles and attributes. Stable write and commit verifier fields must match writeback behavior in `vfs.c`. ACL pointers require proper release on decode or execution failure. 64-bit cookies must remain consistent with file mode flags selected by the VFS readdir layer.

## Test Signals

Exercise NFSv3 ACCESS, guarded SETATTR, READ/WRITE with stable modes, COMMIT verifier changes after writeback errors, CREATE modes, MKNOD, RENAME/LINK WCC data, READDIR/READDIRPLUS small buffers and 64-bit cookies, FSSTAT/FSINFO/PATHCONF, and getacl/setacl decode/release paths.
