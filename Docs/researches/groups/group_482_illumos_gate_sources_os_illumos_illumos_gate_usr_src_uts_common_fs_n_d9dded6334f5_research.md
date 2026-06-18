# Group Research: group_482_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_d9dded6334f5

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is in subset A. All five listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_xdr.c

## Purpose

`nfs4_xdr.c` is the hand-written illumos NFSv4 XDR implementation for the kernel NFS client and server. It serializes and deserializes NFSv4 compound arguments/results, filehandles, bitmaps, attributes, stateids, lock/open payloads, READ/WRITE data, READDIR streams, callback compounds, and selected NFSv4.1 extension operations through `nfs4x_xdr.c` hooks.

The file is performance-sensitive protocol plumbing. It uses inline XDR fast paths, direct decode into kernel objects such as `vattr_t` and `dirent64_t`, RDMA chunk registration/validation, mblk stream support, and custom memory-free paths for compound arrays.

## Main Interfaces

Public or externally used routines include:

- Core types: `xdr_bitmap4`, `xdr_utf8string`, `xdr_nfs_fsl_info`, `xdr_knetconfig`, `xdr_nfs_fh4`, `xdr_inline_decode_nfs_fh4`, `xdr_inline_encode_nfs_fh4`
- Attribute types: `xdr_nfsace4`, `xdr_fattr4_fsid`, `xdr_fattr4_acl`, `xdr_fattr4_fs_locations`, `xdr_fattr4_rawdev`, `xdr_nfstime4`, `xdr_fattr4_sec_label`, `xdr_fattr4`, `xdr_settime4`
- Client decode helpers: `xdr_get_bitmap4_inline`, `xdr_READDIR4res_clnt`, `nfs4_init_dot_entries`, `nfs4_destroy_dot_entries`
- Server result helpers: `xdr_READDIR4res`, `xdr_SECINFO4res`
- Compound wrappers: `xdr_COMPOUND4args_clnt`, `xdr_COMPOUND4args_srv`, `xdr_COMPOUND4res_clnt`, `xdr_COMPOUND4res_srv`
- Callback wrappers: `xdr_CB_COMPOUND4args_clnt`, `xdr_CB_COMPOUND4args_srv`, `xdr_CB_COMPOUND4res`

Important private helpers include filehandle encode/decode routines, `xdr_ga_fattr_res`, `xdr_ga_fattr_res_inline`, `xdr_ga_res`, per-operation argument/result XDR routines, `xdr_nfs_argop4`, `xdr_nfs_resop4`, client/server variants for argop/resop processing, and optimized compound-array free functions.

## Filehandle And Bitmap Handling

`xdr_bitmap4()` stores the common NFSv4 bitmap as a local `uint64_t`, while preserving support for NFSv4.1 bit 75 (`FATTR4_SUPPATTR_EXCLCREAT`) by folding it into a local high bit. It always emits two words unless the folded third word is needed, and on decode it consumes and skips extra words so the XDR stream stays synchronized.

Filehandle handling has distinct client and server semantics:

- Client decode through `xdr_nfs_fh4()` treats filehandles as opaque byte arrays.
- Server-side `xdr_decode_nfs_fh4()` and `xdr_encode_nfs_fh4()` understand illumos internal `nfs_fh4_fmt_t` layout.
- Inline decode validates total filehandle size, fid/export lengths, required padding, flags, and absence of trailing bytes.
- Malformed handles are consumed from the stream but returned with zero length so upper NFS layers can reject them cleanly.

## Attribute Decode Model

The main GETATTR decode path is `xdr_ga_res()`, which reads the returned bitmap and attribute-list length, validates server response bitmaps against the requested bitmap, and then decodes attributes through either `xdr_ga_fattr_res()` or the inline fast path `xdr_ga_fattr_res_inline()`.

Decoded data lands primarily in `nfs4_ga_res_t`:

- `vattr_t` fields for file type, mode, uid/gid, size, link count, node id, rdev, times, and block count.
- Extended result data for fsid, filesystem statistics, pathconf-style properties, max read/write sizes, ACL support, lease time, fs locations, filehandle attributes, and mounted-on file id.
- `vsecattr_t` ACL data when `FATTR4_ACL_MASK` is present.

Owner and group string-to-id conversion uses `nfs_idmap_str_uid()` and `nfs_idmap_str_gid()`. A small `ug_cache_t` can cache repeated owner/group names during READDIR attribute decode, reducing repeated idmap work for directories with many entries owned by the same principals.

The code records attribute conversion failures in `n4g_attrerr` and `n4g_attrwhy` rather than necessarily failing raw XDR decode. This distinction lets callers know whether the network stream was valid but local attribute interpretation failed.

## READ, WRITE, RDMA, And mblk Paths

`xdr_READ4args()` encodes stateid, offset, count, and registers RDMA write chunks when the transport supports RDMA. It can describe either a target address buffer or caller-provided `uio`.

`xdr_READ4res()` is server-side encode-only. It supports ordinary byte payloads, prebuilt `mblk_t` payloads, `xdrmblk_ops`, and RDMA write-list data transfer through `xdrrdma_send_read_data()`.

`xdr_READ4res_clnt()` is the client decode path. It handles direct I/O into `uio`, inline memory decode, mblk streams, RDMA write-list length validation, and caller-provided alternate buffers. It rejects payloads larger than the caller-advertised maximum and verifies RDMA transferred length against the opaque count.

`xdr_WRITE4args()` decodes client write requests into ordinary buffers, mblk chains, or RDMA read chunks via `xdrrdma_getrdmablk()` and `xdrrdma_read_from_client()`. Its free path releases RDMA clists. `xdr_WRITE4res()` serializes status, written count, stable mode, and write verifier.

## Directory Handling

`nfs4_init_dot_entries()` prebuilds padded `.` and `..` `dirent64` records. `xdr_READDIR4res_clnt()` uses those records when decoding cookies 0 and 1, then decodes server entries into an `rddir4_cache` buffer.

The READDIR client decode loop:

- Reads cookie, name, attribute bitmap, attribute length, and attributes for each entry.
- Computes `DIRENT64_RECLEN()` before copying names to prevent output-buffer overflow.
- If the caller buffer fills, skips remaining names/attributes while keeping the stream synchronized.
- Sets `d_ino` from mounted-on fileid when available, otherwise from fileid.
- Optionally constructs NFSv4 rnodes and updates DNLC when both attributes and filehandle attributes are present.
- Distinguishes normal EOF, no entries, bad cookies, and too-small buffers through `rdc->error`.

Server-side `xdr_READDIR4res()` emits pre-encoded mblk data and temporarily disables RDMA chunking when needed so the encoded directory block is transferred as intended.

## Compound Operation Processing

The file implements custom NFSv4 compound serialization rather than relying on rpcgen output.

Client argument encoding is optimized by private pseudo-ops such as `OP_CPUTFH`, `OP_CLOOKUP`, `OP_COPEN`, `OP_CREMOVE`, `OP_CCREATE`, `OP_CLINK`, `OP_CRENAME`, and `OP_CSECINFO`. These avoid temporary allocations and encode C strings or shared filehandles directly into the stream.

Server argument decode uses `xdr_snfs_argop4()`, including special server decode for `OP_PUTFH` so internal filehandles are validated. Operations with opcodes at or above `OP_BACKCHANNEL_CTL` are delegated to `xdr_nfs4x_argop4()` in the NFSv4.1 XDR file.

Result handling has three variants:

- `xdr_nfs_resop4()` for generic result encoding/decoding.
- `xdr_snfs_resop4()` for server result encoding, including internal filehandle encode for `OP_GETFH` and NFSv4.1 delegation.
- `xdr_nfs_resop4_clnt()` for client result decode using the matching argop, enabling specialized GETATTR, READ, and READDIR decoding.

`xdr_COMPOUND4res_clnt()` validates response operation count against the request. A successful compound must return exactly the requested operation count; an error compound may return a shorter prefix. It tracks `decode_len` so partially decoded arrays can be safely freed after decode failure.

## Callback Processing

The callback compound routines handle the role reversal between NFS server and NFS client:

- Server-initiated callback arguments use `xdr_snfs_cb_argop4()` and encode internal server filehandles for `CB_GETATTR` and `CB_RECALL`.
- Client-side callback decode uses `xdr_cnfs_cb_argop4()` and treats callback filehandles as opaque.
- Unknown or NFSv4.1 callback operations are delegated to common callback XDR helpers so the server/client can return protocol errors rather than failing XDR prematurely.

## Memory Management And Safety

The file contains many XDR_FREE fast paths to release only fields that can allocate memory: UTF-8 strings, filehandles, ACL arrays, fs locations, SECINFO lists, READLINK strings, denied lock owners, OPEN owners/claims, WRITE buffers, and compound arrays.

Notable defensive properties:

- Bounds are applied to filehandles, UTF-8 strings, ACLs, opaque security labels, READ/WRITE data, and compound operation counts.
- Filehandle decode consumes malformed handles without desynchronizing the stream.
- GETATTR rejects unknown extra response attributes because they cannot be skipped safely without semantic knowledge.
- READDIR continues decoding skipped entries after local buffer exhaustion.
- RDMA read/write counts are validated against protocol counts.
- Free paths tolerate partially decoded arrays and invalid op placeholders.

## Dependencies

This file depends on:

- Core RPC/XDR, RDMA XDR, and mblk XDR support.
- NFSv4 protocol definitions in `nfs4_kprot.h` and related headers.
- NFSv4 client structures such as `mntinfo4_t`, `rnode4_t`, `rddir4_cache`, shared filehandles, and DNLC helpers.
- Attribute conversion helpers in NFSv4 attribute/id mapping code.
- NFSv4.1 operation XDR hooks in `nfs4x_xdr.c`.

## Research Notes

This is a trust-boundary file: untrusted network bytes become kernel filehandles, attributes, directory entries, stateids, locks, and data buffers. The highest-risk areas are inline attribute decoding, READDIR buffer accounting, server internal filehandle validation, compound partial-free behavior, RDMA length checks, and owner/group string mapping interactions with cacheability.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_dispatch.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_dispatch.c

## Purpose

`nfs4x_dispatch.c` is the NFSv4.1 server dispatch wrapper for COMPOUND RPCs. It validates session-oriented compound layout, prepares NFSv4.1 sequence/replay-cache state, calls the common NFSv4 compound executor, and coordinates reply encoding with slot cleanup.

## Main Interfaces

Main functions:

- `rfs4x_dispatch(struct svc_req *req, SVCXPRT *xprt, char *ap)`

Private helpers:

- `rfs4_err_resp()`
- `valid_first_compound_op()`
- `verify_compound_args()`
- `rfs4x_dispatch_done()`
- `xdr_compound_wrapper()`

## Behavior

`verify_compound_args()` enforces the NFSv4.1 session rules for compounds:

- Empty compounds are accepted.
- The first operation must be `OP_BIND_CONN_TO_SESSION`, `OP_SEQUENCE`, `OP_EXCHANGE_ID`, `OP_CREATE_SESSION`, `OP_DESTROY_SESSION`, `OP_DESTROY_CLIENTID`, or `OP_ILLEGAL`.
- If the first operation is not `OP_SEQUENCE`, the request is outside a session and must contain exactly one operation.

`rfs4x_dispatch()` initializes `compound_state_t`, verifies the request, and calls `rfs4x_sequence_prep()`. If sequence preparation reports a replay-cache hit, dispatch skips normal compound execution and sends the cached response. Otherwise it runs `rfs4_compound()` with `T_DONTPEND` set to avoid RPC pending behavior during server compound execution.

## Reply And Cleanup Flow

Replies are sent through `svc_sendreply()` using `xdr_compound_wrapper()`. The wrapper only calls `rfs4x_dispatch_done()` when XDR is encoding real reply data, which matters because some XDR sizing/probing paths should not mutate slot state.

`rfs4x_dispatch_done()` either:

- Calls `rfs4x_sequence_done()` when the compound owns an NFSv4.1 slot, allowing the slot reply cache to be updated and the slot released.
- Frees the compound response directly for non-session compounds.

`RFS4_DISPATCH_DONE` prevents double cleanup if sendreply fails or if the wrapper already completed cleanup.

## Dependencies

This file depends on common NFSv4 server execution (`rfs4_compound`, `rfs4_compound_free`, compound-state init/fini) and NFSv4.1 session helpers in `nfs4x_srv.c`.

## Research Notes

The important invariant is that slot release and response freeing happen after real reply encoding, not merely after response construction. The dispatch code is small, but it is the handoff point between RPC transport behavior and the NFSv4.1 session replay cache.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_dispatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_slrc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_slrc.c

## Purpose

`nfs4x_slrc.c` implements a slot-table abstraction used by NFSv4.1 session/backchannel replay-cache support. It provides allocation, lookup, resize, free, state transitions, cleanup callbacks, and callback-busy checks for `slot_ent_t` objects stored in an AVL tree.

## Main Interfaces

Low-level slot-table functions:

- `sltab_create`, `sltab_destroy`, `sltab_resize`, `sltab_query`, `sltab_set_cleanup`
- `sltab_get`, `slot_alloc`, `slot_delete`, `slot_free`
- `slot_incr_seq`, `slot_cb_status`, `slot_set_state`, `slot_error_to_inuse`

Wrapper names:

- `slot_table_create`, `slot_table_destroy`, `slot_table_resize`, `slot_table_query`, `slot_get`

## Data Structures And Locking

The table token `stok_t` owns:

- An AVL tree of `slot_ent_t` records keyed by slot number.
- Current width (`st_currw`) and free-slot count (`st_fslots`).
- A table mutex and condition variable.
- An optional cleanup callback invoked as slots are deleted.

Each `slot_ent_t` has its own mutex and condition variable, slot number, sequence id, state bits, and client-associated fields.

The intended locking order is table lock first, then slot lock. Creation initializes locks and the AVL tree. Destruction walks the tree and deletes every slot under the table lock.

## Allocation And Resize Behavior

`slot_alloc()` searches slot numbers from zero up to current width. If no node exists for a slot, it creates one with sequence id 1 and `SLOT_INUSE`. If a node exists and is marked `SLOT_FREE`, it transitions it to `SLOT_INUSE`.

With `SLT_NOSLEEP`, allocation fails immediately when no slot is available. With `SLT_SLEEP`, it waits on `st_wait` until `st_fslots` indicates availability, then retries the scan.

`sltab_resize()` supports increasing width by adding to `st_fslots`. When decreasing width, it deletes nodes whose slot numbers exceed the new maximum. Consumers retain only the opaque token and do not see the underlying AVL storage change.

## State And Callback Handling

`slot_free()` marks a slot free, increments the free count, signals waiters, and preserves the slot object for reuse. `slot_incr_seq()` atomically increments the per-slot sequence id.

`slot_cb_status()` is used when destroying sessions with backchannel slots. If any slot is still `SLOT_INUSE`, it returns `NFS4ERR_BACK_CHAN_BUSY`. Otherwise it marks slots free and updates the free count.

`slot_set_state()` ORs new state bits into a slot. `slot_error_to_inuse()` clears `SLOT_ERROR` while requiring both `SLOT_ERROR` and `SLOT_INUSE`.

## Dependencies

This file depends on illumos AVL, mutex, condition-variable, and atomic primitives, plus NFSv4.1 slot types from NFS headers.

## Research Notes

The file is generic slot infrastructure rather than protocol execution. Audit-sensitive areas are free-slot accounting during resize/delete/free, lock ordering around AVL lookup and slot mutation, and callback-busy detection before session teardown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_slrc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_srv.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_srv.c

## Purpose

`nfs4x_srv.c` implements server-side NFSv4.1 operation handlers and session helpers layered on the existing NFSv4 server state machinery. It covers EXCHANGE_ID, CREATE_SESSION, DESTROY_SESSION, SEQUENCE, RECLAIM_COMPLETE, DESTROY_CLIENTID, BIND_CONN_TO_SESSION, SECINFO_NO_NAME, TEST_STATEID, FREE_STATEID, BACKCHANNEL_CTL, callback security handling, delegation request conversion, and recallable-state race tracking.

## Main Interfaces

Credential/principal helpers:

- `rfs4_cmp_cred_set`, `rfs4_set_cred_set`, `rfs4_free_cred_set`
- `nfs_clid4_cmp`

Operation handlers:

- `rfs4x_op_exchange_id`
- `rfs4x_op_create_session`
- `rfs4x_op_destroy_session`
- `rfs4x_op_sequence`
- `rfs4x_op_reclaim_complete`
- `rfs4x_op_destroy_clientid`
- `rfs4x_op_bind_conn_to_session`
- `rfs4x_op_secinfo_noname`
- `rfs4x_op_test_stateid`
- `rfs4x_op_free_stateid`
- `rfs4x_op_backchannel_ctl`

Session/replay helpers:

- `rfs4x_sequence_prep`
- `rfs4x_sequence_done`
- `rfs4x_cbcheck`
- `rfs4x_bc_setup`
- `rfs4x_exchange_id_free`

Backchannel and delegation helpers:

- `rfs4x_cbsec_valid`, `rfs4x_cbsec_getuid`, `rfs4x_cbsec_getgid`, `rfs4x_cbsec_init`, `rfs4x_cbsec_fini`
- `nfs4x_share_to_delegreq`
- `rfs4x_rs_record`, `rfs4x_rs_erase`

## Client Identity And EXCHANGE_ID

`rfs4x_op_exchange_id()` implements the RFC 5661 EXCHANGE_ID client-record cases. It validates flags, constructs an `nfs_client_id4` from the client owner and RPC caller address, finds or creates the server client record, handles unconfirmed and confirmed records, detects verifier changes, compares credentials/principals, and returns `CLID_INUSE`, `NOENT`, `NOT_SAME`, `PERM`, or `SERVERFAULT` where appropriate.

The handler stores the credential/principal set on new client records, records clientid information in stable storage, reports non-pNFS server behavior, echoes referral support when requested, rejects SSV state protection as unsupported, and fills server implementation/trunking identity. `rfs4x_exchange_id_free()` releases allocated implementation and server-owner response strings.

## Session Creation And Destruction

`rfs4x_op_create_session()` finds the clientid, rejects expired clients, handles sequence-id replay/misorder cases using the client's contrived sequence/result state, confirms unconfirmed clientids when credentials match, creates the session via `rfs4x_createsession()`, caches the CREATE_SESSION result for replay, increments the client sequence, updates the lease, and releases temporary references.

`rfs4x_op_destroy_session()` validates RFC rules when destroying the same session used by the enclosing SEQUENCE: it must be the final operation in the compound. It then finds the session, enforces state-protection credential checks when required, and calls `rfs4x_destroysession()` with an adjusted reference count.

`rfs4x_op_destroy_clientid()` rejects unknown clientids and clientids with sessions or openowners, otherwise marks the client destroying and closes it.

## SEQUENCE And Replay Cache

`rfs4x_sequence_prep()` runs before normal compound execution. It finds the session, validates slot id, operation count, request size, and sequence id. `check_slot_seqid()` distinguishes new requests, replay-cache hits, in-progress duplicates, false retry, retry of uncached replies, and misordered sequence ids.

On a replay-cache hit, the cached `COMPOUND4res` is copied from the slot and normal execution is skipped. On a new request, the slot is marked in use and any previous recallable-state race marker in the slot is erased.

`rfs4x_op_sequence()` must appear as operation zero. It checks for expired leases, validates response-size limits, starts callback-path pinging when needed, records the active client in compound state, advances the slot sequence id, updates session access time, fills the SEQUENCE result, reports callback path down or revoked recallable state, and renews the client lease.

`rfs4x_sequence_done()` releases the slot after reply encoding. It frees any old cached reply, caches the new reply when `cachethis` is set or when the compound is a solo SEQUENCE, otherwise frees the response. It adjusts the session cached-reply count.

## Backchannel Support

`rfs4x_bc_setup()` creates a backchannel if one is not already established, initializes a backchannel slot table, installs it with an atomic compare-and-swap, and marks that a callback ping is needed.

`rfs4x_op_bind_conn_to_session()` binds a transport connection to the fore or back channel. For backchannel binding it sets a session tag on the transport and registers callback connection metadata with RPC service controls.

`ping_cb_null_thr()` tests callback paths using `CB_NULL` calls over untested connections. It tracks ping-in-progress state, path count, ping count, and failure state under the session DB lock.

`rfs4x_op_backchannel_ctl()` updates callback program/security parameters, flushes stale callback channels, and requests a ping. Only `AUTH_NONE` and `AUTH_SYS` callback security are accepted; RPCSEC_GSS is explicitly not implemented here.

## Stateid Operations

`rfs4x_op_test_stateid()` iterates all supplied stateids, normalizes special stateid forms with `get_stateid4()`, calls `rfs4_get_all_state()`, releases any resolved open/delegation/lock state, and returns per-stateid status codes while the operation status itself is `NFS4_OK`.

`rfs4x_op_free_stateid()` handles stateid classes:

- OPEN stateids are valid but not freed directly here; the result is `NFS4ERR_LOCKS_HELD`.
- LOCK stateids check active locks for the lockowner/sysid and invalidate the lock state if no locks remain.
- DELEG stateids use `rfs4_get_deleg_any()` so revoked delegations can be acknowledged. Revoked delegations are invalidated, the client's revoked-delegation count is decremented, and `NFS4_OK` is returned.
- Invalid or unknown stateid types return `NFS4ERR_BAD_STATEID`.

## Other Operations

`rfs4x_op_reclaim_complete()` marks whole-client reclaim complete and decrements the server reclaim counter when applicable. Per-filesystem reclaim completion is accepted as a no-op because this server does not track that granularity.

`rfs4x_op_secinfo_noname()` performs SECINFO on `.` or `..` for the current directory and clears the current filehandle after a successful result, as required by the protocol.

`nfs4x_share_to_delegreq()` maps NFSv4.1 `OPEN4_SHARE_WANT_*` bits saved by XDR decoding into internal `delegreq_t` values. Compile-time assertions verify the bit layout assumption.

`rfs4x_rs_record()` and `rfs4x_rs_erase()` record and clear recallable delegation state associated with a session/slot/sequence tuple, helping detect races where a delegation is returned/recalled around a cached reply.

## Dependencies

This file depends on:

- Existing NFSv4 client/state DB objects: `rfs4_client_t`, `rfs4_session_t`, openowners, stateids, delegations, leases, stable storage.
- Session allocation/destruction in `nfs4x_state.c`.
- Slot/replay-cache state in the session object.
- RPC service controls for callback channel binding.
- Lock manager interfaces for active lock checks.

## Research Notes

This file is the behavioral center of the illumos NFSv4.1 server. The main correctness risks are EXCHANGE_ID case handling, clientid/session lifetime races, sequence-id replay-cache behavior, slot cleanup timing after reply encode, callback path state transitions, and FREE_STATEID handling for revoked delegations and active locks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_state.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_state.c

## Purpose

`nfs4x_state.c` owns NFSv4.1 server session state lifecycle. It defines session lookup indexes, creates and destroys sessions/channels, negotiates channel limits, manages fore-channel replay slots, removes sessions during client teardown, tracks delegation recall race metadata, and initializes the NFSv4.1 session state table.

## Main Interfaces

Session lookup and references:

- `rfs4x_session_rele`
- `rfs4x_session_hold`
- `rfs4x_findsession_by_id`
- `rfs4x_findsession_by_clid`
- `rfs4x_createsession`

Session destruction/removal:

- `rfs4x_destroysession`
- `rfs4x_client_session_remove`
- `rfs4x_destroy_session_channel`

Channel and slot helpers:

- `sess_chan_limits`
- `rfs41_create_session_channel`
- `rfs41_destroy_back_channel`
- `nfs4x_csa_flags_valid`

Recallable-state race helpers:

- `rfs41_deleg_rs_hold`
- `rfs41_deleg_rs_rele`

State table lifecycle:

- `rfs4x_state_init_locked`
- `rfs4x_state_fini`

Important private callbacks include `rfs4_session_create`, `rfs4_session_destroy`, and `rfs4_session_expiry`.

## Session Indexing

Sessions are indexed by `sessionid4` and secondarily by `clientid4`. The session id is an illumos-constructed union containing fixed padding, server start time, and a unique atomic session counter. The session-id hash uses the unique session index.

`rfs4x_findsession_by_id()` searches the primary session index. `rfs4x_findsession_by_clid()` searches the secondary clientid index. `rfs4x_createsession()` uses a unique key that cannot collide with existing clientid associations and lets the common NFSv4 DB layer invoke `rfs4_session_create()`.

## Channel Limit Negotiation

`sess_chan_limits()` clamps or validates negotiated channel attributes:

- Fore-channel max requests is capped by `rfs4_max_slots`.
- Back-channel max requests must be between 1 and `rfs4_back_max_slots`.
- Minimum request/response sizes are enforced for both fore and back channels.
- Fore-channel max operations is capped by `NFS4_COMPOUND_LIMIT`.
- Back-channel max operations must support at least two operations.
- Cached response size is capped to a small slot-cache payload plus SEQUENCE header size.
- Back-channel cached response size is forced to zero.

Unsupported persistent reply cache and RDMA create-session flags are cleared during session creation.

## Session Creation

`rfs4_session_create()` performs the actual session object initialization:

- Holds the parent client DB entry.
- Builds a session id from server start time and unique session counter.
- Validates CREATE_SESSION flags.
- Initializes callback security, defaulting to `AUTH_NONE` if the client supplies no callback security parameters.
- Initializes session access time, flags, callback program, credentials, and reply-cache count.
- Attempts bidirectional RPC callback setup when `CREATE_SESSION4_FLAG_CONN_BACK_CHAN` is requested.
- Creates the fore channel, and if bidirectional callback succeeds, uses it as both fore and back channel.
- Copies requested fore/back channel attributes and validates them with `sess_chan_limits()`.
- Inserts the session into the parent client's session list unless the client is being destroyed.
- Creates a backchannel slot table when bidirectional callback is active.
- Allocates fore-channel replay slots, each with its own mutex.

On failure it tears down allocated channels and releases the client reference.

## Session Destruction And Expiry

`rfs4x_destroysession()` rejects destruction with `NFS4ERR_DELAY` when DB references exceed the expected in-use count. If a backchannel exists, it calls `slot_cb_status()` to reject destruction while callback slots are busy. On success it invalidates the session DB entry and removes the session from the client list.

`rfs4x_client_session_remove()` forcibly invalidates and removes all sessions for a closing client without refcount checks.

`rfs4_session_destroy()` destroys backchannel slot tables, flushes callback channels, frees callback security state, frees cached replay slot replies, destroys fore/back channels, removes the session from the client list, and releases the parent client.

`rfs4_session_expiry()` expires invalid sessions or sessions whose parent client lease has expired.

## Slot Replay Cache

Fore-channel slots are allocated by `slots_alloc()` and freed by `slots_free()`. Each `rfs4_slot_t` has a mutex and may hold a cached `COMPOUND4res`. `slots_free()` destroys slot mutexes and frees cached replies for slots marked `RFS4_SLOT_CACHED`.

The slot replay-cache behavior is completed by `rfs4x_sequence_prep()` and `rfs4x_sequence_done()` in `nfs4x_srv.c`; this file supplies the storage and cleanup routines.

## Backchannel Channels

`rfs41_create_session_channel()` creates a generic session channel. For back or both directions it also allocates `sess_bcsd_t`, initializes its mutex, and attaches it as channel-specific data.

`rfs41_destroy_back_channel()` destroys the backchannel-specific data and the channel lock. `rfs4x_destroy_session_channel()` handles fore-only, back-only, both, and bidirectional-RPC cases, including the case where fore and back pointers refer to the same channel object.

## Recallable-State Race Tracking

`rfs41_deleg_rs_hold()` and `rfs41_deleg_rs_rele()` manage a reference count inside delegation recall-state tracking. When the count reaches zero, the stored session id, sequence id, and slot number are cleared. This supports the `rfs4x_rs_record()`/`rfs4x_rs_erase()` logic in `nfs4x_srv.c`.

## State Table Initialization

`rfs4x_state_init_locked()` creates the NFSv4.1 session table with the common NFSv4 DB framework, then creates:

- A primary unique session-id index.
- A non-unique clientid secondary index.

`rfs4x_state_fini()` is intentionally empty because the caller destroys the common state tables.

## Dependencies

This file depends on the common NFSv4 server DB/index framework, client records, lease timing, RPC service callback controls, slot-table support from `nfs4x_slrc.c`, and backchannel security helpers implemented in `nfs4x_srv.c`.

## Research Notes

This file is where negotiated protocol limits become concrete kernel allocations. Audit hotspots are channel size validation, backchannel slot-table allocation from client-provided limits, bidirectional channel pointer ownership, session/client list removal races, cached reply cleanup, and forced session invalidation during client teardown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_state.c -->