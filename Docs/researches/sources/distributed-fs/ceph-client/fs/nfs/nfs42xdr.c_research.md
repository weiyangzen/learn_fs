# sources/distributed-fs/ceph-client/fs/nfs/nfs42xdr.c

## Purpose

`nfs42xdr.c` supplies the XDR encode/decode implementation and size accounting for NFSv4.2 client procedures. It defines compound request layouts for ALLOCATE, COPY, OFFLOAD_CANCEL, OFFLOAD_STATUS, COPY_NOTIFY, DEALLOCATE, ZERO_RANGE, READ_PLUS, SEEK, LAYOUTSTATS, LAYOUTERROR, CLONE, and NFSv4.2 xattr operations.

## Important APIs, Types, and Functions

The file defines maximum encode/decode sizes plus exported overhead constants `nfs42_maxsetxattr_overhead`, `nfs42_maxgetxattr_overhead`, and `nfs42_maxlistxattrs_overhead`, used by session setup to cap xattr transfer sizes. Encoders named `nfs4_xdr_enc_*` add COMPOUND headers, SEQUENCE, PUTFH/SAVEFH, operation payloads, reply page preparation, and follow-up GETATTR or COMMIT. Decoders named `nfs4_xdr_dec_*` reverse those sequences.

Important helpers include `encode_copy`, `encode_read_plus`, `encode_layoutstats`, `encode_setxattr`, `encode_listxattrs`, `decode_write_response`, `decode_copy`, `decode_offload_status`, `decode_copy_notify`, `decode_read_plus`, `decode_getxattr`, and `decode_listxattrs`.

## Control Flow

Each encoder initializes `compound_hdr`, encodes COMPOUND and SEQUENCE, encodes relevant filehandles, encodes the operation, optionally encodes GETATTR or COMMIT, and finalizes op counts. Variable-length data operations call `rpc_prepare_reply_pages` so response data lands directly in caller pages.

`READ_PLUS` decodes all returned data/hole segments first, then processes them backward so moving XDR subsegments into reply pages does not overwrite unprocessed data. Hole segments are zero-filled. LISTXATTRS translates `NFS4ERR_TOOSMALL` to `-ERANGE`, `NFS4ERR_NOXATTR` to success with EOF, and a full caller buffer overflow to `-E2BIG`.

## State and Persistence Behavior

This file has no persistent state beyond static constants. It mutates only RPC request/response buffers and result structures supplied by procedure code. Correctness is state-sensitive because sequence arguments/results, stateids, COPY stateids, cookies, EOF markers, and verifier fields are carried between `nfs42proc.c` and the wire.

## Dependencies and Integration Points

It depends on NFSv4 shared XDR helpers, `nfs42.h` argument/result structures, SUNRPC XDR stream APIs, pNFS layout-private encoder callbacks, xattr UAPI constants, and NFS procedure table macros. Its encoders/decoders are selected by `nfs4_procedures[]` entries for NFSv4.2 procedure IDs.

## Risks and Edge Cases

The highest-risk areas are size calculations, variable-length opaque data, and page-buffer placement. READ_PLUS must clip segments to the requested range and preserve EOF semantics. GETXATTR validates returned length against received page capacity. LISTXATTRS must add `user.` prefixes locally and enforce both `XATTR_NAME_MAX` and caller buffer bounds.

## Test Signals

Wire-level tests should cover sparse READ_PLUS data/hole mixes, COPY synchronous and async replies, OFFLOAD_STATUS no-completion and error-completion cases, COPY_NOTIFY with NETADDR, SEEK EOF behavior, xattr boundary lengths, LISTXATTRS pagination and overflow, and malformed server lengths.
