# subset-b-009706 research

This grouped report covers the requested NFS-Ganesha NFS protocol helper, NFSACL, NLM, and RQUOTA files. Each section is source-tree aligned and bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs_proto_tools.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs_proto_tools.c

Purpose: `nfs_proto_tools.c` is the central protocol helper for NFSv3 weak cache consistency, NFSv4 attribute XDR translation, path validation, response sizing, FSAL attribute conversion, and optional NFSACL3 POSIX ACL conversion. It is used by many NFSv3 and NFSv4 operation handlers through `nfs_proto_tools.h`.

Important APIs/types/functions: NFSv3 helpers include `nfs_SetPostOpAttr`, `nfs_PreOpAttrFromFsalAttr`, `nfs_SetPreOpAttr`, `nfs_SetWccData`, `nfs3_Sattr_To_FSALattr`, and `nfs3_Fixup_FSALattr`. NFSv4 helpers include the `fattr4tab` dispatch table, many per-attribute `encode_*` and `decode_*` functions, `file_To_Fattr`, `nfs4_FSALattr_To_Fattr`, `nfs4_Fattr_To_FSAL_attr`, `bitmap4_to_attrmask_t`, `nfs4_Fattr_Supported`, `nfs4_Fattr_cmp`, `xdr_fattr4_encode`, and `xdr_encode_entry4`. NFSACL3-only helpers include `encode_posix_acl`, `decode_posix_acl`, and `nfs3_acl_2_fsal_acl`.

Control flow: attribute encode/decode is table driven. Requested bitmaps are filtered by minor version, server support, FSAL support masks, valid FSAL attribute masks, and special cases such as ACL synthesis from mode. Encoders write a bitmap and later patch the XDR attribute length. Decoders walk the bitmap in order and call each table entry's decode function, setting FSAL valid masks or returning NFSv4 protocol errors. `file_To_Fattr` performs access checks, optionally uses delegation callback attributes, otherwise calls FSAL `getattrs`, then builds an NFSv4 fattr blob.

State and persistence: this file does not persist state directly, but it consumes global request/export context (`op_ctx`, `nfs_param`), session response limits, FSAL object attributes, cached delegation callback attributes, and ACL refcounted objects. It allocates XDR buffers, path component arrays, net ACL structures, and FSAL ACL entries that callers must release through existing FSAL/NFS free paths.

Dependencies and integration points: the file sits between RPC/XDR wire structures and FSAL/export/idmapper/state subsystems. It calls FSAL object ops, `fsal_statfs`, `fsal_access`, `fsal_mode_to_acl`, id mapping (`name2uid`, `name2gid`, `xdr_encode_nfs4_owner/group`), export options and limits, NFSv4 ACL helpers, and NFSv3 file handle/cache helpers. It is a shared correctness point for `GETATTR`, `SETATTR`, `READDIR`, file creation, ACL handling, and response-size admission.

Risks: table-driven attributes are sensitive to exact XDR sizes and bitmap order. Missing valid-mask bits silently omit requested attributes except special ACL cases. ACL decoding rejects excessive ACE counts but still depends on correct owner/group mapping and cleanup. The sticky-bit helper appears to return false when any execute bit is set, which is unusual for directory sticky-bit semantics and should be validated against callers. Response-size accounting must match session cache rules. Test signals include NFSv3 WCC post/pre attribute behavior, NFSv4 GETATTR/SETATTR round trips across minor versions, ACL get/set including unmapped users, `READDIR` rdattr error encoding, delegation timestamp callback attributes, response-too-big paths, and quota/FS stat attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs_proto_tools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/CMakeLists.txt

Purpose: builds the optional NFSACL protocol object library. It defines `nfsacl_STAT_SRCS` as `nfsacl_Null.c`, `nfsacl_getacl.c`, and `nfsacl_setacl.c`, then creates the `nfsacl` object target.

Important APIs/types/functions: this file contributes build metadata rather than C APIs. Its important integration points are `add_library(nfsacl OBJECT ...)`, `add_sanitizers(nfsacl)`, `set_target_properties(... -fPIC)`, and optional LTTng trace-header dependency wiring.

Control flow: parent protocol CMake logic enters this directory only when `USE_NFSACL3` is enabled. The target is compiled as position-independent object code and later linked into the daemon/library aggregate.

State and persistence: no runtime state. Build state includes target properties, sanitizer instrumentation, and generated trace header dependency ordering when `USE_LTTNG` is set.

Dependencies and integration points: integrates with the top-level `Protocols/CMakeLists.txt` feature flag and the generated LTTng property include under the binary directory.

Risks and test signals: build omissions here remove RPC handlers even if XDR/procedure tables expect them. Test by configuring with and without `USE_NFSACL3`, with sanitizers and LTTng enabled, and verifying `nfsacl` object files are linked only in the enabled build.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_Null.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_Null.c

Purpose: implements the NFSACL NULL procedure. It is a ping/no-op RPC endpoint used for protocol reachability and dispatch validation.

Important APIs/types/functions: exports `nfsacl_Null(nfs_arg_t *, struct svc_req *, nfs_res_t *)` and `nfsacl_Null_Free(nfs_res_t *)`.

Control flow: the handler logs the call on `COMPONENT_NFSPROTO` at full debug and returns `0`, the success convention used by these null handlers. The free routine intentionally does nothing.

State and persistence: no state is read or modified. Arguments, request, and result are ignored.

Dependencies and integration points: includes common NFS core, export, logging, hashtable, and NFSACL headers so it matches the protocol procedure signature expected by `nfs_proto_functions.h`.

Risks and test signals: low behavioral risk, but procedure registration depends on this symbol. Test via an NFSACL NULL RPC and by validating that result cleanup does not attempt to free uninitialized result fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_Null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_getacl.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_getacl.c

Purpose: implements NFSACL GETACL for NFSv3-style POSIX ACL retrieval when `USE_NFSACL3` is compiled in.

Important APIs/types/functions: exports `nfsacl_getacl` and `nfsacl_getacl_Free`. It uses `nfs3_FhandleToCache`, FSAL `getattrs`, `fsal_acl_2_posix_acl`, POSIX `acl_valid`, `encode_posix_acl`, `nfs3_Fixup_FSALattr`, `fsal_release_attrs`, and `nfs_RetryableError`.

Control flow: it prepares NFSv3 ACL attributes, resolves the file handle to an FSAL object, fetches attributes/ACL, validates the caller mask against allowed ACL bits, optionally encodes access and default ACLs, fixes returned attributes, sets `NFS3_OK`, and releases all object/ACL references. Failures map FSAL status to NFSv3 status and may return `NFS_REQ_DROP` for retryable errors.

State and persistence: no persistent mutation. It allocates encoded ACL buffers into the result and obtains temporary POSIX ACLs that are freed before return. It also fetches attributes whose embedded references are released.

Dependencies and integration points: bridges NFSACL wire masks (`NFS_ACL`, `NFS_ACLCNT`, `NFS_DFACL`, `NFS_DFACLCNT`) with FSAL ACL storage and NFSv3 post-op attributes. It depends on the helper conversions in `nfs_proto_tools.c`.

Risks and test signals: invalid masks, missing ACLs, invalid POSIX ACLs, and retryable FSAL failures are key branches. Result free currently does nothing, so ownership of encoded ACL result storage should be checked against the generated XDR free path. Test access/default ACL retrieval for files and directories, empty ACLs, invalid masks, stale handles, and FSAL transient errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_getacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_setacl.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_setacl.c

Purpose: implements NFSACL SETACL, translating NFSv3 ACL wire structures into FSAL ACL attributes and applying them to an FSAL object.

Important APIs/types/functions: exports `nfsacl_setacl` and `nfsacl_setacl_Free`. It uses `nfs3_FhandleToCache`, `nfs3_acl_2_fsal_acl`, `nfs_get_grace_status`, `fsal_setattr`, FSAL `getattrs`, `fsal_release_attrs`, and `nfs_RetryableError`.

Control flow: the handler initializes response attributes as not-following, resolves the target handle, validates that an access ACL is present, rejects default ACLs on non-directories, converts access/default ACLs to `ATTR_ACL`, checks the grace-period gate, applies `fsal_setattr` with bypass semantics, fetches post-operation attributes, and maps success or FSAL errors to NFSv3 status.

State and persistence: this file mutates persistent file ACL metadata through FSAL `setattr`. It temporarily holds an FSAL object reference and an FSAL ACL attrlist that must be released to drop inherited ACL references.

Dependencies and integration points: tied to NFS server grace handling, FSAL ACL conversion, NFSv3 status mapping, and NLM share bypass comments. It uses NFSACL-specific result fields and NFSv3 attributes.

Risks and test signals: grace handling maps to `NFS3ERR_JUKEBOX`/drop behavior. A notable code path sets `res->res_getacl...attributes_follow` instead of the setacl result union after a successful getattrs, which deserves focused verification. Test directory and non-directory default ACLs, access ACL absence, FSAL setattr failure, grace period, retry/drop options, and returned post-op attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_setacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/CMakeLists.txt

Purpose: builds the NLM protocol object library used for NFSv3 locking, share reservations, NSM monitoring, async callbacks, and the standalone `sm_notify` source when included in the source list.

Important APIs/types/functions: build metadata includes `nlm_STAT_SRCS`, `add_library(nlm OBJECT ...)`, sanitizer instrumentation, `-fPIC`, and optional LTTng generated-header dependencies. The source list includes lock/test/cancel/unlock/share/unshare/null/free-all/sm-notify handlers plus `nlm_async.c`, `nlm_util.c`, and `nsm.c`.

Control flow: CMake defines and compiles all NLM protocol source files into one object library. Parent protocol build logic controls whether this directory participates.

State and persistence: no runtime state. Build output state is object files with consistent sanitizer, PIC, and trace-generation dependencies.

Dependencies and integration points: integrates with core NFS-Ganesha protocol dispatch, state/SAL, FSAL, RPC/XDR, and optional LTTng tracing through the compiled sources.

Risks and test signals: missing one source causes unresolved symbols or disabled lock semantics. Test feature-enabled builds, LTTng builds, sanitizer builds, and link checks for all NLM procedure handlers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Cancel.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Cancel.c

Purpose: implements NLMv4 CANCEL and CANCEL_MSG, canceling a blocked range lock request.

Important APIs/types/functions: exports `nlm4_Cancel`, `nlm4_Cancel_Message`, and `nlm4_Cancel_Free`; uses `nlm_process_parameters`, `state_cancel`, `nlm_convert_state_error`, async scheduling helpers, and netobj cookie copy/free helpers.

Control flow: it rejects missing exports as `NLM4_STALE_FH`, copies the cookie, checks grace-period state, resolves the FSAL object/NLM owner/client without requiring owner existence, calls `state_cancel`, maps state errors, and releases refs. The message variant obtains non-monitoring clients, invokes the synchronous function, schedules an async CANCEL_RES, then always drops the original RPC response.

State and persistence: cancels in-memory blocked lock state in SAL/state. It does not directly persist data but affects pending lock queues and grant callbacks.

Dependencies and integration points: depends on NLM utility parameter decoding, SAL state cancellation, NSM/NLM client reference management, and `nlm_async.c` callback transport.

Risks and test signals: the file uses `res_nlm4test.cookie` in some places while sending `res_nlm4`, so cookie union consistency should be tested. Test cancellation during grace, missing owner/client, stale handles, async message response failure, and block queue cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Free_All.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Free_All.c

Purpose: implements NLM_FREE_ALL, releasing all locks for a named NSM client.

Important APIs/types/functions: exports `nlm4_Free_All` and `nlm4_Free_All_Free`. It uses `get_nsm_client`, `state_nlm_notify`, and `dec_nsm_client_ref`.

Control flow: it looks up the NSM client by name. If found, it invokes `state_nlm_notify(nsm_client, false, 0)`, which uses SM_NOTIFY-like cleanup semantics for that client, logs failures because the protocol result is void, releases the client reference, and returns `NFS_REQ_OK`.

State and persistence: mutates in-memory NLM lock state by releasing locks for a client. No result payload or persistent file metadata is written.

Dependencies and integration points: shares cleanup semantics with NSM notification handling and SAL lock ownership tracking.

Risks and test signals: no protocol error can be returned, so observability depends on logs. Test unknown clients, clients with active locks, clients rebooted with state protection, and state cleanup failure logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Free_All.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Granted_Res.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Granted_Res.c

Purpose: handles client replies to server-initiated `NLMPROC4_GRANTED_MSG` callbacks for previously blocked locks.

Important APIs/types/functions: exports `nlm4_Granted_Res` and `nlm4_Granted_Res_Free`; uses `state_find_grant`, `state_release_grant`, `state_complete_grant`, `nlm_signal_async_resp`, export reference/context setup, and `export_ready`.

Control flow: it decodes/logs the cookie, finds the pending grant cookie entry, ignores old replies with missing entries or block data, installs the related export into `op_ctx`, and either releases the grant on client error/stale export or completes it and signals the async sender waiting for the acknowledgement.

State and persistence: updates in-memory grant cookie/blocking-lock state. It may complete or release a pending lock grant, changing subsequent lock availability.

Dependencies and integration points: pairs with `nlm_granted_callback` and `nlm_send_async`; depends on export lifetime management and the state cookie table.

Risks and test signals: stale exports, duplicate/old replies, missing block data, and failed release paths are important. Test successful grant acknowledgement, denied grant response, stale export cleanup, old cookie ignore, and async wait signalling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Granted_Res.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Lock.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Lock.c

Purpose: implements NLMv4 LOCK, NM_LOCK, and LOCK_MSG for byte-range locking.

Important APIs/types/functions: exports `nlm4_Lock`, `nlm4_Lock_Message`, and `nlm4_Lock_Free`; uses `nlm_process_parameters`, `state_lock`, `state_deleg_conflict`, `nfs_get_grace_status`, `nlm_convert_state_error`, async response helpers, and refcount release functions.

Control flow: it identifies monitored versus non-monitored lock variants, rejects missing exports, copies the cookie, gates reclaim/non-reclaim requests through grace handling unless FSAL handles grace, resolves object/client/owner/state/block data, checks NFSv4 delegation conflicts, increments anonymous operation tracking while locking, calls SAL `state_lock` under state lock, maps state outcomes, frees unused block data, and releases refs. The message variant schedules a LOCK_RES callback and drops the direct response.

State and persistence: creates or modifies in-memory NLM lock state and may enqueue blocking lock grant data. It does not write file data but enforces persistent client-visible lock behavior.

Dependencies and integration points: integrates FSAL max-file-size limits, NSM monitoring, NLM owner/client tables, SAL locking, NFS grace state, and async callbacks.

Risks and test signals: range overflow conversion, delegation conflict drop, grace/reclaim behavior, blocked lock cleanup, and reference release are high-risk. Test blocking/nonblocking locks, NM_LOCK, reclaim during grace, lock past max file size, delegation conflict, async message response, and denied/no-locks cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Null.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Null.c

Purpose: implements the NLM NULL procedure, a no-op endpoint for RPC reachability.

Important APIs/types/functions: exports `nlm_Null` and `nlm_Null_Free`.

Control flow: logs the call on `COMPONENT_NLM` and returns success. The result free function has no work.

State and persistence: no runtime state is read or mutated.

Dependencies and integration points: depends only on NLM/common headers and the standard NFS procedure signature.

Risks and test signals: minimal logic risk. Test that the procedure dispatches across supported NLM versions and does not require initialized result storage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Share.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Share.c

Purpose: implements NLMv4 SHARE, creating DOS-style share reservations for NFSv3 clients.

Important APIs/types/functions: exports `nlm4_Share` and `nlm4_Share_Free`; uses `nfs_param.core_param.disable_NLM_SHARE`, `nlm_process_share_parms`, `state_nlm_share`, `check_and_remove_conflicting_client`, grace handling, and netobj helpers.

Control flow: it optionally fails all share calls if disabled, rejects missing exports, logs file handle/owner/access/deny details, copies the cookie, handles grace/reclaim admission, resolves object/client/owner/share state, calls `state_nlm_share`, retries once after removing expired conflicting clients on denial, maps state errors, and releases refs.

State and persistence: creates or updates in-memory NLM share reservation state. No file metadata is persisted, but access denial semantics become visible to other clients.

Dependencies and integration points: ties NLM share wire structures to SAL share state, NSM/NLM client management, export grace support, and global NFS configuration.

Risks and test signals: disabled-share behavior, reclaim gating, expired-client conflict removal, and cleanup after `nlm_process_share_parms` errors need coverage. Test read/write/deny combinations, conflict/expired client retry, grace reclaim/non-reclaim, non-regular files, and cookie free paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Sm_Notify.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Sm_Notify.c

Purpose: handles incoming NSM `SM_NOTIFY` callbacks delivered through the NLM program when monitored clients reboot.

Important APIs/types/functions: exports `nlm4_Sm_Notify` and `nlm4_Sm_Notify_Free`; uses `is_loopback`, `get_nsm_client`, `state_nlm_notify`, `set_op_context_client`, `SetClientIP`, and op context caller/client restoration.

Control flow: only loopback callers are honored. The handler temporarily clears client/caller context so the NSM client is looked up by caller name, restores the matched Ganesha client for cleanup, calls `state_nlm_notify(nsm_client, true, state)`, releases the NSM client, then restores original op context values.

State and persistence: mutates in-memory lock/share state by removing or protecting state according to the reboot state number. No result payload is returned.

Dependencies and integration points: integrates local statd notification delivery with NLM state cleanup and request context bookkeeping.

Risks and test signals: loopback validation, op context restoration, caller-name mapping, and cleanup semantics are important. Test spoofed non-loopback notify, known/unknown clients, reboot state protection, and restoration when original client is null or changed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Sm_Notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Test.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Test.c

Purpose: implements NLMv4 TEST and TEST_MSG, checking whether a proposed byte-range lock would conflict.

Important APIs/types/functions: exports `nlm4_Test`, `nlm4_Test_Message`, and `nlm4_Test_Free`; uses `nlm_process_parameters`, `state_test`, `nlm_process_conflict`, `nlm_convert_state_error`, async test response helpers, and holder netobj cleanup.

Control flow: it rejects missing exports, copies the cookie, checks grace status, resolves lock parameters with owner care, calls `state_test`, fills conflict holder details on `STATE_LOCK_CONFLICT`, releases state/client/owner/object refs, and returns the lock test status. The message variant schedules TEST_RES asynchronously and drops the direct response.

State and persistence: reads lock state and may take temporary state/owner references. It should not create persistent locks, though helper lookup can create/return NLM state depending on care semantics.

Dependencies and integration points: bridges NLM test requests to SAL lock conflict reporting and uses async callback infrastructure for message procedures.

Risks and test signals: conflict holder ownership and `oh` allocation/free are critical. Test granted/no-conflict, denied with holder, grace period denial, stale handles, unknown owners, async TEST_MSG, and holder cleanup in `nlm4_Test_Free`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Unlock.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Unlock.c

Purpose: implements NLMv4 UNLOCK and UNLOCK_MSG for releasing byte-range locks.

Important APIs/types/functions: exports `nlm4_Unlock`, `nlm4_Unlock_Message`, and `nlm4_Unlock_Free`; uses `nlm_process_parameters` with `CARE_NOT`, `state_unlock`, `nlm_convert_state_error`, async unlock response helpers, and netobj free.

Control flow: it rejects missing exports, copies the cookie, resolves object/client/owner/state without requiring existing owner/client, treats missing state as success, calls `state_unlock` when state exists, maps errors, releases state/client/owner/object refs, and returns success. The message handler sends an async UNLOCK_RES and drops the direct RPC reply.

State and persistence: mutates in-memory lock state by releasing locks. No persistent file data is written.

Dependencies and integration points: uses common NLM parameter conversion, SAL unlock, NSM/NLM client tracking, and async callback transport.

Risks and test signals: success-on-missing-owner/client is protocol-significant. Test unlock existing and nonexistent locks, missing client/owner, stale file handle, non-regular files, async response failure, and cleanup of copied cookies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Unlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Unshare.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Unshare.c

Purpose: implements NLMv4 UNSHARE, removing a share reservation.

Important APIs/types/functions: exports `nlm4_Unshare` and `nlm4_Unshare_Free`; uses `disable_NLM_SHARE`, `nlm_process_share_parms`, `state_nlm_share(..., unshare=true)`, netobj cookie helpers, and reference release helpers.

Control flow: it optionally fails when share support is disabled, rejects missing exports, logs details, copies the cookie, resolves object/client/owner/share state with `CARE_NOT`, invokes `state_nlm_share` in unshare mode, maps errors to NLM statuses, releases refs, and returns `NFS_REQ_OK`.

State and persistence: removes or updates in-memory share reservations. Missing client/owner under `CARE_NOT` is treated as granted because there is nothing to remove.

Dependencies and integration points: pairs with `nlm_Share.c` and the SAL share state machine.

Risks and test signals: unlike SHARE, this does not do grace handling. Test unshare existing and nonexistent shares, disabled share config, non-regular files, stale handles, denied state errors, and cookie cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Unshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_async.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_async.c

Purpose: provides async NLM callback scheduling, callback RPC transport, and acknowledgement signalling for NLM message procedures and granted-lock callbacks.

Important APIs/types/functions: exports `nlm_send_async_res_nlm4`, `nlm_send_async_res_nlm4test`, `find_peer_addr`, `nlm_send_async`, and `nlm_signal_async_resp`. It defines `nlm_reply_proc`, `nlm_async_resp_mutex`, `nlm_async_resp_cond`, and a single `resp_key`.

Control flow: response-scheduling helpers deep-copy cookies into a `state_async_queue_t` and call `state_async_schedule`. `nlm_send_async` lazily creates/reuses callback clients, handles TCP address binding and rpcbind lookup, retries failures, performs a one-shot RPC call, optionally waits up to five seconds for `nlm_signal_async_resp`, and tears down failed callback clients.

State and persistence: maintains per-NLM-client callback RPC client/auth handles and global wait state for one response key. It does not persist data but controls callback completion and blocking-lock grant acknowledgement.

Dependencies and integration points: depends on TI-RPC client APIs, rpcbind, state async queues, NLM XDR routines, `nfs_param`, and network address helpers.

Risks and test signals: global `resp_key` serializes acknowledgement waits and can be sensitive to concurrent callbacks. TCP callback setup, IPv4-mapped IPv6 conversion, retry handling, and copied result ownership are high-risk. Test TCP/UDP callbacks, DNS failures, rpcbind failure, callback timeout, granted acknowledgement signalling, denied TEST holder copy, and async schedule failure cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_util.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_util.c

Purpose: contains shared NLM utilities for cookies/netobjs, lock/share parameter decoding, NLM-to-SAL status mapping, initialization, and granted-lock callback construction.

Important APIs/types/functions: exports `next_granted_cookie`, `lock_result_str`, `lock_end`, `fill_netobj`, `copy_netobj`, `netobj_free`, `netobj_to_string`, `nlm_init`, `free_grant_arg`, `nlm_process_parameters`, `nlm_process_share_parms`, `nlm_process_conflict`, `nlm_convert_state_error`, and `nlm_granted_callback`.

Control flow: parameter processors resolve NFSv3 file handles to FSAL objects, reject non-regular files and out-of-range offsets, look up NSM/NLM clients and owners according to `care_t`, obtain NLM state, build optional block data, and return either an NLM status or `-1` on success. Grant callback code adds a grant cookie, builds a `NLMPROC4_GRANTED_MSG`, schedules async work, and cancels the grant if scheduling fails.

State and persistence: initializes grace/cookie counters, creates/cancels grant cookie entries, allocates block data, and obtains client/owner/state refs. It mutates in-memory locking state indirectly through grant cookie management.

Dependencies and integration points: integrates `nfs3_FhandleToCache`, FSAL max-file-size, NSM monitor/client APIs, SAL state owner/state/cookie APIs, and NLM async sender.

Risks and test signals: ownership/ref cleanup in error branches is critical. Range overflow handling changes length to zero-to-EOF. `care_t` drives protocol semantics for missing owners. Test every lock/share caller with missing handles, non-regular objects, max-file-size edge cases, owner/client misses under each care mode, blocked lock grant success/failure, and conflict holder construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nsm.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nsm.c

Purpose: manages local NSM/statd monitor and unmonitor RPCs for NLM clients.

Important APIs/types/functions: exports `nsm_connect`, `nsm_disconnect`, `nsm_monitor`, `nsm_unmonitor`, and `nsm_unmonitor_all`; internal helpers are `nsm_monitor_noretry` and `nsm_unmonitor_noretry`. Global state includes `nsm_mutex`, `nsm_clnt`, `nsm_auth`, `nsm_count`, and `nodename`.

Control flow: connection setup obtains local nodename and creates a TCP RPC client to localhost statd. Monitor/unmonitor functions lock host and global NSM mutexes, avoid duplicate operations via `ssc_monitored`, issue `SM_MON`/`SM_UNMON`, update monitor count and atomics, and retry once after failures. `nsm_unmonitor_all` sends `SM_UNMON_ALL` for the NLM callback identity.

State and persistence: persists process-local statd client/auth handles and monitor counts. It also updates per-NSM-client monitored flags. Actual monitoring state is persisted externally in statd.

Dependencies and integration points: depends on TI-RPC/statd XDR, `state_nsm_client_t`, atomic helpers, admin shutdown configuration, and NLM callback identity constants.

Risks and test signals: mutex ordering, retry behavior after statd restart, monitor count underflow, nodename lifetime, and shutdown unmonitor policy need coverage. Test statd unavailable, statd restart retry, double monitor/unmonitor, admin shutdown with `unmonitor_on_shutdown` false, and unmonitor-all cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/sm_notify.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/sm_notify.c

Purpose: standalone helper program to send an NSM `SM_NOTIFY` RPC, useful for notification delivery/testing outside the main daemon.

Important APIs/types/functions: defines `LogMallocFailure`, `nsm_notify_1`, and `main`. It parses `-p`, `-l`, `-m`, `-r`, and `-s` options and uses TI-RPC datagram client calls.

Control flow: `main` validates required options, creates and binds a nonblocking UDP socket to the local address/port, resolves the remote statd port with `rpcb_find_mapped_addr`, creates a datagram RPC client, fills `notify` with monitor name and state, calls `nsm_notify_1`, frees rpcbind buffers, destroys the client, closes the socket, and exits. `nsm_notify_1` sends `SM_NOTIFY` with a 15-second timeout.

State and persistence: no daemon state. It sends one remote notification and exits.

Dependencies and integration points: depends on generated NSM XDR, TI-RPC, rpcbind, socket APIs, and Ganesha memory wrappers.

Risks and test signals: option length checks are bounded, but `inet_addr` accepts limited forms and error reporting is coarse. Test missing options, bind failure, rpcbind failure, successful notify, non-default port, and unreachable remote statd.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/sm_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/CMakeLists.txt

Purpose: builds the optional RQUOTA protocol object library.

Important APIs/types/functions: defines `rquota_STAT_SRCS` with null, getquota, getactivequota, setquota, setactivequota, and common helpers; creates `rquota` object target with sanitizers and `-fPIC`; optionally depends on generated LTTng trace headers.

Control flow: parent protocol build enters this directory when `USE_RQUOTA` is enabled. The object library is compiled and later linked into the server.

State and persistence: no runtime state; only build target metadata.

Dependencies and integration points: integrates with `Protocols/CMakeLists.txt`, generated tracing, and all RQUOTA procedure symbols used by dispatch/XDR code.

Risks and test signals: the source list includes `rquota_setquota.c` even though it is outside this work item, so build validation should cover the complete target. Test enabled/disabled RQUOTA builds, sanitizer builds, LTTng builds, and link resolution for all RQUOTA procedures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_Null.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_Null.c

Purpose: implements the RQUOTA NULL procedure for basic RPC reachability.

Important APIs/types/functions: exports `rquota_Null` and `rquota_Null_Free`.

Control flow: logs `RQUOTA_NULL` at full debug and returns success. Result cleanup is intentionally empty.

State and persistence: no state is touched.

Dependencies and integration points: includes RQUOTA and common NFS core/export headers to conform to protocol dispatch signatures.

Risks and test signals: low risk. Test a NULL RPC and result cleanup behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_Null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_common.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_common.c

Purpose: provides shared RQUOTA path normalization.

Important APIs/types/functions: exports `check_handle_lead_slash(char *quota_path, char *temp_path, size_t temp_path_size)`.

Control flow: if a quota path is absolute, it returns the original pointer. For relative/tag-like paths, it fetches the root pseudo export, reads the export full path under RCU/refstr protection, copies it to the caller buffer, adds a slash if needed, appends the quota path, and returns the buffer. Overlong paths or missing export/fullpath return `NULL`.

State and persistence: no persistent mutation. It takes and releases export and refstr references and uses caller-supplied temporary storage.

Dependencies and integration points: integrates RQUOTA handlers with export manager path lookup and the root pseudo export.

Risks and test signals: path length checks, root export absence, RCU/refstr lifetime, and relative path handling determine quota lookup correctness. Test absolute paths, relative paths, long paths, missing root pseudo export, and root fullpath without trailing slash.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_getactivequota.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_getactivequota.c

Purpose: placeholder implementation for RQUOTA GETACTIVEQUOTA.

Important APIs/types/functions: exports `rquota_getactivequota` and `rquota_getactivequota_Free`.

Control flow: logs the operation and returns success without filling a meaningful quota result.

State and persistence: no state is read or written.

Dependencies and integration points: compiled into the RQUOTA target and used by dispatch tables, but currently does not call FSAL quota APIs.

Risks and test signals: clients expecting active quota semantics may see an effectively unimplemented result path. Test protocol compatibility and confirm generated XDR defaults are acceptable for supported clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_getactivequota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_getquota.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_getquota.c

Purpose: implements RQUOTA GETQUOTA and extended GETQUOTA by resolving an export and reading FSAL quota state.

Important APIs/types/functions: exports `rquota_getquota` and `rquota_getquota_Free`; uses `check_handle_lead_slash`, export lookups by tag/pseudo/path, `set_op_context_export`, `nfs_req_creds`, and FSAL `get_quota`.

Control flow: it selects quota type/id from classic or extended version arguments, initializes status to `Q_EPERM`, normalizes the path, finds the matching export using tag/pseudo/path policy, installs the export into `op_ctx`, obtains request credentials, calls `get_quota`, maps no-quota to `Q_NOQUOTA`, and on success scales block counts/limits down until they fit 32-bit RQUOTA fields while increasing block size.

State and persistence: reads persistent FSAL quota accounting but does not modify it. It updates request context with an export reference that is expected to be released by normal request cleanup.

Dependencies and integration points: bridges RQUOTA wire structures, export manager, credentials, and FSAL quota APIs. It relies on `os/quota.h` for `USRQUOTA`.

Risks and test signals: export resolution policy, credential failure, scaling overflow, and result defaults are important. Test absolute/pseudo/tag paths, extended group/project quota types if supported, no quota, large 64-bit quota values, credential denial, and missing export.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_getquota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_setactivequota.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_setactivequota.c

Purpose: placeholder implementation for RQUOTA SETACTIVEQUOTA.

Important APIs/types/functions: exports `rquota_setactivequota` and `rquota_setactivequota_Free`.

Control flow: logs the operation and returns success without changing quota activation.

State and persistence: no state is modified.

Dependencies and integration points: compiled into the RQUOTA object target and satisfies dispatch symbol requirements.

Risks and test signals: the success return may mask unimplemented semantics for clients that expect active quota changes. Test client behavior and consider explicit unsupported status if protocol compatibility allows it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_setactivequota.c -->
