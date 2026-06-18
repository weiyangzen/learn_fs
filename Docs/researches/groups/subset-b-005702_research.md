# subset-b-005702 Research

Grouped source research for the NFS server NFSv4 XDR encoder/decoder, generated XDR helpers for NFSv4.1 extension types, and the NFSD duplicate reply cache. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.c` is generated XDR helper code for selected NFSv4.1 XDR specification types. It provides type-safe decode and encode functions consumed by `nfs4xdr.c` for open-argument capability attributes, delegated timestamp attributes, ACL model/scope enums, and POSIX ACL extension structures. The source was read as a complete 569-line generated file.

## Important APIs, Types, and Functions

The exported functions are `xdrgen_decode_fattr4_open_arguments()`, `xdrgen_encode_fattr4_open_arguments()`, `xdrgen_decode_fattr4_time_deleg_access()`, `xdrgen_encode_fattr4_time_deleg_access()`, `xdrgen_decode_fattr4_time_deleg_modify()`, `xdrgen_encode_fattr4_time_deleg_modify()`, `xdrgen_decode_aclmodel4()`, `xdrgen_encode_aclmodel4()`, `xdrgen_decode_aclscope4()`, `xdrgen_encode_aclscope4()`, `xdrgen_decode_posixacetag4()`, `xdrgen_encode_posixacetag4()`, `xdrgen_decode_posixaceperm4()`, and `xdrgen_encode_posixaceperm4()`.

Internal helpers cover generated primitive aliases (`int64_t`, `uint32_t`, `bitmap4`, UTF-8 string aliases, `nfstime4`), enum decoders for open share access/deny/want/claim/create modes, `open_delegation_type4`, ACL model/scope, POSIX ACE tags, and compound structures such as `open_arguments4`, `posixace4`, `fattr4_posix_default_acl`, and `fattr4_posix_access_acl`.

## Control Flow

Decode helpers read from `struct xdr_stream` in XDR field order and return `false` on short stream, malformed enum value, or failed nested decode. Array helpers first decode `count` and then iterate `count` elements using the generated element decoder. Enum decoders read a `u32`, switch over the allowed constants, reject unknown values, and assign the typed enum only after validation.

Encode helpers mirror the decode layout. They write counts before array elements, serialize enum values as `u32`, encode `nfstime4` as signed seconds plus unsigned nanoseconds, and encode UTF-8 string aliases with `xdr_stream_encode_opaque()`. Public wrappers simply delegate to the generated structure/alias implementation for the corresponding XDR typedef.

## State and Persistence Behavior

The file keeps no global mutable state and performs no persistence. It only advances an XDR stream and populates caller-owned structures or reads caller-owned values. The generated bitmap and array types assume their `element` pointers are supplied by the caller and have enough storage for the decoded `count`; this contract is inherited from the generated XDR type definitions in the included headers.

## Dependencies and Integration Points

The file depends on `linux/sunrpc/svc.h`, `nfs4xdr_gen.h`, generic xdrgen builtins, and generated NFSv4.1 type definitions. Its primary consumer in this subset is `nfs4xdr.c`: delegated time attributes use the generated time decoders, OPEN_ARGUMENTS uses generated bitmap encoders, and POSIX ACL extension decode/encode paths use generated POSIX ACE tag and permission helpers.

Because it is generated from `Documentation/sunrpc/xdr/nfs4_1.x`, the source of truth is the XDR specification and generator, not this C file. Manual edits would be overwritten and should instead be made in the specification or xdrgen tooling.

## Risks and Edge Cases

The biggest risk is array bounds: generated decode loops trust the destination array layout associated with generated `bitmap4` and fattr array types. Callers must provide storage consistent with the decoded count or ensure upstream XDR definitions cap it. Enum decoders are stricter than simple casts, which is good for protocol hardening but can reject values if the XDR specification evolves without regenerating this file.

For encode paths, most enum encoders do not revalidate the enum value and simply write it; callers must avoid passing untrusted or uninitialized enum values. Generated UTF-8 helpers encode opaque bytes and do not validate Unicode semantics. The file uses `__maybe_unused` for many helpers because generation may emit support code for types not currently referenced by NFSD.

## Test Signals

Useful signals are build coverage after regenerating from `nfs4_1.x`, round-trip XDR tests for each exported helper, malformed enum decode tests, array count boundary tests, and integration tests through `nfs4xdr.c` for OPEN_ARGUMENTS, delegated timestamp setattr, and POSIX ACL extension attributes. Static analysis should focus on generated array element storage contracts and return-value handling by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.h

## Purpose

`sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.h` declares the generated XDR helper interface used by NFSD NFSv4 XDR code. It exposes encode/decode prototypes for a small set of generated NFSv4.1 and extension types while hiding the generated helper implementation in `nfs4xdr_gen.c`. The source was read as a complete 35-line generated header.

## Important APIs, Types, and Functions

The header includes Linux integer types, SUNRPC XDR stream declarations, xdrgen definitions/builtins, and generated `linux/sunrpc/xdrgen/nfs4_1.h` type declarations. It declares bool-returning encode/decode helpers for `fattr4_open_arguments`, `fattr4_time_deleg_access`, `fattr4_time_deleg_modify`, `aclmodel4`, `aclscope4`, `posixacetag4`, and `posixaceperm4`.

All functions take a `struct xdr_stream *` plus either a mutable destination pointer for decode or a value/const pointer for encode. The enum/value helpers use typed generated aliases such as `aclmodel4`, `aclscope4`, `posixacetag4`, and `posixaceperm4`.

## Control Flow

The header has no executable control flow. Compile-time include guards prevent duplicate declarations, and consumers call into `nfs4xdr_gen.c` for the actual stream manipulation and validation.

## State and Persistence Behavior

The header defines no state and performs no persistence. It is part of the build-time ABI between generated XDR helper implementation and handwritten NFSD XDR code.

## Dependencies and Integration Points

The primary handwritten integration point is `nfs4xdr.c`, which includes this header to use generated helpers for POSIX ACL extension values, delegated timestamp attributes, ACL trueform/scope values, and OPEN_ARGUMENTS capability encoding. The header is generated from `Documentation/sunrpc/xdr/nfs4_1.x`; manual modifications are explicitly marked as non-durable.

## Risks and Edge Cases

Prototype drift between this header, `nfs4xdr_gen.c`, generated `nfs4_1.h` types, and handwritten `nfs4xdr.c` would cause compile failures or subtle ABI mismatches. Because all helpers return `bool`, callers must map failures to protocol errors consistently, usually `nfserr_bad_xdr` for decode and `nfserr_resource` for encode.

## Test Signals

Compile coverage is the primary signal for declaration compatibility. Integration tests that exercise POSIX ACL extension attributes, delegated timestamp setattrs, and OPEN_ARGUMENTS fattr encoding verify that the generated declarations remain aligned with both generated implementation and handwritten call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfscache.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfscache.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfsd/nfscache.c` implements the NFSD duplicate reply cache (DRC). The cache detects retransmitted non-session NFS RPC calls, drops duplicate in-progress requests, and replays cached replies for completed requests when safe. It also sizes, initializes, prunes, shrinks, updates, and reports statistics for the per-network-namespace reply cache. The source was read as a complete 667-line file.

## Important APIs, Types, and Functions

Public entry points are `nfsd_drc_slab_create()`, `nfsd_drc_slab_free()`, `nfsd_reply_cache_init()`, `nfsd_reply_cache_shutdown()`, `nfsd_cache_lookup()`, `nfsd_cache_update()`, and `nfsd_reply_cache_stats_show()`. `struct nfsd_drc_bucket` contains the per-bucket rb-tree root, LRU list, and spinlock. Cache entries are `struct nfsd_cacherep` objects allocated from the global `drc_slab`; they carry request key fields, state (`RC_UNUSED`, `RC_INPROG`, `RC_DONE`), reply type (`RC_NOCACHE`, `RC_REPLSTAT`, `RC_REPLBUFF`), secure-request flag, timestamp, rb-node, LRU node, and cached reply payload/status.

Important helpers include `nfsd_cache_size_limit()` and `nfsd_hashsize()` for sizing, `nfsd_cacherep_alloc()`/`nfsd_cacherep_free()` for entry lifetime, `nfsd_cacherep_unlink_locked()` for unlinking and accounting, `nfsd_prune_bucket_locked()` and shrinker callbacks for reclamation, `nfsd_cache_csum()` for weak checksums over request headers, `nfsd_cache_key_cmp()` and `nfsd_cache_insert()` for rb-tree lookup/insert, and `nfsd_cache_append()` for replaying cached reply buffers into an XDR response stream.

## Control Flow

Initialization uses `nfsd_reply_cache_init()` per `struct nfsd_net`: compute a max entry limit from low memory, round bucket count up based on `TARGET_BUCKET_SIZE`, allocate the bucket table with `kvzalloc()`, allocate/register a shrinker, initialize bucket LRUs and locks, and store hash metadata. Shutdown unregisters/frees the shrinker, walks each bucket LRU, frees all cache entries under bucket locks, and releases the bucket table.

Lookup starts in `nfsd_cache_lookup()`. If the current procedure's thread-local cache type is `RC_NOCACHE`, the function records a no-cache stat and returns `RC_DOIT`. Otherwise it computes a checksum over the NFS call header, preallocates a candidate entry, selects a bucket by XID hash, and calls `nfsd_cache_insert()` under the bucket lock. A true miss installs the new entry as `RC_INPROG`, prunes a few old entries from the bucket LRU, drops the lock, disposes pruned entries, accounts a miss, and tells the caller to process normally with `*cacherep` set.

If lookup finds an existing entry, the preallocated candidate is freed, hit stats are incremented, and the default result is `RC_DROPIT`. `RC_INPROG` entries remain drops so another server thread does not process the same RPC concurrently. Completed entries are replayed only if the original secure transport requirements are met; insecure retransmits cannot use replies cached from secure requests. Depending on cached reply type, lookup either does nothing for `RC_NOCACHE`, encodes a cached status word for `RC_REPLSTAT`, or appends a cached reply buffer for `RC_REPLBUFF`, returning `RC_REPLY` when replay succeeds.

Update happens in `nfsd_cache_update()` after procedure execution. It finds the same bucket, computes the word length from the status pointer to the current response head end, rejects excessive replies and encode failures, stores either a single status or a kmalloc-copied reply buffer, then under lock updates memory accounting, moves the entry to the LRU tail, records whether the request was secure, sets the reply type, and marks the entry `RC_DONE`.

## State and Persistence Behavior

The DRC is in-memory, per NFSD network namespace, and not persistent across server restart or netns teardown. Bucket rb-trees provide exact request-key lookup; bucket LRU lists provide age-based pruning. The request key includes XID, procedure, client address and port, transport protocol, RPC version, argument length, and checksum of leading call bytes. The checksum is deliberately weak and used as a key discriminator, not as cryptographic authentication.

Memory accounting is maintained through `atomic_t num_drc_entries` and NFSD stats counters for DRC memory usage, hits, misses, no-cache calls, payload misses, and longest rb-chain observations. Entries expire by `RC_EXPIRE` and are also pruned when the cache exceeds `max_drc_entries` or when the shrinker asks for reclaim.

## Dependencies and Integration Points

The file depends on SUNRPC request/transport structures, XDR buffers and streams, network address helpers, kernel slab/vmalloc/shrinker APIs, rb-trees, list LRUs, spinlocks, checksum helpers, page access, NFSD per-net state in `netns.h`, cache type definitions in `cache.h`, and tracepoints. It integrates with NFSD dispatch through `nfsd_cache_lookup()` before executing a request and `nfsd_cache_update()` after encoding a reply. It also integrates with proc/seq reporting through `nfsd_reply_cache_stats_show()`.

The cache is especially relevant for NFS versions/procedures without NFSv4.1 session replay semantics. `nfs4xdr.c` disables this DRC path for minor versions with sessions, while NFSv2/v3 and NFSv4.0 cacheable operations use the same infrastructure through thread-local `ntli_cachetype`.

## Risks and Edge Cases

The lookup/update path is concurrency-sensitive. The preallocate-then-insert design avoids allocation under the bucket lock but requires freeing the unused candidate correctly on hits. `RC_INPROG` duplicate handling intentionally drops retransmits, so stale in-progress entries must eventually expire or be removed. Reply caching only copies up to 256 bytes from the status pointer region; larger or failed encodings are uncached and the in-progress entry is removed.

Security behavior depends on `c_secure`: replies generated for secure requests are not replayed to insecure retransmits. Request identity relies on address, port, XID, argument length, and checksum; checksum collisions are possible, but mismatching checksums for equal XID are traced and counted. The shrinker scans all buckets and removes only expired or over-limit entries, so memory pressure behavior depends on timestamps and LRU ordering. `nfsd_prune_bucket_locked()` uses a `max` limit but increments after unlinking, so callers should treat it as an approximate pruning bound.

## Test Signals

Useful tests include retransmission/replay tests for cacheable NFS procedures, duplicate in-progress request drops, secure-to-insecure replay denial, large reply no-cache behavior, encode-failure cleanup with `statp == NULL`, shrinker/prune behavior under low memory or forced cache limits, and netns init/shutdown leak checks. Runtime signals include DRC tracepoints for found/mismatch events and `/proc`/seq stats for hits, misses, no-cache calls, payload misses, memory usage, and longest chain length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfscache.c -->
