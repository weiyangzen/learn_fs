# sources/distributed-fs/ceph-client/fs/nfs/nfs3xdr.c

## Purpose
`nfs3xdr.c` implements XDR encoding and decoding for NFSv3 and the optional NFSv3 ACL side protocol. It defines the NFSv3 RPC procedure table `nfs3_procedures[]`, `nfs_version3`, and, when configured, `nfsacl_version3`.

## Important APIs, Types, And Functions
The file contains size macros for each NFSv3 argument and reply shape, a file type mapping table, user namespace helpers, primitive codecs for integers, file IDs, names, paths, cookies, verifiers, filehandles, times, types, device numbers, attributes, weak cache consistency data, and post-op filehandles. Encoders cover GETATTR, SETATTR with optional guard, LOOKUP, ACCESS, READLINK, READ, WRITE, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RENAME, LINK, READDIR, READDIRPLUS, COMMIT, GETACL, and SETACL. Decoders cover the matching result unions plus `nfs3_decode_dirent()`.

## Control Flow And Integration Points
NFSv3 procedure dispatch is table-driven through the `PROC()` macro at the end of the file. Read, readlink, readdir, and ACL get operations prepare page-backed receive buffers before RPC. Write and symlink encoders mark transmit buffers as page-backed writes. Result decoders first read `nfsstat3`, then decode success or failure arms, preserving post-op or WCC attributes even on errors. Directory replies are stored as raw XDR pages; `nfs3_decode_dirent()` later decodes entries, including readdirplus attributes and filehandles, during directory iteration.

## State And Persistence Behavior
Static state is limited to RPC procedure tables and per-procedure counters. Runtime state is written into caller-owned response structs. Attribute decoders set `NFS_ATTR_FATTR_V3`, WCC fields, pre-change values, mounted-on file IDs, and write verifier/stability values. `decode_read3resok()` records `eof`, byte count, and guards against mismatched opaque lengths. `nfs3_xdr_dec_read3res()` records `replen` so later reads can optimize header sizing.

## Dependencies
Dependencies include SunRPC XDR streams, NFSv3 protocol constants, NFS ACL encoding/decoding helpers, page buffers, user namespace uid/gid mapping, NFS common status-to-errno conversion, NFS tracepoints, and common helpers such as `nfs_timespec_to_change_attr()` and `nfs_umode_to_dtype()`.

## Risks And Edge Cases
Malformed XDR is common-risk surface: oversized names/paths/handles, invalid uid/gid mappings, bad stable write modes, mismatched read counts, invalid ACL masks, and missing post-op filehandles must be rejected or normalized. `nfs3_xdr_enc_setacl3args()` contains explicit `BUG_ON(error < 0)` comments, so invalid ACL marshalling would crash rather than return a recoverable error. Readdirplus must handle file ID mismatches by recording mounted-on fileid for mountpoint detection.

## Test Signals
Run NFSv3 protocol tests for every procedure, fuzz or fault-inject malformed XDR replies, exercise user namespaces, readdir and readdirplus caches, large ACL payloads, missing create filehandles that force lookup, WCC behavior after failures, write verifier changes, and read header-size caching.
