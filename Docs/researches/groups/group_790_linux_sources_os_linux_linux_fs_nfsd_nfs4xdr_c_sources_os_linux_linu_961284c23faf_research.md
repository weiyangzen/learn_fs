# Group Research: group_790_linux_sources_os_linux_linux_fs_nfsd_nfs4xdr_c_sources_os_linux_linu_961284c23faf

Scope: `Docs/research_subset_a.md`; all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4xdr.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4xdr.c

## Summary
Implements server-side XDR decode and encode for Linux NFSD's NFSv4 protocol engine. It translates NFSv4 COMPOUND request wire data into `nfsd4_*` operation structures, validates operation arguments, estimates reply reservations and duplicate-reply-cache needs, encodes operation results, and handles the large NFSv4 file attribute surface for NFSv4.0, v4.1, and v4.2.

This mainline copy includes casefold-aware attribute handling for `FATTR4_CASE_INSENSITIVE`, `FATTR4_CASE_PRESERVING`, and `FATTR4_HOMOGENEOUS`, including READDIR caching of case attributes for non-directory children.

## Main APIs
- Request decode and cleanup: `nfs4svc_decode_compoundargs()`, `nfsd4_release_compoundargs()`.
- Reply encode: `nfs4svc_encode_compoundres()`, `nfsd4_encode_operation()`, `nfsd4_encode_replay()`.
- Attribute encoding helper: `nfsd4_encode_fattr_to_buf()`.
- Reply sizing: `nfsd4_check_resp_size()`.
- Supported attribute table: `nfsd_suppattrs`.

## Decode Path
The decoder starts with helpers for counted opaques, path components, NFS times, verifiers, bitmaps, stateids, clientids, owner strings, ACLs, security labels, callback security parameters, and optional POSIX ACL structures. Temporary decoded data is attached to `nfsd4_compoundargs.to_free` via `svcxdr_tmpalloc()` and released after compound processing.

`nfsd4_decode_fattr4()` is the central SETATTR/CREATE/OPEN attribute decoder. It rejects unsupported writable attributes, decodes size, NFSv4 ACLs, mode, owner/group names through idmapping, access/modify times, security labels, NFSv4.2 delegated timestamps, `mode_umask`, and optional POSIX default/access ACLs. It validates that the encoded `attrlist4` length exactly matches the consumed stream length.

Per-operation decoders populate `union nfsd4_op_u` for classic NFSv4.0 operations, v4.1 sessions/pNFS/stateid operations, v4.2 copy/clone/fallocate/seek/read-plus operations, and RFC 8276 xattr operations. Unsupported or configuration-disabled operations are mapped to `nfserr_notsupp`.

`nfsd4_decode_compound()` decodes the compound tag, minor version, client operation count, opnums, and operation bodies through `nfsd4_dec_ops`. It caps operation count, allocates a larger op array when required, rejects opnums outside the negotiated minor version, traces decode errors, computes maximum reply reservation, chooses duplicate-reply-cache behavior for NFSv4.0, and disables splice reads when compound layout or reply size makes them unsafe.

## Encode Path
The encoder includes low-level writers for filehandles, NFS times, device numbers, change info, network addresses, path components, filesystem locations/referrals, NFSv4 ACL entries, security labels, POSIX ACLs, stateids, sessionids, and lock-denied records.

`nfsd4_encode_fattr4()` is the main attribute encoder. It makes a mutable copy of the requested bitmap, handles migrated/referral exports, checks delegation GETATTR conflicts for size/change/time attributes, gathers `vfs_getattr()` and `vfs_statfs()` data, composes a temporary filehandle when needed, fetches NFSv4 ACLs, security labels, POSIX ACLs, and emits the bitmap plus attribute value list by iterating `nfsd4_enc_fattr4_encode_ops`.

This file’s mainline-specific case attribute logic calls `nfsd_get_case_info()` when clients request case-insensitive or case-preserving attributes. GETATTR and other single-dentry callers probe the target dentry directly. READDIR passes `rd_case_cache` so non-directory children can reuse the parent directory’s casefold answer; crossed mount entries bypass that cache. Filesystems without explicit case-state support return POSIX defaults, while other probe failures fail the operation. `FATTR4_HOMOGENEOUS` reports false for superblocks with Unicode encoding because casefold-capable filesystems can vary case behavior by directory.

Directory replies are encoded by `nfsd4_encode_dirlist4()` and `nfsd4_encode_entry4()`. They skip `.` and `..`, delay cookie backpatching until the next entry is known, optionally cross mountpoints, encode requested per-entry attributes, use `RDATTR_ERROR` when allowed, enforce both `dircount` and `maxcount`, and preserve the casefold cache only for entries that remain under the directory being read.

Read replies have two data paths. `nfsd4_encode_splice_read()` uses splice-capable file operations for a single safe READ in a compound, while `nfsd4_encode_readv()` reads into the XDR page vector for ordinary or multiple reads. `READ_PLUS` currently emits a DATA segment when not already at EOF.

Operation result encoders are dispatched through `nfsd4_enc_ops`. They cover stateful replies such as OPEN delegations, LOCK denied data, CREATE/REMOVE/RENAME change info, SETCLIENTID, EXCHANGE_ID, CREATE_SESSION, SEQUENCE, TEST_STATEID, pNFS layout responses, server-to-server copy responses, offload status, seek, and extended attribute result bodies.

`nfsd4_encode_operation()` writes opnum and status, invokes operation-specific encoders when needed, commits or truncates XDR output on resource/reply-too-big errors, maps a few internal statuses to protocol statuses, saves replay data for NFSv4.0 stateowners, calls operation release hooks, and updates `rq_next_page`.

## NFSv4 Feature Coverage
- NFSv4.0: classic compound ops, OPEN/CLOSE/LOCK seqids, SETCLIENTID, RENEW, RELEASE_LOCKOWNER, and stateowner replay caching.
- NFSv4.1: sessions, SEQUENCE, channel attributes, EXCHANGE_ID state protection, backchannel security parameters, TEST/FREE_STATEID, directory delegations, and pNFS when enabled.
- NFSv4.2: ALLOCATE/DEALLOCATE, COPY/COPY_NOTIFY/OFFLOAD_STATUS, READ_PLUS, SEEK, CLONE, delegated timestamp attrs, clone block size, xattr support, open argument reporting, and POSIX ACL extension attributes.
- Optional kernel features: `CONFIG_NFSD_PNFS`, `CONFIG_NFSD_V4_SECURITY_LABEL`, and `CONFIG_NFSD_V4_POSIX_ACLS`.

## Dependencies
Uses SunRPC `xdr_stream`/`xdr_buf`, svc request/reply reservation and payload marking, VFS lookup/stat/statfs/read helpers, export lookup and access checks, idmapping helpers, NFSv4 ACL conversion, LSM security labels, POSIX ACL APIs, NFSD file cache objects, NFSv4 state/delegation helpers, pNFS layout ops, xattr APIs, casefold probing via `nfsd_get_case_info()`, and NFSD tracepoints.

Local headers include `idmap.h`, `acl.h`, `xdr4.h`, `vfs.h`, `state.h`, `cache.h`, `netns.h`, `pnfs.h`, `filecache.h`, `nfs4xdr_gen.h`, and `trace.h`.

## Risks
XDR buffer accounting is the central invariant. Every decoder must consume exactly the wire representation and every encoder must reserve enough room, backpatch lengths/cookies/status fields correctly, and truncate partial results only where protocol-safe.

Attribute handling is subtle because the requested bitmap is modified based on export migration, filesystem capabilities, ACL support, security-label support, birthtime availability, pNFS configuration, and casefold state. Incorrect filtering can produce protocol-inconsistent GETATTR/READDIR replies.

The casefold-aware path depends on probing the right dentry. READDIR deliberately probes the held parent directory for non-directory children to avoid racing with child renames, but crossed mount entries must not reuse that cache. This is a correctness-sensitive protocol-visible behavior.

Read, READ_PLUS, READDIR, xattr, and pNFS replies interact with page-vector output, direct placement, payload marking, client maxcount limits, and session reply-size limits. Mistakes can cause short replies, `NFS4ERR_REP_TOO_BIG`, stale buffer contents, or non-idempotent operations after partial encoding.

NFSv4.0 replay behavior depends on caching only the correct already-encoded result body. Session-based NFSv4.1+ avoids the DRC but adds slot/cache-size constraints that must be honored during encode.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4xdr_gen.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4xdr_gen.c

## Summary
Generated `xdrgen` support code for a subset of NFSv4.1 XDR declarations used by NFSD's hand-written `nfs4xdr.c`. It is generated from `Documentation/sunrpc/xdr/nfs4_1.x` and explicitly warns that manual edits will be lost.

## Main APIs
- `xdrgen_decode_fattr4_open_arguments()` / `xdrgen_encode_fattr4_open_arguments()`.
- `xdrgen_decode_fattr4_time_deleg_access()` / `xdrgen_encode_fattr4_time_deleg_access()`.
- `xdrgen_decode_fattr4_time_deleg_modify()` / `xdrgen_encode_fattr4_time_deleg_modify()`.
- `xdrgen_decode_aclmodel4()` / `xdrgen_encode_aclmodel4()`.
- `xdrgen_decode_aclscope4()` / `xdrgen_encode_aclscope4()`.
- `xdrgen_decode_posixacetag4()` / `xdrgen_encode_posixacetag4()`.
- `xdrgen_decode_posixaceperm4()` / `xdrgen_encode_posixaceperm4()`.

## Behavior
The file wraps generic xdrgen builtins for integers, booleans, hyper values, opaque strings, UTF-8 strings, bitmaps, and NFS times, then layers NFSv4-specific enum validation and structure traversal on top.

Enum decoders validate incoming values for open argument bit categories, delegation types, ACL models, ACL scopes, and POSIX ACL tags before storing them. Encoders write enum values directly as u32s because local callers are expected to provide valid constants.

The exported open-arguments encoder/decoder handles five bitmap arrays describing supported OPEN share access, share deny, delegation-want, claim, and create-mode choices. Delegated timestamp attributes are encoded/decoded as NFS time structures. POSIX ACL helper functions encode/decode tag, permission, and owner-name elements, with internal array helpers for default and access ACL forms.

## Dependencies
Includes Linux SunRPC svc/XDR headers, `nfs4xdr_gen.h`, and generated xdrgen type definitions from `linux/sunrpc/xdrgen/nfs4_1.h`.

## Risks
This file must stay synchronized with the generated header and the XDR specification. Bounds for generated bitmap and array element storage are determined by generated type definitions, so callers must use those structures as intended.

Because only a subset of generated helpers is exported, `nfs4xdr.c` still owns most protocol-specific validation, memory allocation, and Linux object conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4xdr_gen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4xdr_gen.h -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4xdr_gen.h

## Summary
Generated header declaring the `xdrgen` helper functions consumed by NFSD NFSv4 XDR code.

## Contents
The header includes Linux base types, SunRPC XDR declarations, xdrgen builtins, and generated NFSv4.1 type definitions. It declares encode/decode helpers for open-arguments attributes, delegated access/modify times, ACL model/scope enums, POSIX ACL tags, and POSIX ACL permissions.

## Important Details
The include guard is `_LINUX_XDRGEN_NFS4_1_DECL_H`. Comments identify `Documentation/sunrpc/xdr/nfs4_1.x` as the source and state that manual edits will be lost.

## Risks
Consumers depend on this header matching `nfs4xdr_gen.c` and the generated xdrgen type headers. Manual changes would be overwritten and could desynchronize the NFSv4 XDR helper ABI inside NFSD.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4xdr_gen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfscache.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfscache.c

## Summary
Implements NFSD's duplicate reply cache, used to recognize retransmitted non-idempotent RPC calls and either replay a saved reply or drop duplicate in-progress requests. The cache is per NFSD network namespace, with hash buckets backed by red-black trees for lookup and per-bucket LRU lists for pruning.

## Main APIs
- Slab lifecycle: `nfsd_drc_slab_create()`, `nfsd_drc_slab_free()`.
- Per-net lifecycle: `nfsd_reply_cache_init()`, `nfsd_reply_cache_shutdown()`.
- Request path: `nfsd_cache_lookup()`, `nfsd_cache_update()`.
- Observability: `nfsd_reply_cache_stats_show()`.

## Data Model
Each bucket is `struct nfsd_drc_bucket`, containing an rb-tree, LRU list, and spinlock. Cache entries are `struct nfsd_cacherep` objects allocated from `drc_slab`; they carry a key made from XID, procedure, peer address/port, transport protocol, NFS version, argument length, and a weak checksum of the request payload.

Entries move through unused, in-progress, and done states. Reply types include no-cache, status-only replies, and short reply buffers. The implementation records whether the original request was secure so an insecure retransmission cannot read a cached secure reply.

## Behavior
`nfsd_reply_cache_init()` sizes the cache from available low memory, caps it at 256k entries, chooses a power-of-two bucket count targeting about eight entries per bucket, allocates the bucket table, and registers a shrinker named for the NFSD net namespace.

`nfsd_cache_lookup()` first skips work when the current thread-local cache type is `RC_NOCACHE`. Otherwise it computes a checksum over the leading RPC/NFS call bytes, preallocates a candidate entry, hashes by XID, and inserts or finds a matching rb-tree node under the bucket lock. On a miss it marks the entry `RC_INPROG`, prunes a few expired entries, updates miss and memory stats, and returns `RC_DOIT`. On a hit it drops the unused candidate, returns `RC_DROPIT` for in-progress duplicates, or appends/replays the cached status or buffer when safe.

`nfsd_cache_update()` finalizes an in-progress entry after dispatch. It refuses to cache missing status pointers, XDR failures, or replies larger than 256 bytes from the status pointer onward. Status-only replies store one status word; buffer replies allocate and copy the encoded status-plus-result segment. The entry is moved to the LRU tail and marked done.

The shrinker and shutdown paths prune entries through `nfsd_prune_bucket_locked()` and dispose them outside bucket lists. Pruning removes expired entries and also brings the cache back under its max-entry limit. Memory usage, hit/miss counters, not-cached counts, payload checksum misses, longest rb-chain length, and cache size at longest chain are exposed via `nfsd_reply_cache_stats_show()`.

## Dependencies
Uses Linux slab/vmalloc allocation, per-net NFSD state, rb-trees, lists, spinlocks, shrinkers, jiffies expiry, SunRPC request/reply buffers, socket address helpers, XDR buffer subsegments, page access, TCP-style checksum helpers, NFSD stats counters, and NFSD tracepoints.

Local headers are `nfsd.h`, `cache.h`, and `trace.h`.

## Risks
Cache-key correctness is essential. XID reuse is only safe because the key also includes address, port, protocol, version, procedure, argument length, and checksum. The checksum is deliberately weak, so payload mismatches are traced and counted but are not a cryptographic guard.

The cache stores copied reply fragments rather than owning the original RPC send buffer. `nfsd_cache_update()` therefore depends on `statp` pointing into the encoded reply and on the 256-byte cap matching the intended DRC memory tradeoff.

Locking is per bucket. Entries must be unlinked from both rb-tree and LRU under the bucket lock, while freeing and buffer deallocation happen after unlinking. Shrinker, shutdown, lookup pruning, and update paths share these invariants.

The current limit is per container/network namespace, so total memory can scale with the number of active NFSD namespaces despite the per-namespace cap.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfscache.c -->