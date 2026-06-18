# subset-b-009704 Research

This grouped report covers NFS-Ganesha NFSv4 operation handlers from `sources/user-network-fs/nfs-ganesha/src/Protocols/NFS`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_destroy_clientid.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_destroy_clientid.c

Purpose: implements `NFS4_OP_DESTROY_CLIENTID` for NFSv4.1+ by removing confirmed and/or unconfirmed clientid records when they are no longer active. The handler is centered on `nfs4_op_destroy_clientid`, with `nfs4_op_destroy_clientid_Free` as a no-op result cleanup hook.

Important APIs and types: it consumes `DESTROY_CLIENTID4args` and fills `DESTROY_CLIENTID4res`, uses SAL client identity types `nfs_client_record_t` and `nfs_client_id_t`, and coordinates with `nfs_client_id_get_confirmed`, `nfs_client_id_get_unconfirmed`, `remove_confirmed_client_id`, `remove_unconfirmed_client_id`, `nfs4_rm_clid`, and reference helpers. It also uses `cr_mutex` and `cid_mutex` for record-level and clientid-level synchronization.

Control flow: the operation sets `resp->resop`, traces the request, looks first for a confirmed clientid, falls back to unconfirmed, then rechecks confirmed to handle a race where another thread confirmed the clientid during lookup. If nothing is found it returns `NFS4ERR_STALE_CLIENTID`. Once a record is found, it increments the client record ref, locks `client_record->cr_mutex`, re-reads the confirmed/unconfirmed pointers, and exits quietly if another destroy already removed both. Confirmed records are not removed if their NFSv4.1 callback session list is non-empty, returning `NFS4ERR_CLIENTID_BUSY`. Otherwise the confirmed stable-storage record is removed through `nfs4_rm_clid` and the record is unhashed. Unconfirmed records are unhashed similarly.

State and persistence: this file directly mutates SAL clientid tables and removes the stable clientid record for confirmed clients. It depends on reference counts and mutex ordering to avoid use-after-free while racing EXCHANGE_ID, CREATE_SESSION, and other destroy paths.

Dependencies and integration: integrates with NFS compound dispatch, SAL clientid management, LTTng tracepoints, and logging. The returned status is converted through `nfsstat4_to_nfs_req_result`.

Risks: races around confirmed/unconfirmed transitions are the main risk; the double lookup and recheck under `cr_mutex` are essential. Session checks rely on `cid_cb.v41.cb_session_list` as the proxy for "busy"; future state forms would need matching checks. Stable-storage removal before unhashing must remain ordered carefully.

Test signals: cover stale clientids, destroying only-unconfirmed records, destroying confirmed records with no sessions, `NFS4ERR_CLIENTID_BUSY` when sessions exist, and concurrent confirm/destroy races. Lease recovery tests should verify stable clientid records disappear after successful destroy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_destroy_clientid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_destroy_session.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_destroy_session.c

Purpose: implements `NFS4_OP_DESTROY_SESSION`, the NFSv4.1 operation that deletes an established session. The public functions are `nfs4_op_destroy_session` and a no-op `nfs4_op_destroy_session_Free`.

Important APIs and types: uses `DESTROY_SESSION4args`, `DESTROY_SESSION4res`, and `nfs41_session_t`. It depends on `nfs41_Session_Get_Pointer`, `check_session_conn`, `nfs41_Session_Del`, and `dec_session_ref`.

Control flow: the handler rejects NFSv4.0 compounds with `NFS4ERR_INVAL`. It resolves the supplied session id into a session pointer; failure maps to `NFS4ERR_BADSESSION`. It then enforces RFC behavior that `DESTROY_SESSION` be invoked over a connection associated with that session via `check_session_conn(session, data, false)`, returning `NFS4ERR_CONN_NOT_BOUND_TO_SESSION` if not. A successful connection check calls `nfs41_Session_Del`; delete failure is converted to `NFS4ERR_BADSESSION`, otherwise the operation completes with `NFS4_OK`.

State and persistence: the operation removes the session from the in-memory NFSv4.1 session registry. It does not directly remove clientids, stable recovery records, open state, or locks. Reference ownership is simple: the lookup takes a session reference and every path after lookup drops it.

Dependencies and integration: tightly integrated with session-table SAL code, connection binding checks, NFS QoS/session request handling, and LTTng NFSv4 tracepoints. It returns through `nfsstat4_to_nfs_req_result` for compound control.

Risks: the primary risk is accepting a request on the wrong transport, which would violate session-channel binding; `check_session_conn` is the guard. Race risk is limited to deletion after lookup; `nfs41_Session_Del` must be idempotent enough to report `BADSESSION`. Cleanup must always release the lookup reference.

Test signals: exercise minorversion 0 rejection, unknown session ids, connection-not-bound failure, successful delete, and duplicate destroy after a successful delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_destroy_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_exchange_id.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_exchange_id.c

Purpose: implements NFSv4.1 `EXCHANGE_ID`, which maps a client owner/verifier and server role negotiation into an unconfirmed or confirmed clientid response. It also builds the server owner/scope fields required by RFC 5661.

Important APIs and types: uses `EXCHANGE_ID4args`, `EXCHANGE_ID4res`, `client_owner4`, `nfs_client_record_t`, and `nfs_client_id_t`. It uses `get_client_record`, `create_client_id`, `nfs_client_id_insert`, credential comparison through `nfs_compare_clientcred`, lease/state checks through `valid_lease` and `client_id_has_state`, and cleanup through clientid ref helpers. Response memory uses `gsh_malloc` and is released by `nfs4_op_exchange_id_Free`.

Control flow: the handler rejects minorversion 0 and invalid `eia_flags`, checks response room, computes server pNFS role flags from client requests and `nfs_param.nfsv4_param`, then looks up or creates a `client_record` keyed by owner id, pNFS flags, and transport addresses. Under `client_record->cr_mutex` it implements the RFC cases: non-update with existing confirmed record may return the confirmed response, expire a colliding old clientid, or return `NFS4ERR_CLID_INUSE`; update requests require matching verifier, credential, and `op_ctx->client`; update without a confirmed record returns `NFS4ERR_NOENT`. Existing unconfirmed records are removed before creating a new unconfirmed clientid. Successful responses include clientid, create-session sequence, server flags, state protection `SP4_NONE`, major/minor server owner, server scope, and empty impl id.

State and persistence: it creates, updates, expires, or removes in-memory clientid records and initializes v4.1 session list and create-session sequencing. It records incoming verifier and credential state but currently ignores requested state protection beyond metrics. It allocates response strings that must be freed only on success.

Dependencies and integration: integrates with RPC transport address helpers, NFS credentials, pNFS role configuration, SAL metrics, clientid tables, server owner globals `cid_server_owner` and `cid_server_scope`, and virtual-server address scoping.

Risks: this is a high-concurrency identity negotiation point. Bugs can cause duplicate clientids, incorrect trunking/collision behavior, or leaked response buffers. The `eir_flags` field is ORed in multiple paths; it must be initialized by XDR/result allocation. Virtual-server major id sizing must include the address suffix correctly.

Test signals: cover invalid flags, minorversion 0, first exchange, replay with same verifier, client restart with changed verifier, credential collision, update cases 6 to 9, pNFS role negotiation, response-size failure, and memory cleanup of successful responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_exchange_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_free_stateid.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_free_stateid.c

Purpose: implements NFSv4.1 `FREE_STATEID`, allowing clients to free stateids, especially lock stateids with no held locks and revoked delegation stateids.

Important APIs and types: uses `FREE_STATEID4args`, `FREE_STATEID4res`, `state_t`, `fsal_obj_handle`, and `gsh_export`. It calls `is_stateid_revoked`, `atomic_remove_revoked_and_clear_flags`, `nfs4_Check_Stateid`, `get_state_obj_export_owner_refs`, `save_op_context_export_and_set_export`, `state_del_locked`, and state/object/export reference helpers.

Control flow: minorversion 0 is rejected with `NFS4ERR_INVAL`. Revoked delegation stateids are special-cased before normal stateid validation: if the stateid is on the revoked list it is atomically removed and client session flags may be cleared; the operation returns `NFS4_OK`. For normal stateids, `nfs4_Check_Stateid` resolves the state using `STATEID_SPECIAL_CURRENT`. The handler obtains object/export refs, switches `op_ctx` to the state export, locks the object state, and only frees `STATE_TYPE_LOCK` stateids whose lock list is empty. Any other state or lock state with held locks returns `NFS4ERR_LOCKS_HELD`.

State and persistence: mutates revoked delegation bookkeeping and may delete a lock state from SAL state tables. It preserves export context while manipulating state, then restores it. It does not directly change stable storage.

Dependencies and integration: integrated with NFSv4.1 sessions for revoked delegation notification flags, SAL state validation/deletion, FSAL object references, export context switching, and LTTng.

Risks: the code explicitly supports only empty lock stateids; future support for other state types would need additional protocol checks. The revoked path assumes `data->session` is present for v4.1; logging dereferences `clientid` in one branch after the atomic helper succeeds, so tests should include session-present assumptions. Locking object state before `state_del_locked` is required.

Test signals: revoked delegation cleanup, revoked cleanup when more revoked delegations remain, invalid stateid, empty lock state deletion, lock state with held locks returning `LOCKS_HELD`, and non-lock state rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_free_stateid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getattr.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getattr.c

Purpose: implements NFSv4 `GETATTR` by translating a requested bitmap into FSAL attributes and encoding an NFSv4 `fattr4` result.

Important APIs and types: uses `GETATTR4args`, `GETATTR4res`, `fattr4`, `attrmask_t`, `fsal_attrlist`, and `nfs_client_id_t`. It calls `nfs4_sanity_check_FH`, `nfs4_Fattr_Check_Access_Bitmap`, `bitmap4_to_attrmask_t`, `nfs4_bitmap4_Remove_Unsupported`, `file_To_Fattr`, `nfs4_Fattr_Fill_Error`, `check_resp_room`, and delegation helpers `is_write_delegated` and `handle_deleg_getattr`.

Control flow: after current filehandle validation, empty bitmaps return success immediately. The handler rejects requests containing attributes not readable by clients, translates the bitmap to an attrmask, prepares FSAL attrs, and strips unsupported bitmap bits. For regular files, it checks write delegations under `STATELOCK_lock`; if another client holds a write delegation it invokes `handle_deleg_getattr`, allowing callback-based attribute refresh or returning delay/error. It then calls `file_To_Fattr`. Referral objects get special handling: if `fs_locations` or `rdattr_error` is requested, it fills restricted attrs and `NFS4ERR_MOVED`; otherwise it returns `NFS4ERR_MOVED`. On success it computes response size from the encoded attr list and verifies compound response room.

State and persistence: does not create persistent state, but it may trigger delegation callback behavior and consumes/refcounts a delegation client. It allocates fattr buffers that `nfs4_op_getattr_Free` releases on success and that the error path frees explicitly.

Dependencies and integration: depends on FSAL attr conversion, referral handling, mount-on fileid helpers, state/delegation code, compound response sizing, and LTTng tracepoints.

Risks: GETATTR sits on hot paths and must avoid leaking attr buffers on errors. Delegation callback behavior can introduce delay and must not hold the state lock across slow paths incorrectly. Referral behavior depends on exact requested bitmap semantics.

Test signals: empty bitmap success, unsupported/read-protected attributes, regular file attrs, referral with and without `RDATTR_ERROR`, response-size overflow, write delegation held by same client versus different client, and cleanup after `file_To_Fattr` failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getdeviceinfo.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getdeviceinfo.c

Purpose: implements pNFS `GETDEVICEINFO`, returning FSAL-encoded device address information for a supplied device id and layout type.

Important APIs and types: uses `GETDEVICEINFO4args`, `GETDEVICEINFO4res`, `GETDEVICEINFO4resok`, `struct pnfs_deviceid`, `struct fsal_module`, and XDR streams. It uses the global `pnfs_fsal` table, `fs_da_addr_size`, `getdeviceinfo`, `xdrmem_create`, and `check_resp_room`.

Control flow: minorversion 0 is rejected. The handler overlays Ganesha's `pnfs_deviceid` on the wire `deviceid4` bytes, validates `fsal_id`, and looks up the FSAL module. It computes a minimum response count, asks the FSAL for maximum device address body size, and caps allocation by the client's `gdia_maxcount`. The FSAL encodes the `da_addr_body` into an in-memory XDR stream. After encoding, the handler checks response room, clears the notification bitmap, and attaches the allocated buffer to the result. Any error frees the allocated buffer before setting `gdir_status`.

State and persistence: read-only with respect to NFS state. It allocates an opaque response buffer owned by the XDR result until `nfs4_op_getdeviceinfo_Free`.

Dependencies and integration: integrated with pNFS FSAL module registration, FSAL layout-specific device encoding, compound response sizing, and export/device id conventions.

Risks: `gdia_maxcount` smaller than the base response can underflow when computing `gdia_maxcount - mincount`; callers rely on unsigned/count behavior and FSAL size checks. Invalid or inactive FSAL ids must not index beyond `pnfs_fsal`. FSALs must report non-zero address sizes and must not overrun the XDR stream.

Test signals: minorversion 0, invalid fsal id, inactive FSAL, tiny `maxcount`, FSAL getdeviceinfo failure, response-room failure, successful opaque body encoding, and cleanup of successful/error buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getdeviceinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getdevicelist.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getdevicelist.c

Purpose: implements pNFS `GETDEVICELIST`, returning device ids for a filesystem/layout type.

Important APIs and types: uses `GETDEVICELIST4args`, `GETDEVICELIST4res`, `GETDEVICELIST4resok`, `struct fsal_getdevicelist_res`, and a local `cb_data` callback carrier. It calls `nfs4_sanity_check_FH`, `op_ctx->fsal_export->exp_ops.getdevicelist`, `check_resp_room`, and `gsh_malloc/free`.

Control flow: minorversion 0 is rejected, then the current filehandle is checked. The handler initializes FSAL cookie and verifier from request arguments. It allocates a fixed array for up to 32 device ids and passes a callback to the FSAL. The callback writes a device id composed from the current export id (`swexport`) and the FSAL-provided id in network order, incrementing the count. After the FSAL returns, the handler sizes the response, checks response room, copies output cookie/verifier/eof, and records the returned list length.

State and persistence: read-only with respect to state. It allocates a device list result buffer freed by `nfs4_op_getdevicelist_Free` only on success; FSAL failure and response-room failure free the buffer in-line.

Dependencies and integration: depends on current export in `op_ctx`, FSAL pNFS `getdevicelist`, NFSv4 verifier/cookie conventions, pNFS device id packing, and response sizing.

Risks: the callback checks `count > max`, not `count >= max`, so a full list can write at index `max`; this is a boundary risk around the fixed 32-entry allocation. The handler ignores client-provided `gdla_maxdevices` style bounds if the protocol has one and uses its local max. Device id byte casting assumes alignment and deviceid layout.

Test signals: minorversion 0, invalid current FH, FSAL returns zero devices, exactly 32 and more than 32 devices, non-zero cookies/verifiers, response-room failure, and successful free of result list.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getdevicelist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getfh.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getfh.c

Purpose: implements `GETFH`, returning the compound's current NFSv4 filehandle to the client.

Important APIs and types: uses `GETFH4res`, `nfs_fh4`, `fsal_attrlist`, and the current `compound_data_t` filehandle/object. It calls `nfs4_sanity_check_FH`, `check_resp_room`, `fs_supported_attrs`, `obj_ops->is_referral`, `nfs4_AllocateFH`, and `gsh_free`.

Control flow: the handler validates that a current filehandle exists and is usable, computes padded response size from `currentFH.nfs_fh4_len`, and checks available response room. It prepares a broad attr request from the FSAL supported attrs, excluding ACLs and FS locations, then asks the current object whether it is a referral. Referral filehandles return `NFS4ERR_MOVED` rather than exposing the handle. On success it allocates the result filehandle, copies length and bytes from `data->currentFH`, and returns `NFS4_OK`.

State and persistence: no persistent state changes. It allocates response memory that `nfs4_op_getfh_Free` releases on successful status.

Dependencies and integration: depends on compound filehandle state established by `PUTFH`, `PUTROOTFH`, `LOOKUP`, `OPEN`, or similar operations, plus FSAL referral detection and response sizing.

Risks: referral detection requires an attrlist and FSAL support; wrong masking could make referrals visible. The operation copies raw currentFH bytes, so preceding operations must have produced a valid handle. Error paths must set `data->op_resp_size` to just `nfsstat4`.

Test signals: no current FH, response too large, referral object returning `MOVED`, normal handle copy byte-for-byte, and result free.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getfh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_illegal.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_illegal.c

Purpose: provides dispatch handlers for illegal and unsupported NFSv4 operations.

Important APIs and types: uses `nfs_argop4`, `nfs_resop4`, `NFS4_OP_ILLEGAL`, `NFS4ERR_OP_ILLEGAL`, and `NFS4ERR_NOTSUPP`. Public handlers are `nfs4_op_illegal`, `nfs4_op_notsupp`, and their no-op free hooks.

Control flow: `nfs4_op_illegal` sets `resp->resop` to `NFS4_OP_ILLEGAL`, stores `NFS4ERR_OP_ILLEGAL` in the union's illegal status, emits a tracepoint, and returns `NFS_REQ_ERROR`. `nfs4_op_notsupp` sets `resp->resop` to the original `op->argop` so the response matches the unsupported operation number, stores `NFS4ERR_NOTSUPP` in the same union member, traces, and returns error.

State and persistence: no state, references, exports, filehandles, or persistent records are changed.

Dependencies and integration: used by the NFSv4 operation dispatch table for invalid opcodes or compiled/negotiated unsupported operations. Tracepoints provide lightweight observability.

Risks: the code relies on the response union layout using `opillegal.status` for unsupported operations. Dispatch table users must pick `illegal` versus `notsupp` correctly to preserve protocol-visible `resop`.

Test signals: invalid opcode maps to `OP_ILLEGAL`; known but unsupported opcode maps to original op number with `NFS4ERR_NOTSUPP`; free hooks are harmless.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_illegal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutcommit.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutcommit.c

Purpose: implements pNFS `LAYOUTCOMMIT`, committing client layout writes and optional size/mtime updates back through the FSAL.

Important APIs and types: uses `LAYOUTCOMMIT4args`, `LAYOUTCOMMIT4res`, `LAYOUTCOMMIT4resok`, `state_t`, `state_layout_segment_t`, `fsal_layoutcommit_arg`, `fsal_layoutcommit_res`, and XDR decode streams. It calls `nfs4_sanity_check_FH`, `nfs4_Check_Stateid`, `obj_ops->layoutcommit`, and state ref helpers.

Control flow: minorversion 0 and non-regular current FHs are rejected. The handler maps optional `loca_last_write_offset` and `loca_time_modify` fields into FSAL args, creates an XDR decode stream over `loca_layoutupdate.lou_body`, and validates the supplied layout stateid. It sets the FSAL layout type from the layout state, locks the current object's state, and iterates all layout segments attached to the state. For each segment it passes segment metadata and FSAL segment data to `layoutcommit`. If the FSAL says `commit_done`, iteration stops; otherwise the XDR stream is reset to the original body start for the next segment. The response reports new size only if the FSAL supplied one.

State and persistence: does not directly modify SAL layout lists, but commits data/metadata to the backing FSAL and may cause persistent file size or mtime updates via FSAL implementation. Holds state lock while iterating segments.

Dependencies and integration: integrated with layout state validation, pNFS FSAL layoutcommit callbacks, XDR layout-specific opaque decoding, and NFSv4.1 status mapping.

Risks: every segment reuses the same opaque body; FSAL implementations must tolerate reset decode streams. Holding state lock across FSAL callbacks can be expensive or deadlock-prone if FSAL re-enters state. Error paths must release layout state and destroy the XDR stream.

Test signals: minorversion 0, invalid FH, bad layout stateid, multiple segments with `commit_done` false/true, layout body decode failure in FSAL, size-supplied response, and state/XDR cleanup on errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutcommit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutget.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutget.c

Purpose: implements pNFS `LAYOUTGET` and also contains simple handlers for NFSv4.2 `LAYOUTERROR` and `LAYOUTSTATS`.

Important APIs and types: key helpers are `acquire_layout_state`, `free_layouts`, `one_segment`, `nfs4_op_layoutget`, `nfs4_op_layouterror`, and `nfs4_op_layoutstats`. It uses `state_t`, `state_owner_t`, `state_refer`, `fsal_layoutget_arg/res`, `layout4`, `state_layout_segment_t`, pNFS segment helpers, and XDR encode streams.

Control flow: `acquire_layout_state` validates the supplied stateid under the state lock. Existing layout stateids are reused; share, deleg, or lock stateids create a per-clientid layout state after returning and deleting any prior layout state of the same type, supporting forgetful clients. `one_segment` allocates a layout body buffer sized by `fs_loc_body_size`, asks the FSAL `layoutget` to encode one segment, records the returned segment in SAL via `state_add_segment`, and frees on failure. `nfs4_op_layoutget` rejects v4.0 and non-regular FHs, verifies pNFS support via `fs_maximum_segments`, acquires layout state, then repeatedly grants segments until `last_segment`. It tracks response size and remaining maxcount, checks response room, updates the layout stateid under lock, and returns the layout array. Failure frees partial layouts, deletes brand-new zero-seqid layout state, and invalidates current stateid. `LAYOUTERROR` and `LAYOUTSTATS` currently log client reports and return OK without persistence.

State and persistence: creates and updates layout stateids, stores FSAL segment data on state segment lists, increments a `granting` counter while FSAL layoutget is active, and can return/delete forgotten layouts. No stable storage is touched.

Dependencies and integration: relies on SAL state locking and refs, pNFS FSAL `layoutget`, FSAL max segment and body sizing, `nfs4_return_one_state` from layoutreturn code, compound response sizing, and NFSv4.1 session slot references.

Risks: failure cleanup around partially added segments is delicate; a segment may be in SAL even if later response-size checking fails. The function holds object state locks across FSAL layoutget and state updates. `arg.maxcount` subtraction can underflow if a segment exceeds remaining maxcount. Layout stats/error handlers are currently observability only.

Test signals: v4.0 rejection, unsupported pNFS, new layout state from share state, reuse existing layout state, forgetful-client deletion path, multi-segment layout, response-room failure after segments, FSAL error cleanup, and layoutstats/layouterror logging behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutreturn.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutreturn.c

Purpose: implements pNFS `LAYOUTRETURN` plus shared layout return helpers used by `LAYOUTGET` cleanup and recalls.

Important APIs and types: exports `nfs4_op_layoutreturn`, `handle_recalls`, and `nfs4_return_one_state`. Uses `LAYOUTRETURN4args/res`, `layoutreturn_file4`, `layoutreturn_stateid`, `state_t`, `state_owner_t`, `state_layout_segment_t`, `state_layout_recall_file`, `fsal_layoutreturn_arg`, `pnfs_segment`, and XDR decode streams.

Control flow: the top-level operation rejects v4.0, then dispatches by return type. `LAYOUTRETURN4_FILE` validates the current regular file, optionally resolves the layout stateid under state lock, builds the requested segment, calls `nfs4_return_one_state`, and either invalidates current stateid if the state was deleted or updates and returns a new stateid. `LAYOUTRETURN4_FSID` records the current fsid and falls through to the ALL-style loop. FSID/ALL returns initialize a temporary root op context, iterate the clientid owner's state list while carefully dropping `so_mutex` around work, set the correct export context per state, lock each object's state, and return matching layout states. `handle_recalls` removes satisfied recall entries and returns recall cookies. `nfs4_return_one_state` iterates layout segments, calls FSAL `layoutreturn` for contained or overlapping segments, deletes or shrinks segments, and deletes the layout state when no segments remain; reclaim returns call FSAL without recorded segments.

State and persistence: mutates layout segment lists, recall lists, layout stateids, current stateid validity, and possibly deletes layout states. It may switch `op_ctx` export context for bulk returns. No stable storage is directly updated.

Dependencies and integration: used by layoutget forgetful-state handling, recall completion, FSAL pNFS return callbacks, SAL state lists, export references, and NFSv4.1 clientid owner state tracking.

Risks: the FSID branch compares `fsid` to `data->current_obj->fsid` while iterating different `obj` values, which is suspicious and should be tested. `alloca(sizeof(arg)+sizeof(void *)*(recalls-1))` is risky when `recalls` is zero because of unsigned underflow. Bulk iteration restarts are necessary but easy to break. FSAL calls under state lock may be costly.

Test signals: file return with full deletion, partial segment shrink, reclaim return, recall cookie satisfaction, FSID return across multiple states, ALL return restart behavior, stale state refs, and zero-recall layoutreturn path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_link.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_link.c

Purpose: implements NFSv4 `LINK`, creating a hard link to the saved filehandle object under the current directory filehandle.

Important APIs and types: uses `LINK4args`, `LINK4res`, `fsal_obj_handle`, `fsal_attrlist`, and `fsal_status_t`. It calls `nfs4_sanity_check_FH`, `nfs4_sanity_check_saved_FH`, `nfs4_utf8string_scan`, `fsal_link`, `fsal_get_changeid4`, `nfs4_Errno_status`, and FSAL attr prepare/release helpers.

Control flow: the current FH must be a directory and the saved FH must not be a directory. Cross-export hard links are rejected with `NFS4ERR_XDEV`. The new name is scanned as one UTF-8 path component. The handler captures pre-change information, calls `fsal_link(saved_obj, current_dir, name, pre_attrs, post_attrs)`, then fills `change_info4` from FSAL-provided pre/post change attributes when available, falling back to `fsal_get_changeid4` for `after`. The `atomic` flag is true only when both pre and post change attrs are valid.

State and persistence: persists a directory entry/hard link through the FSAL. It does not modify NFSv4 open/lock state directly, but it changes filesystem namespace and directory change ids.

Dependencies and integration: depends on compound `SAVEFH`/current FH semantics, export identity in `op_ctx` and `data->saved_export`, FSAL link implementation, NFS status conversion, and LTTng change-info tracing.

Risks: cross-export detection relies on export ids already set in compound context. Saved FH sanity uses `-DIRECTORY` to reject directories; behavior for special files depends on `nfs4_sanity_check_saved_FH`. Change info quality depends on FSAL attr support.

Test signals: missing current/saved FH, current not directory, saved directory, cross-export link, invalid UTF-8/path component, FSAL link errors, and accurate before/after/atomic cinfo.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lock.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lock.c

Purpose: implements NFSv4 `LOCK`, including new lock owner creation, existing lock owner requests, blocking lock callbacks, replay handling, grace-period handling, and conflict responses.

Important APIs and types: key functions are `nfs4_op_lock`, `nfsv4_granted_callback`, `notify_granted_completion`, `nfs4_op_lock_Free`, and `nfs4_op_lock_CopyRes`. It uses `LOCK4args/res`, `state_t`, `state_owner_t`, `nfs_client_id_t`, `fsal_lock_param_t`, `state_block_data_t`, `state_refer`, SAL functions `state_add_impl`, `state_lock`, `state_del_locked`, and conflict helpers `Process_nfs4_conflict`/`Copy_nfs4_denied`.

Control flow: the operation first reserves response room for a successful stateid result, validates a regular-file FH, converts lock type into FSAL read/write lock and blocking/nonblocking mode, and normalizes EOF length. For new lock owners it validates the open stateid, gets the open owner and clientid, verifies the open state is a share state, and converts the lock owner name. For existing lock owners it validates the lock stateid under the state lock, checks object/export consistency, requires a lock state, retrieves the related open owner and open state. NFSv4.0 paths check owner seqids and use replay caches. It validates nonzero length, overflow, maxfilesize, and open share access versus requested lock type. Grace logic rejects invalid reclaim/non-reclaim timing unless FSAL handles grace. New lock owners are created and may create a new lock state tied to the open state. The open state is rechecked under state lock to avoid CLOSE races. Blocking locks allocate block data and register `nfsv4_granted_callback`, then `state_lock` performs SAL/FSAL locking. Conflicts become denied replies; success updates the lock stateid and caches responses for v4.0.

State and persistence: creates lock owners and lock stateids, adds lock states to share state's lock list, records byte-range locks in SAL/FSAL, may leave blocked locks with callback metadata, updates current stateid, and uses replay cache for v4.0.

Dependencies and integration: depends on clientid leases/grace, stateid validation, FSAL lock support and max file size, callback RPC for `CB_NOTIFY_LOCK`, export refs, and compound context `op_ctx->clientid`.

Risks: this is concurrency-sensitive. New lock state cleanup differs for blocked locks versus failed locks. `state_open` is decremented before state creation but later reused, so lifetime depends on SAL references and comments deserve scrutiny. Response caching must not cache unrecoverable resource/bad-state errors incorrectly. Blocking callback allocation and freeing must match `state_lock` ownership.

Test signals: new and existing owners, v4.0 seqid replay, bad open/lock stateids, wrong export, read/write openmode mismatch, zero/overflow length, grace and reclaim cases, conflict denied deep-copy/free, blocked lock callback, CLOSE racing LOCK, and maxfilesize normalization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lockt.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lockt.c

Purpose: implements NFSv4 `LOCKT`, a test-only byte-range lock request that reports whether a lock would conflict.

Important APIs and types: uses `LOCKT4args/res`, `state_owner_t`, `nfs_client_id_t`, `state_t`, and `fsal_lock_param_t`. Calls include `nfs4_sanity_check_FH`, `nfs_get_grace_status`, `nfs_client_id_get_confirmed`, `reserve_lease_or_expire`, `convert_nfs4_lock_owner`, `create_nfs4_owner`, `nfs4_State_Get_Obj`, `state_test`, `Process_nfs4_conflict`, and `Release_nfs4_denied`.

Control flow: validates current regular file, rejects zero length, and rejects non-reclaim activity during grace. It maps read/write lock type to FSAL lock type, rejects invalid types, normalizes EOF length to zero, checks overflow and maxfilesize. It resolves the clientid from the request for v4.0 or session for v4.1, reserves the v4.0 lease, creates/fetches a lock owner, and for v4.0 sets `op_ctx->clientid`. It optionally retrieves an existing lock state for this object/owner, locks the object state, and calls `state_test`. Conflicts are encoded into `LOCK4denied`; non-conflict statuses are converted from SAL state status.

State and persistence: should not create persistent locks, but it may create a lock owner record as part of owner resolution. It updates the v4.0 lease on exit and releases grace status.

Dependencies and integration: depends on NFS grace coordination, SAL lock conflict testing, clientid/owner management, FSAL max file size, and denied response allocation/free helpers.

Risks: creating a lock owner for a test request may leave owner state behind depending on owner cache behavior. `nfs_put_grace_status` is called unconditionally at `out`, but `nfs_get_grace_status(false)` only succeeds on the main path; the grace helper must tolerate this pairing. Maxfilesize subtraction assumes `lock_start <= maxfilesize`.

Test signals: valid read/write tests, invalid type, zero length, overflow length, past-maxfilesize range, grace rejection, unknown clientid, conflict denied content and cleanup, and no-conflict success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lockt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_locku.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_locku.c

Purpose: implements NFSv4 `LOCKU`, unlocking a byte range represented by a lock stateid.

Important APIs and types: uses `LOCKU4args/res`, `state_t`, `state_owner_t`, `fsal_obj_handle`, `fsal_lock_param_t`, and `state_status_t`. It calls `nfs4_check_stateid_acquire_state_lock`, `Check_nfs4_seqid_locked`, `state_unlock_locked`, `update_stateid_locked`, `Copy_nfs4_state_req`, and ref helpers.

Control flow: validates current regular file and lock type, builds an FSAL lock descriptor with unlock range, then validates the lock stateid while acquiring the state lock. NFSv4.0 requests check the lock owner seqid and may replay a cached response. It rejects stale owners, zero length, range overflow, and normalizes ranges past maxfilesize to EOF. With `op_ctx->clientid` set for v4.0, it calls `state_unlock_locked` under the state lock. Success updates the lock stateid into the response; v4.0 responses are cached in the lock owner for replay. The common cleanup unlocks state, drops owner/object/state refs, and traces result.

State and persistence: mutates SAL/FSAL byte-range lock state by removing all or part of a lock. It updates stateid sequencing/current stateid and v4.0 replay cache. It does not delete the lock stateid automatically unless lower SAL decides so.

Dependencies and integration: integrated with stateid validation, owner seqids, FSAL max file size, SAL unlock, and compound stateid propagation.

Risks: error paths after `nfs4_check_stateid_acquire_state_lock` must release state locks and refs exactly once. If `state_unlock_locked` partially succeeds then returns an error, protocol recovery depends on SAL behavior. As with LOCKT, maxfilesize subtraction needs valid starts.

Test signals: bad FH, invalid lock type, bad/replayed stateid, stale lock owner, v4.0 seqid replay, zero/overflow length, unlock full range, unlock partial range, maxfilesize normalization, and response cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_locku.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lookup.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lookup.c

Purpose: implements NFSv4 `LOOKUP`, resolving a name in the current directory and replacing the compound current filehandle/object with the result.

Important APIs and types: uses `LOOKUP4args/res`, `fsal_obj_handle`, `fsal_status_t`, exports, and junction state. It calls `nfs4_sanity_check_FH`, `nfs4_utf8string_scan`, `fsal_lookup`, `export_ready`, `set_op_context_export`, `nfs4_export_check_access`, `nfs_export_get_root_entry`, `nfs4_FSALToFhandle`, and `set_current_entry`.

Control flow: the current FH must be a directory; if the check reports notdir on a symlink, the result is converted to `NFS4ERR_SYMLINK`. The target name is validated as a single UTF-8 path component, then `fsal_lookup` returns a referenced object. If the found object is a directory with a `junction_export`, the handler crosses the pseudo-filesystem junction: it verifies export readiness, switches `op_ctx` to the target export, checks access, hides inaccessible exports as `NFS4ERR_NOENT`, handles `WRONGSEC`, obtains the target export root object, and replaces the looked-up junction object with the root. Finally it converts the object to an NFSv4 filehandle, updates `data->currentFH` and `data->current_obj`, and drops the local ref.

State and persistence: mutates compound current object/FH and operation export context. It does not change filesystem contents or NFS state.

Dependencies and integration: central to pathname traversal, pseudo-fs junction exports, export access control, FSAL lookup, filehandle encoding, and LTTng.

Risks: export lock/reference ordering around junction traversal is critical. Access-denied hiding must match READDIR visibility. On errors after `set_op_context_export`, the compound context remains at the crossed export, which may be intended for junction errors but must be consistent.

Test signals: lookup in non-directory, symlink current FH, invalid name, missing name, normal file/directory lookup, junction crossing success, inaccessible junction hidden as NOENT, WRONGSEC, stale export, and filehandle encoding failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lookupp.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lookupp.c

Purpose: implements NFSv4 `LOOKUPP`, moving the compound current filehandle/object to the parent directory, including reverse traversal over pseudo-fs junctions.

Important APIs and types: uses `LOOKUPP4res`, `fsal_obj_handle`, `gsh_export`, and export locks. Calls include `nfs4_sanity_check_FH`, `nfs_export_get_root_entry`, `export_ready`, `set_current_entry`, `set_op_context_export`, `nfs4_export_check_access`, `fsal_lookupp`, and `nfs4_FSALToFhandle`.

Control flow: validates current FH as a directory. It gets the current export root and checks whether the current object is that root. If so, it handles reverse junction traversal: root of the top pseudo root returns `NFS4ERR_NOENT`; otherwise it obtains the parent export and junction object under `original_export->exp_lock`, sets the junction object as current, switches `op_ctx` to the parent export, and checks access. Inaccessible parent exports are hidden as `NFS4ERR_NOENT`. After reverse-junction handling, or for normal directories, it calls `fsal_lookupp` to resolve the parent. A returned parent object is converted to a filehandle and installed as current; null parent results clear current entry and map the FSAL status.

State and persistence: mutates compound current object/FH and export context only. No stable state or filesystem namespace changes.

Dependencies and integration: tied to pseudo-fs export graph, export readiness/reference management, FSAL parent lookup, and access checking.

Risks: lock ordering around clearing current entry and export locks is intentionally careful; regressions can deadlock cleanup paths. The comparison `data->current_obj == root_obj` depends on object identity, not equivalent handles. Errors after switching export context need consistent cleanup.

Test signals: root pseudo lookup parent returning NOENT, reverse junction to parent export, access-hidden parent, stale parent export, normal parent lookup, FSAL lookup parent failure, and filehandle encoding failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lookupp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_nverify.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_nverify.c

Purpose: implements NFSv4 `NVERIFY`, succeeding when supplied attributes do not match current object attributes and returning `NFS4ERR_SAME` when they do.

Important APIs and types: uses `NVERIFY4args/res`, `fattr4`, and `fsal_attrlist`. It calls `nfs4_sanity_check_FH`, `nfs4_Fattr_Check_Access`, `nfs4_Fattr_Supported`, `bitmap4_to_attrmask_t`, `file_To_Fattr`, `nfs4_Fattr_cmp`, and `nfs4_Fattr_Free`.

Control flow: validates current FH, rejects attributes that are not client-readable, rejects unsupported attributes, translates the requested bitmap to an FSAL attr request mask, and fetches current attributes through `file_To_Fattr`. It compares the client-provided fattr against freshly encoded file attributes. If the comparison says unequal, `NFS4_OK` is returned; if equal, the operation returns `NFS4ERR_SAME`; if comparison detects invalid data, it returns `NFS4ERR_INVAL`.

State and persistence: read-only. It allocates temporary fattr memory for current attrs and releases it before returning. It does not change compound current FH.

Dependencies and integration: shares attribute conversion and comparison code with VERIFY/GETATTR paths and depends on FSAL attr retrieval through `file_To_Fattr`.

Risks: on early `file_To_Fattr` errors the prepared attrs are not released in the visible code path, so attr masks with inherited allocations should be examined. Correct semantics depend on `nfs4_Fattr_cmp` returning false for not-same, true for same, and -1 for invalid.

Test signals: unreadable attrs, unsupported attrs, bitmap conversion failure, unequal attributes returning OK, equal attributes returning SAME, invalid encoded attr returning INVAL, and temporary fattr cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_nverify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open.c

Purpose: implements NFSv4 `OPEN` and most of its helper logic: owner/replay handling, create/open via FSAL, share state creation/upgrades, delegation claims and grants, grace-period validation, and result change info.

Important APIs and types: public hooks are `nfs4_op_open`, `nfs4_op_open_CopyRes`, and `nfs4_op_open_Free`. Major helpers include `open4_create_fh`, `open4_validate_claim`, `open4_open_owner`, `open4_claim_deleg`, `get_delegation`, `do_delegation`, `open4_ex_create_args`, and `open4_ex`. It uses `OPEN4args/res`, `state_owner_t`, `state_t`, `nfs_client_id_t`, `fsal_attrlist`, `fsal_openflags_t`, `fsal_create_mode`, `state_refer`, and delegation data structures.

Control flow: `nfs4_op_open` checks export write permissions, current FH, confirmed clientid, v4.0 lease, open owner, claim validity/grace, create-with-non-CLAIM_NULL invalidity, share_access/share_deny masks, and prepares attrset/cinfo. It then delegates actual FSAL and state work to `open4_ex`. `open4_ex` handles claim-specific object selection: `CLAIM_NULL` names under a directory and may create; `CLAIM_PREVIOUS`, `CLAIM_FH`, and delegation claims use current FH. Create args validate writable/supported attrs, convert fattrs, handle exclusive verifiers, set default mode, and squash owner attrs. Existing files are looked up before open; guarded create of existing files returns EXIST, exclusive create may verify. It opens or reopens through `fsal_open2`, `fsal_verify2`, or `fsal_reopen2`, handles share-denied retry after expired conflicting clients, creates share state via `state_add_impl`, updates/installs current FH, upgrades existing share access/deny bitmasks, attempts delegation, and updates stateid under the state lock. `open4_open_owner` handles owner creation and v4.0 replay; replay success can re-lookup the opened file to restore current FH. Delegation helpers validate delegation claim stateids, decide support/contention, create delegation state, acquire FSAL lease locks, and fill standard or timestamp delegation responses.

State and persistence: creates and updates share state, open owners, owner replay cache, delegation state, FSAL open handles, current FH/object, lease timestamps, delegation statistics, and optional create attributes on disk. `CLAIM_PREVIOUS` and reclaim paths interact with recovery/grace state.

Dependencies and integration: central integration point for clientid SAL, leases/grace, FSAL open/create/reopen/verify APIs, export permissions, attribute conversion, delegation policy/callback support, stateid sequencing, compound response cinfo, and NFSv4.1/4.2 feature flags.

Risks: this is one of the highest-risk handlers. Cleanup ordering around `file_state`, `new_state`, `file_obj` refs, and state locks is delicate. There is a suspicious sequence in `nfs4_op_open` where `file_state` is decremented before a later conditional tries to `state_del(file_state)` on error. Delegation-related skip of `fsal_reopen2` for same-client delegations must not bypass required access/share checks. Replay paths must restore current FH exactly. Share downgrade history depends on `share_access_prev` and `share_deny_prev` bit encoding used here.

Test signals: v4.0 owner seqid replay and OPEN_CONFIRM flag, v4.1 session clientid, create guarded/unchecked/exclusive/exclusive4_1, unsupported attrs and squashing, CLAIM_FH/PREVIOUS/DELEGATE_CUR/DELEG_CUR_FH, write export ROFS, invalid share flags including delegation hint flags by minorversion, delegation grant/none reasons, share denied and expired-client retry, cinfo before/after/atomic, open upgrade, error cleanup with new state, and current FH after replay.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open_confirm.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open_confirm.c

Purpose: implements NFSv4.0 `OPEN_CONFIRM`, confirming an open owner that previously required confirmation. NFSv4.1+ does not support this operation.

Important APIs and types: uses `OPEN_CONFIRM4args/res`, `OPEN_CONFIRM4resok`, `state_t`, `state_owner_t`, and `fsal_obj_handle`. It calls `nfs4_sanity_check_FH`, `nfs4_check_stateid_acquire_state_lock`, `Check_nfs4_seqid_locked`, `update_stateid_locked`, `Copy_nfs4_state_req`, and ref helpers.

Control flow: minorversion greater than zero returns `NFS4ERR_NOTSUPP`. The current FH must be a regular file. The supplied open stateid is validated while acquiring the state lock. Replay (`NFS4ERR_REPLAY`) is allowed through to seqid handling. The open owner must still exist; otherwise stale state returns `NFS4ERR_STALE`. Under owner mutex the v4.0 seqid is checked. If the owner is already confirmed, the operation returns `NFS4ERR_BAD_STATEID`. Otherwise it marks `so_confirmed = true`, updates the stateid under lock, and saves the response in the open owner replay cache.

State and persistence: mutates the open owner's confirmed flag, updates stateid sequencing/current stateid, and records the response for NFSv4.0 replay. It does not change FSAL open state.

Dependencies and integration: coupled to `OPEN` result flag `OPEN4_RESULT_CONFIRM`, owner replay cache, SAL stateid validation, and compound stateid propagation.

Risks: replay handling depends on `nfs4_check_stateid_acquire_state_lock` and `Check_nfs4_seqid_locked` cooperating while the response union is prefilled. Already-confirmed state must not accidentally advance seqids. Lock/ref cleanup is important on early stale paths.

Test signals: v4.1 not supported, non-regular FH, bad stateid, stale owner, seqid replay, already-confirmed owner, successful confirmation and replayed confirmation response.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open_confirm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open_downgrade.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open_downgrade.c

Purpose: implements `OPEN_DOWNGRADE`, reducing the share access/deny mode associated with an open stateid.

Important APIs and types: uses `OPEN_DOWNGRADE4args/res`, `state_t`, `state_owner_t`, `fsal_obj_handle`, and `fsal_openflags_t`. Key helpers are `share_downgrade_allowed` and `nfs4_do_open_downgrade_locked`, plus stateid/seqid APIs `nfs4_check_stateid_acquire_state_lock`, `Check_nfs4_seqid_locked`, `update_stateid_locked`, and `Copy_nfs4_state_req`.

Control flow: validates the current FH and requires a regular file. It validates the open stateid while acquiring the state lock, checks v4.0 seqid if needed, then calls `nfs4_do_open_downgrade_locked`. The helper verifies the requested share access and deny are subsets of current state. It also verifies the target mode was previously seen using `share_access_prev`/`share_deny_prev`; special handling allows target BOTH when READ and WRITE were separately seen. It converts target share bits into FSAL open flags and calls `fsal_reopen2(..., true)`. Success updates the open stateid and caches v4.0 response.

State and persistence: changes FSAL open/share reservation mode for an existing share state, updates stateid sequencing/current stateid, and uses replay cache. It does not directly edit the in-memory `share_access`/`share_deny` fields in the helper visible here; it relies on `fsal_reopen2`/state integration for effective downgrade behavior.

Dependencies and integration: depends on share history encoded during `OPEN`, FSAL reopen semantics, SAL stateid validation, v4.0 seqid replay, and export state locks.

Risks: if `fsal_reopen2` does not update SAL share fields, the in-memory state may remain broader than intended. The bit-history encoding uses `(1 << mode)` where `mode` can itself be a bitmask; tests must preserve this convention. Error logging uses a cause pointer to aid diagnosis.

Test signals: bad/non-regular FH, bad/replayed stateid, stale state, invalid subset access/deny, target share mode never previously opened, BOTH allowed from separate read/write opens, FSAL reopen failure, successful stateid update, and v4.0 response replay.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open_downgrade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_openattr.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_openattr.c

Purpose: provides the `OPENATTR` operation hook, but the operation is not implemented.

Important APIs and types: uses `OPENATTR4args`, `OPENATTR4res`, and `nfs_resop4`. The only public behavior is `nfs4_op_openattr`, with `nfs4_op_openattr_Free` as a no-op.

Control flow: the handler sets `resp->resop = NFS4_OP_OPENATTR`, unconditionally sets `res_OPENATTR4->status = NFS4ERR_NOTSUPP`, and returns `NFS_REQ_ERROR`. It does not inspect the target filehandle or the OPENATTR arguments beyond taking the union address.

State and persistence: no state changes, no filesystem operations, no allocations.

Dependencies and integration: used by the NFSv4 operation dispatch table to advertise a defined but unsupported operation. It depends only on core NFSv4 response types.

Risks: clients expecting named attribute directories receive `NOTSUPP`. Because no FH sanity check is performed, the unsupported status takes precedence over filehandle errors; this should match intended protocol behavior for unsupported ops.

Test signals: any OPENATTR request returns `NFS4ERR_NOTSUPP`; free hook is harmless; compound stops with `NFS_REQ_ERROR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_openattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putfh.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putfh.c

Purpose: implements `PUTFH`, installing a client-provided NFSv4 filehandle as the compound current filehandle and resolving it into either an MDS object or pNFS DS handle.

Important APIs and types: functions are `nfs4_ds_putfh`, `nfs4_mds_putfh`, `nfs4_op_putfh`, and no-op free. It uses `file_handle_v4`, `fsal_pnfs_ds`, `gsh_export`, `fsal_export`, `gsh_buffdesc`, `fsal_obj_handle`, and `compound_data_t`.

Control flow: top-level `nfs4_op_putfh` validates the wire FH with `nfs4_Is_Fh_Invalid`, allocates `data->currentFH` storage if needed, copies bytes into it, then dispatches to DS or MDS handling based on `nfs4_Is_Fh_DSHandle`. DS handling resolves the pNFS data server id through `pnfs_ds_get`, updates `op_ctx` with the DS and its MDS export, clears current entry, checks DS permissions if server/export changed, builds an FSAL DS handle via `pds->s_ops.make_ds_handle`, and marks the current file type regular. MDS handling resolves the export id, updates `op_ctx` export, clears current entry, checks export access if export changed, converts the opaque handle from wire to host with `wire_to_host`, creates an FSAL object handle, installs it as current entry, then drops the local ref.

State and persistence: mutates compound current FH/object/filetype and global per-request `op_ctx` export or pNFS DS context. It does not alter stable state or filesystem content.

Dependencies and integration: central integration point for filehandle encoding conventions, export manager, pNFS DS registry, FSAL handle digest/create APIs, access checks, credentials, and compound context cleanup.

Risks: input handle length is trusted after `nfs4_Is_Fh_Invalid`; MDS copies `fs_len` into a fixed `NFS4_FHSIZE` buffer and relies on validation. Export/DS context changes before later failures mean callers see the resolved context even on some errors. DS handles intentionally leave `current_obj` NULL, so later metadata ops must reject them.

Test signals: invalid FH, unknown export, unknown DS, export access denied/wrongsec, DS permission failure, `wire_to_host` failure, `create_handle` failure, successful MDS current object install, and DS current_ds install with regular file type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putfh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putpubfh.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putpubfh.c

Purpose: implements `PUTPUBFH` by delegating to `PUTROOTFH`, effectively treating the public filehandle as the pseudo root.

Important APIs and types: uses `nfs4_op_putrootfh`, `PUTPUBFH` response union behavior, and no-op free hook.

Control flow: the handler calls `nfs4_op_putrootfh(op, data, resp)` to perform all work, then overwrites `resp->resop` with `NFS4_OP_PUTPUBFH` before returning the same request result.

State and persistence: same state effects as `PUTROOTFH`: current compound object/FH and export context are set to the pseudo root. No independent persistence or allocation occurs here.

Dependencies and integration: depends entirely on `nfs4_op_putrootfh` for access checks, root export lookup, filehandle creation, and error status population.

Risks: because it reuses the `PUTROOTFH` response union and only changes `resop`, callers must agree that status layout is compatible. If public FH semantics ever diverge from root FH semantics, this shortcut will need replacement.

Test signals: Pseudo root success via PUTPUBFH, access failures inherited from PUTROOTFH, and response `resop` reported as `NFS4_OP_PUTPUBFH`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putpubfh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putrootfh.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putrootfh.c

Purpose: implements `PUTROOTFH`, setting the compound current filehandle to the root of the NFSv4 pseudo filesystem.

Important APIs and types: uses `PUTROOTFH4res`, `fsal_obj_handle`, `gsh_export`, and `fsal_status_t`. It calls `set_current_entry`, `get_gsh_export_by_pseudo`, `set_op_context_export`, `nfs4_export_check_access`, `nfs_export_get_root_entry`, `nfs4_FSALToFhandle`, and FSAL ref helpers.

Control flow: the handler clears the response struct, sets `resop`, clears any current entry, fetches the export for pseudo path `/`, and sets it in `op_ctx`. If no export is available it returns `NFS4ERR_NOENT`. It checks export access; plain access denial returns error without exposing the pseudo root, and other access setup failures are logged. It obtains the root FSAL object for the pseudo root export, installs it as current entry, drops the local ref, converts it into `data->currentFH`, and returns `NFS4_OK`.

State and persistence: mutates the compound current object/FH and request export context. No filesystem data or NFSv4 state is changed.

Dependencies and integration: foundational for path traversal from the pseudo root, export manager lookup by pseudo path, credentials/access setup, FSAL root object retrieval, and filehandle encoding.

Risks: `memset(resp, 0, sizeof(*resp))` assumes no previous response allocations are live for the same slot. Root export reference handling is delegated to `set_op_context_export`; callers must not leak the export ref returned by `get_gsh_export_by_pseudo`. Filehandle encoding failure after setting current entry leaves current object installed with error status.

Test signals: missing pseudo root export, access denied, wrong credentials/access setup failure, FSAL root lookup failure, filehandle encoding failure, and successful current FH/object/export installation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putrootfh.c -->
