# sources/distributed-fs/ceph-client/fs/nfsd/nfs3xdr.c

## Purpose
`nfs3xdr.c` implements XDR decoding, encoding, directory-entry construction, and release helpers for NFSD's NFSv3 service.

## Important APIs, types, and functions
Public helpers include `svcxdr_decode_nfs_fh3()`, `svcxdr_encode_nfsstat3()`, `svcxdr_encode_post_op_attr()`, all `nfs3svc_decode_*args()` functions, all `nfs3svc_encode_*res()` functions, `nfs3svc_encode_cookie3()`, `nfs3svc_encode_entry3()`, `nfs3svc_encode_entryplus3()`, `nfs3svc_release_fhandle()`, and `nfs3svc_release_fhandle2()`. Important internals include `svcxdr_decode_sattr3()`, `svcxdr_decode_filename3()`, `svcxdr_encode_fattr3()`, `svcxdr_encode_wcc_data()`, and `compose_entry_fh()`.

## Control flow
Decode helpers validate filehandle sizes, filename length and separators, sattr discriminants, create modes, write payload count/length consistency, readdir verifiers, and commit ranges. Write decode clamps oversized payloads to `svc_max_payload()` and creates an XDR subsegment. Encode helpers emit status first, then conditionally emit post-op attrs, WCC data, filehandles, payload page references, write verifiers, and filesystem/pathconf data. READ and READLINK encoders attach page payloads with `svc_encode_result_payload()`. READDIR entry encoding reserves a placeholder cookie, commits entries only on success, backpatches the previous cookie when the next entry arrives, and rolls back `dirlist.len` on buffer exhaustion. READDIRPLUS composes per-entry filehandles and attributes unless the entry is a mountpoint or outside the export root.

## State and persistence
No durable state is stored. Transient state lives in response structures: XDR stream positions, `dirlist` buffers, page pointers, cookie offsets, scratch filehandles, status fields, and saved pre/post attributes. Encoded fsids derive from export fsid, export UUID, or superblock device encoding.

## Dependencies and integration points
It depends on SUNRPC XDR stream/page helpers, NFSD filehandle and attribute helpers, NFSv3 protocol constants, export metadata for fsid source, user namespace mapping for uid/gid encoding, lease mtime adjustment, and VFS lookup for READDIRPLUS filehandle composition. It is wired into `nfs3proc.c` procedure descriptors.

## Risks and test signals
Risks include XDR length/padding errors, accepting malformed names or handles, uid/gid mapping surprises, symlink size clamping, fsid derivation mismatches, WCC/post-op attr omission after failures, READDIR cookie corruption, READDIRPLUS races with rename/unlink/mountpoints, and buffer exhaustion handling. Test signals include XDR fuzzing, max-size filehandles and names, names containing NUL or slash, write count/opaque length mismatch, reply buffer exhaustion for every encoder, READDIR cookie replay, READDIRPLUS on `.`/`..` and mountpoints, UUID fsid exports, and user namespace id encoding.
