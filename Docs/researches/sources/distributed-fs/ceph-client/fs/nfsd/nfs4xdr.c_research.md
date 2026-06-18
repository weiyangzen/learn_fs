# sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr.c` implements server-side XDR decode and encode for NFSD NFSv4 compounds. It turns RPC request XDR streams into `struct nfsd4_op` arrays, validates protocol-level fields before operation execution, estimates reply space and duplicate-reply-cache needs, and later encodes NFSv4.0, v4.1, v4.2, pNFS, extended attribute, security label, delegation, and POSIX ACL results back into the RPC response stream. The source was read as a complete 6405-line file.

## Important APIs, Types, and Functions

The externally visible entry points are `nfs4svc_decode_compoundargs()`, `nfs4svc_encode_compoundres()`, `nfsd4_encode_operation()`, `nfsd4_encode_replay()`, `nfsd4_release_compoundargs()`, `nfsd4_check_resp_size()`, and `nfsd4_encode_fattr_to_buf()`. They are called by the NFSD RPC dispatch/procedure layer to decode request arguments, encode per-operation results, emit replayed stateowner results, release temporary decode allocations, and encode attribute sets into temporary buffers.

Important decode helpers include `svcxdr_tmpalloc()`, `svcxdr_dupstr()`, and `svcxdr_savemem()` for compound-lifetime memory; `check_filename()` for path-component validation; basic decoders for component strings, opaques, times, verifier, stateid, clientid, bitmaps, ACLs, callback security, and NFSv4.1 session IDs; `nfsd4_decode_fattr4()` for SETATTR/CREATE/OPEN attribute lists; and one decoder per operation in `nfsd4_dec_ops[]`.

Important encode helpers include scalar encoders for filehandles, nfstime, change info, clientid, stateid, sessionid, fs locations, security labels, ACLs, POSIX ACLs, and bitmaps. `struct nfsd4_fattr_args` aggregates all VFS/export/state used while encoding attributes. `nfsd4_enc_fattr4_encode_ops[]` maps fattr bit numbers to attribute encoder callbacks. `nfsd4_enc_ops[]` maps operation numbers to result encoders, while `nfsd4_map_status()` adjusts a few status codes for protocol-version compatibility.

## Control Flow

Decode starts in `nfs4svc_decode_compoundargs()`, which initializes the compound args, disables `RQ_USEDEFERRAL` to avoid NFSv4 compound/session-slot deferral hazards, and delegates to `nfsd4_decode_compound()`. The compound decoder reads the tag, minor version, client op count, allocates a larger operation array with `vcalloc()` when needed, validates op numbers against minor-version limits, and invokes the appropriate entry in `nfsd4_dec_ops[]`. It stops decoding at the first per-op decode error, records trace information, accumulates worst-case reply sizing, disables v4.0 DRC caching for v4.1+ sessions, reserves response/auth space with `svc_reserve_auth()`, and decides whether splice-based reads are safe.

Operation decoders are mostly strict XDR parsers that populate the corresponding union member. They gate obsolete v4.0-only operations from v4.1+, gate v4.1/v4.2-only claim and session fields from older minor versions, validate enum ranges, reject invalid share-access/share-deny combinations, bound variable-length fields, and save scratch-backed data into temporary memory when necessary. `nfsd4_decode_fattr4()` is a central path: it decodes the writable attribute bitmap, rejects unsupported or read-only writes, decodes attrlist length, fills `iattr`, security labels, NFSv4 ACLs, POSIX ACLs, delegated atime/mtime attributes, and verifies that the decoded byte count exactly matches `attrlist4_count`.

Encode of individual operation results starts in `nfsd4_encode_operation()`. It writes the op number and reserves the status word, skips trivial error bodies, invokes the selected encoder from `nfsd4_enc_ops[]`, commits the stream, checks remaining reply/session space, maps `nfserr_resource` to v4.1 session `rep_too_big` variants when appropriate, truncates partial encodings for resource errors, optionally saves stateowner replay bytes, writes the final mapped status, releases operation resources through the operation descriptor, and updates `rq_next_page`.

Attribute encoding starts in `nfsd4_encode_fattr4()`. It copies the requested bitmap, handles absent/migrated filesystem referrals, resolves delegation conflicts for size/change/time attributes, obtains VFS stats and statfs data only when needed, composes a temporary filehandle when no current fh exists, fetches NFSv4 ACL/security label/POSIX ACL state conditionally, emits the resulting attribute bitmap, reserves the attr length field, iterates the bitmap through `nfsd4_enc_fattr4_encode_ops[]`, then backfills the encoded length. On failure it releases all temporary ACL/security/filehandle state and truncates the XDR stream to the starting length.

## State and Persistence Behavior

This file owns no persistent on-disk state. It manages transient per-RPC decode and encode state in `struct nfsd4_compoundargs`, `struct nfsd4_compoundres`, and operation-specific union members. Temporary decode allocations are chained in `argp->to_free` and freed by `nfsd4_release_compoundargs()`. Large operation arrays are allocated only for compounds exceeding the inline `iops` capacity and released after processing.

Persistent effects are indirect: decoded operations drive NFSD state, VFS mutations, client/session/delegation state, xattr changes, and pNFS work in other files. Encoded replies can also feed replay persistence in memory: `nfsd4_encode_operation()` copies the encoded operation payload into `nfs4_stateowner.so_replay` for stateowner replay, while v4.1 session DRC offsets are established when encoding `OP_SEQUENCE`.

## Dependencies and Integration Points

The file depends on Linux SUNRPC XDR stream APIs, NFSD protocol definitions in `xdr4.h`, operation descriptors and execution state in `state.h`, VFS helpers in `vfs.h`, export and net namespace state, idmapping, security label support, ACL conversion, pNFS layout operations, NFSD filecache/read/write helpers, xattr APIs, and tracepoints. It includes `nfs4xdr_gen.h` for generated encoders/decoders used by NFSv4.1 extension attributes and POSIX ACL extension values.

Important runtime integration points include `nfsd4_proc_compound()`/RPC dispatch for top-level decode/encode, the duplicate reply cache via `ntli->ntli_cachetype`, the v4.1 session slot layer through `nfsd4_has_session()`, `nfsd4_sequence_done()`, and slot cache flags, idmapping through `nfsd_map_name_to_uid()` and `nfsd_map_name_to_gid()`, export traversal through `rqst_find_fsidzero_export()` and cross-mount helpers, and VFS stat/statfs/getattr/xattr operations for fattr and xattr replies.

## Risks and Edge Cases

This file is exposed to untrusted network input, so XDR bounds, enum validation, attrlist length checks, bitmap handling, and temporary-memory lifetime are high-risk. Scratch-buffer data must be copied when stable storage is required; otherwise later XDR stream movement can invalidate pointers. Minor-version gating mistakes can expose unsupported operations or reject valid protocol forms. Attribute encoding has many conditional paths where unsupported filesystem features should clear requested bits or return protocol-specific errors without corrupting the response stream.

Reply-size handling is delicate. Some encoders write partial results before discovering a space problem, so truncation must occur only for operations whose error bodies are trivial. READ, READ_PLUS, READDIR, xattr, and pNFS layout encoders manipulate page-backed XDR buffers and direct-placement metadata, making off-by-one and padding errors especially risky. `nfs4svc_decode_compoundargs()` intentionally disables deferral because decode-time cache lookups can otherwise leak v4.1 session slots if `RQ_DROPME` is set before encoding.

## Test Signals

Useful test coverage includes NFSv4.0/v4.1/v4.2 connectathon and pynfs suites, malformed XDR fuzzing, minor-version operation-boundary tests, ACL/POSIX ACL/security label attribute tests, GETATTR/READDIR attr bitmap combinations, READ/READ_PLUS splice and non-splice paths, xattr RFC 8276 operations with large values and cookies, pNFS layout operations with and without `CONFIG_NFSD_PNFS`, and response-size exhaustion under v4.1 sessions. Runtime signals include `trace_nfsd_compound_decode_err`, `trace_nfsd_compound_encode_err`, stateowner replay traces, warnings from non-idempotent truncation, and KASAN/KMSAN reports from malformed network input.
