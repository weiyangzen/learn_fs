# sources/distributed-fs/ceph-client/fs/nfs/nfs4xdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfs/nfs4xdr.c` is the Linux NFS client-side XDR implementation for NFSv4. It translates VFS/NFS client operation arguments into NFSv4 COMPOUND RPC request streams, decodes server replies back into NFS client result structures, validates operation ordering and reply sizes, and publishes the NFS version 4 RPC procedure table. The source was read as a complete 7,786-line file for this report.

## Important APIs, Types, and Functions

The file centers on `struct compound_hdr`, which tracks COMPOUND status, operation count, tag, expected reply length, and minor version while encoding or decoding. Public integration objects are `nfs4_procedures[]`, `nfs_version4_counts[]`, `nfs_version4`, `nfs41_maxwrite_overhead`, `nfs41_maxread_overhead`, `nfs41_maxgetdevinfo_overhead`, and `nfs4_decode_dirent`.

The generic encoder layer includes `reserve_space`, `encode_string`, `encode_uint32`, `encode_uint64`, `xdr_encode_bitmap4`, `mask_bitmap4`, `encode_compound_hdr`, `encode_op_hdr`, `encode_nops`, `encode_nfs4_stateid`, `encode_nfs4_verifier`, `encode_attrs`, and per-operation helpers such as `encode_open`, `encode_close`, `encode_read`, `encode_write`, `encode_readdir`, `encode_getattr`, `encode_setattr`, `encode_lock`, `encode_layoutget`, `encode_layoutcommit`, `encode_layoutreturn`, `encode_exchange_id`, `encode_create_session`, and `encode_sequence`.

The RPC-facing encoder entry points are named `nfs4_xdr_enc_*` and build full COMPOUND sequences for access, lookup, open, read/write, metadata, ACL, fs_locations, security, lease/session, and pNFS operations. They are wired into `nfs4_procedures[]` through `PROC`, `PROC40`, `PROC41`, and `PROC42`.

The generic decoder layer includes `decode_compound_hdr`, `__decode_op_hdr`, `decode_op_hdr`, `decode_bitmap4`, `decode_attr_*` helpers, `verify_attr_len`, `decode_getfattr_attrs`, `decode_getfattr_generic`, `decode_fsinfo`, `decode_getfh`, `decode_open`, `decode_read`, `decode_write`, `decode_readdir`, `decode_readlink`, `decode_secinfo_common`, `decode_exchange_id`, `decode_create_session`, `decode_sequence`, `decode_getdeviceinfo`, and the pNFS layout decoders. RPC-facing decoders are named `nfs4_xdr_dec_*`.

## Control Flow

Encoding starts in an `nfs4_xdr_enc_*` procedure selected from `nfs4_procedures[]`. The entry point initializes a `compound_hdr`, emits the COMPOUND header, usually emits `OP_SEQUENCE` for NFSv4.1+ sessions, places the current filehandle with `PUTFH` or `PUTROOTFH`, emits one or more operation-specific bodies, prepares reply pages for bulk replies when needed, and finally patches the real operation count with `encode_nops`.

Simple metadata flows are linear. For example LOOKUP encodes `SEQUENCE`, `PUTFH`, `LOOKUP`, `GETFH`, and `GETATTR`; ACCESS optionally appends `GETATTR`; STATFS and PATHCONF request selected attributes through `GETATTR` bitmaps. Mutating directory operations such as RENAME and LINK use `SAVEFH` and `RESTOREFH` to control the current and saved filehandles.

Data paths use page-backed XDR buffers. READ, READLINK, READDIR, GETACL, FS_LOCATIONS, GETDEVICEINFO, and LAYOUTGET call `rpc_prepare_reply_pages` or enter reply pages so large opaque payloads land directly in page vectors. WRITE, SETACL, symlink creation, and layoutcommit can splice caller pages into the send buffer with `xdr_write_pages` and set XDR buffer flags.

Decoding mirrors the compound order. Each `nfs4_xdr_dec_*` routine decodes the COMPOUND header, checks the session sequence where present, verifies each expected operation with `decode_op_hdr`, and only then fills result fields. Attribute decoding is order-sensitive: bitmap bits are consumed by `decode_attr_*` helpers, unexpected earlier bits are treated as malformed XDR, and `verify_attr_len` confirms that the decoded attribute body length matches the server's declared length.

pNFS control flow adds layout-specific handling. `LAYOUTGET` validates that at least one layout is returned, decodes stateid/range/type/length, and reads opaque layout bytes from pages. `GETDEVICEINFO` reads opaque device addresses into pages and validates the layout type and notification bitmap. `LAYOUTRETURN` and `LAYOUTCOMMIT` manage layout stateids and optional size updates.

NFSv4.2 procedures are conditionally included by `#include "nfs42xdr.c"` and conditionally wired into the same table. NFSv4.0-only operations such as RENEW and RELEASE_LOCKOWNER are compiled as real procedures only when `CONFIG_NFS_V4_0` is enabled; otherwise procedure slots become stubs.

## State and Persistence Behavior

This file owns no durable storage. It mutates caller-provided RPC argument/result structures, page arrays, XDR streams, NFS fattr structures, sequence/session state fields, lock/open seqids, and pNFS layout/device buffers. Reply status is propagated into result fields such as `op_status`, `sr_status`, `lr_ret`, `sattr_ret`, and layout-specific `status`.

Protocol state appears in encoded and decoded stateids, clientids, sessionids, sequence numbers, slot ids, verifier values, open/lock owner identifiers, delegations, and pNFS layout state. These are persisted by higher NFS client state managers, not by this file. The static `nfs_version4_counts` array is RPC statistics storage associated with the exported `nfs_version4` table.

Attribute results populate caches through `struct nfs_fattr`, filehandles through `struct nfs_fh`, fsinfo/pathconf/statfs structures, ACL buffers, security flavor pages, and fs_locations structures. Directory entries are not decoded at READDIR RPC completion; `nfs4_decode_dirent` parses cached XDR directory pages later when VFS readdir consumers request entries.

## Dependencies and Integration Points

The file depends on Linux SUNRPC XDR APIs (`xdr_stream`, `xdr_buf`, `rpc_rqst`, `rpc_prepare_reply_pages`), NFS protocol definitions (`linux/nfs.h`, `linux/nfs4.h`, `linux/nfs_fs.h`, `linux/nfs_common.h`), NFSv4 client internals (`nfs4_fs.h`, `internal.h`, `nfs4idmap.h`, `nfs4session.h`, `pnfs.h`, `netns.h`), GSS/security types, and kernel identity mapping helpers.

Important integration points are the RPC procedure table consumed by the NFS client transport layer, idmapping via `nfs_map_uid_to_name`, `nfs_map_gid_to_group`, `nfs_map_name_to_uid`, and `nfs_map_group_to_gid`, tracepoints from `nfs4trace.h` for bad XDR status/operation/filehandle cases, pNFS layout driver callbacks for layoutreturn encoding, and NFSv4.2 XDR code included from `nfs42xdr.c`.

Compile-time configuration affects behavior through `CONFIG_NFS_V4_0`, `CONFIG_NFS_V4_1`, `CONFIG_NFS_V4_2`, `CONFIG_NFS_V4_SECURITY_LABEL`, `DEBUG`, and implementation ID settings. The file also integrates with kernel UTS data for implementation IDs and session AUTH_SYS callback parameters.

## Risks and Edge Cases

XDR length accounting is a primary risk. Encode size macros must stay aligned with the actual helper bodies and with the `p_arglen`/`p_replen` values registered in `nfs4_procedures[]`. Underestimates can corrupt send or receive buffer planning; overestimates can waste space or hide incomplete decode assumptions.

Attribute bitmap ordering is fragile. Many `decode_attr_*` helpers reject earlier unexpected bits, and `verify_attr_len` rejects mismatched attribute lengths. Adding or reordering attributes requires protocol-order review across encoder masks, decoder helpers, and fattr validity flags.

Bulk page handling is security-sensitive. READ, READLINK, READDIR, ACL, deviceinfo, layoutget, and fs_locations replies rely on correct page length, offset, and padding calculations. The code has explicit checks for giant symlinks, cheating servers that report more data than received, invalid filehandle lengths, unsupported notifications, layout type mismatches, and empty layout arrays.

State sequencing is correctness-sensitive. OPEN/CLOSE/LOCK decoders increment sequence ids on non-XDR statuses, `decode_sequence` rejects mismatched session ids, sequence numbers, and slot ids, and pNFS paths lock around layout stateid encoding. Incorrect status propagation can break recovery or replay behavior.

Several paths intentionally tolerate partial or optional data, such as ignored extra layout entries, optional implementation IDs, optional security labels, unsupported ACL attributes, and fallback owner/group mapping to `nobody` during encode. These behaviors should be preserved deliberately because they encode interoperability choices with imperfect servers.

## Test Signals

Useful test signals include kernel build coverage across NFSv4.0, v4.1, v4.2, pNFS, ACL, xattr, and security-label configurations; NFS client xfstests over v4.0/v4.1/v4.2 for open, delegation, locking, rename/link/create, ACL, fs_locations, and read/write/commit flows; pNFS layoutget/getdeviceinfo/layoutcommit/layoutreturn tests with multiple layout types and small maxcount retries; fault injection or packet-level tests for malformed XDR lengths, invalid op numbers, bad filehandle sizes, giant symlink lengths, truncated page payloads, and mismatched session slots; and tracepoint checks for `nfs4_xdr_status`, bad operations, and bad filehandles.
