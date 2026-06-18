# Research Group: subset-b-009705

This grouped research report covers the listed NFS-Ganesha NFS protocol source files. Each file section is bounded by the required reconciliation markers and uses the original source path as its title.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_read.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_read.c

## Purpose
Implements NFSv4 READ, NFSv4.2 READ_PLUS, IO_ADVISE, and SEEK handling inside compound execution. It validates current file handles and stateids, routes pNFS data-server handles directly to DS operations, enforces export read size/offset limits, manages asynchronous FSAL read completion, maps FSAL results into NFS status, and records server I/O statistics.

## Important APIs, Types, and Functions
- `struct nfs4_read_data` is the heap continuation for async reads. It stores the response, optional owner reference, compound data, object handle, async flags, QoS flag, READ_PLUS `io_info`, and embedded `fsal_io_arg`.
- `nfs4_op_read`, `nfs4_op_read_plus`, `nfs4_op_io_advise`, and `nfs4_op_seek` are exported operation handlers.
- `nfs4_read` is the shared READ/READ_PLUS implementation. It calls `nfs4_sanity_check_FH`, `nfs4_Check_Stateid`, `allow_read`, `check_resp_room`, `fsal_read2`, and the FSAL `read2` object op.
- `nfs4_complete_read` finalizes EOF, result length, iovec ownership, statistics, owner/clientid cleanup, and state reference release.
- `op_dsread` and `op_dsread_plus` call `op_ctx->ctx_pnfs_ds->s_ops.dsh_read` or `dsh_read_plus` for pNFS data-server file handles.
- `nfs4_op_read_resume` and `nfs4_op_read_plus_resume` finish async, QoS, and FSAL-resume continuations from `data->op_data`.
- `xdr_READ4res_uio_release` releases read UIO buffers unless RDMA response buffers are in use.

## Control Flow
READ first sets `resp->resop`, detects minorversion data-server handles, and otherwise enters `nfs4_read`. The shared path checks that CurrentFH is a regular file, validates the input stateid, resolves open state from share/lock/delegation state, checks open mode and owner confirmation, handles anonymous special stateids and delegation conflicts, applies pre-read access policy, clamps against `MaxRead` and `MaxOffsetRead`, reserves response room, initializes the response iovec, allocates `nfs4_read_data`, optionally schedules QoS, and calls `fsal_read2`. If the callback completes before exit, the function completes inline; otherwise it returns `NFS_REQ_ASYNC_WAIT` and resume functions complete later.

READ_PLUS uses the same read path with an `io_info` pointer. On success `nfs4_complete_read_plus` overlays READ result state onto the READ_PLUS union and fills either `NFS4_CONTENT_HOLE` or `NFS4_CONTENT_DATA`. IO_ADVISE is NFSv4.2-only, validates a stateid, calls `obj_ops->io_advise`, and persists hints in `state_found->state_data.io_advise`. SEEK is also NFSv4.2-only and calls `obj_ops->seek2` with data/hole/adbs content selection.

## State and Persistence Behavior
The file touches transient compound state (`data->op_data`, `op_resp_size`, `current_obj`), NFS state refs, owner refs, and `op_ctx->clientid` for v4.0 owner-scoped I/O. State references are intentionally held through async callbacks and released in completion. IO_ADVISE stores hint bits on the open state for later read/seek operations. There is no durable storage update, but reads affect server statistics and QoS accounting.

## Dependencies and Integration Points
Depends on FSAL object operations (`read2`, `getattrs`, `test_access`, `io_advise`, `seek2`), SAL state management, pNFS DS callbacks, export limits and access policy, QoS (`qos_process`, `nfs4_qos_read_cb`), RDMA-aware response buffers, XDR UIO release, and LTTng tracepoints. The compound engine must invoke the matching resume handlers while `data->op_data` is live.

## Risks
- Async flag races around `ASYNC_PROC_DONE` and `ASYNC_PROC_EXIT` must preserve exactly one completion/free path.
- READ_PLUS uses union overlay behavior with READ results; changes to XDR unions or response structs could break `nfs4_complete_read_plus`.
- Zero-length, max-offset, and maxread clamping paths must leave response iovec and release callbacks in a valid state.
- pNFS DS READ_PLUS uses a directly allocated buffer and relies on FSAL-provided `io_info` fields; ownership must match free logic.
- EOF correction may call `getattrs` on completion; failure silently leaves FSAL EOF semantics in place.

## Test Signals
Exercise regular READ, zero-length READ, offset beyond `MaxOffsetRead`, size clamping, all-zero/all-one stateids, share-deny conflicts, delegation conflicts, v4.0 owner-confirmation failures, async FSAL completion before and after handler exit, FSAL `fsal_resume`, QoS delay and rate-control paths, pNFS DS reads, RDMA response-buffer cleanup, READ_PLUS data/hole responses, IO_ADVISE persistence, and SEEK for data/hole/not-supported cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_readdir.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_readdir.c

## Purpose
Implements NFSv4 READDIR, including attribute encoding for directory entries, cookie-verifier handling, response-size limiting, dircount byte-budget enforcement, junction traversal for nested exports, and RDMA-aware serialized XDR result buffers.

## Important APIs, Types, and Functions
- `struct nfs4_readdir_cb_data` tracks the XDR stream, entry buffer, maxcount, dircount accounting, requested attributes, compound data, error state, and saved export context used during junction traversal.
- `nfs4_op_readdir` is the public handler.
- `nfs4_readdir_callback` is passed to `fsal_readdir` and encodes each `entry4` or error attribute record into the preallocated XDR memory buffer.
- `restore_data` restores `op_ctx` export and request credentials after a junction traversal or failure.
- `xdr_dirlist4_uio_release` releases the response UIO buffers when XDR no longer references them.

## Control Flow
The handler validates CurrentFH as a directory, derives `maxcount` from session response room, configured readdir response size, and client `maxcount`, rejects reserved cookies 1 and 2, validates and filters requested attributes, optionally builds a cookie verifier from the directory change attribute, allocates the entries buffer, creates an XDR memory stream, and calls `fsal_readdir`. The callback accounts for base entry size, encoded filename size, and dircount bytes; optionally crosses junction exports to gather attributes from the target export root; handles WRONGSEC, ACCESS, MOVED, and RDATTR_ERROR; temporarily swaps `data->current_obj` to encode filesystem attributes; and rolls the XDR stream back when an entry cannot fit.

After `fsal_readdir`, the handler converts tracker errors, writes final `entry_follows`/EOF booleans, wraps the encoded byte range in `struct xdr_uio`, transfers buffer ownership to the response, copies the cookie verifier, and destroys the XDR stream. If no entry fit, it returns EOF state directly in `reply.eof`.

## State and Persistence Behavior
READDIR does not persist filesystem state, but it mutates transient compound context while crossing junctions and while encoding attributes. The callback saves and restores export context and credentials. The response buffer is handed off by setting `tracker.entries = NULL`; free behavior is tied to UIO release and RDMA buffer usage. Cookie verifier state is derived from the directory change attribute when the export option enables it.

## Dependencies and Integration Points
Depends on FSAL readdir and object access checks, export manager junction fields (`junction_export`, `jct_lock`), credential rebuilding through `nfs_req_creds`, attribute/XDR helpers (`bitmap4_to_attrmask_t`, `xdr_encode_entry4`, `xdr_nfs4_fattr_fill_error`), response sizing, and RDMA buffer helpers. It is tightly integrated with pseudo export behavior because READDIR must present junction entries with the same filehandle and attributes that LOOKUP would expose.

## Risks
- Junction traversal lock and export-reference ordering is delicate; failure to restore context can leak credentials/export state into later compound operations.
- Buffer rollback must encode a false `entry_follows`; XDR position mistakes can corrupt the directory list.
- `dircount` is enforced as cookie plus XDR name bytes, while `maxcount` limits the whole serialized response; regressions here affect client pagination.
- Requested attribute combinations around WRONGSEC, RDATTR_ERROR, FS_LOCATIONS, and MOUNTED_ON_FILEID need protocol-specific handling.
- UIO allocation size and RDMA buffer ownership must match release expectations.

## Test Signals
Test empty directories, one-entry and many-entry pagination, cookie 1/2 rejection, cookie-verifier mismatch, `maxcount` too small, `dircount` limiting after some entries, long names, unsupported or unreadable attributes, ACL attribute access failures, referrals and junctions, WRONGSEC with and without allowed attrs, RDMA buffer responses, and repeated READDIR pages where cookies and EOF remain stable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_readlink.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_readlink.c

## Purpose
Implements NFSv4 READLINK for symbolic links. It validates the current file handle, asks the FSAL for the link target, checks response room, and frees target storage through the operation free hook.

## Important APIs, Types, and Functions
- `nfs4_op_readlink` handles `NFS4_OP_READLINK`.
- `fsal_readlink` fills the result `utf8string`.
- `check_resp_room` accounts for status, XDR string length, and payload.
- `nfs4_op_readlink_Free` releases `READLINK4resok.link.utf8string_val` on success.

## Control Flow
The operation sets `resp->resop`, validates CurrentFH as `SYMBOLIC_LINK`, calls `fsal_readlink(data->current_obj, link_buffer)`, converts FSAL errors, computes the rounded response size, and either records `data->op_resp_size` or frees the link target if response size cannot fit.

## State and Persistence Behavior
No persistent state changes occur. The only owned state is the FSAL-allocated link buffer stored in the response and released by `nfs4_op_readlink_Free`.

## Dependencies and Integration Points
Depends on filehandle sanity checking, FSAL symlink target retrieval, NFS error conversion, response room tracking, and LTTng tracepoints. It participates in compound processing through CurrentFH and response-size accounting.

## Risks
The main risk is ownership of `utf8string_val`: it must be freed on response-size failure and after successful XDR use, but not after FSAL errors that did not allocate it. Long symlink targets must be rounded correctly for response-size checks.

## Test Signals
Test successful READLINK, non-symlink CurrentFH, stale/no filehandle errors, FSAL readlink failures, response-room overflow with long targets, and memory cleanup on both success and overflow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_readlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_reclaim_complete.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_reclaim_complete.c

## Purpose
Implements NFSv4.1 `RECLAIM_COMPLETE`, letting a session client signal that reboot reclaim for the client is complete. It updates client recovery flags and notifies the state layer.

## Important APIs, Types, and Functions
- `nfs4_op_reclaim_complete` handles the operation.
- Uses `data->session->clientid_record` and its `cid_cb.v41.cid_reclaim_complete` flag.
- Calls `nfs41_reclaim_complete_clid` and increments global `reclaim_completes` when reclaim was allowed.
- `nfs4_op_reclaim_complete_Free` is a no-op.

## Control Flow
The handler sets `resp->resop` and initializes success. If the request is for all filesystems and the client already completed reclaim, it returns `NFS4ERR_COMPLETE_ALREADY`. If `rca_one_fs` is false, it marks the client complete, increments the reclaim-complete counter when applicable, and calls the SAL recovery completion helper. One-filesystem completion is accepted but currently does not update per-filesystem state.

## State and Persistence Behavior
Mutates in-memory client recovery state. It may affect server-wide recovery progress via `reclaim_completes` and the SAL reclaim-complete callback. It does not write persistent recovery records directly in this file.

## Dependencies and Integration Points
Requires an established NFSv4.1 session in `compound_data_t`. Integrates with SAL client/recovery structures and LTTng tracepoints.

## Risks
The implementation explicitly does not handle `rca_one_fs` beyond accepting it, so per-filesystem recovery semantics may be incomplete. Duplicate all-filesystem completion must return `COMPLETE_ALREADY` without re-notifying recovery state.

## Test Signals
Test first all-filesystem completion, duplicate completion, `rca_one_fs` behavior, clients with and without `cid_allow_reclaim`, and behavior when invoked in a valid v4.1 session after server grace/recovery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_reclaim_complete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_release_lockowner.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_release_lockowner.c

## Purpose
Implements NFSv4.0 `RELEASE_LOCKOWNER`. It validates the clientid, reserves or expires the lease, resolves the lock owner, releases it if present, and updates the client lease.

## Important APIs, Types, and Functions
- `nfs4_op_release_lockowner` handles the operation.
- Uses `nfs_client_id_get_confirmed`, `reserve_lease_or_expire`, `convert_nfs4_lock_owner`, `create_nfs4_owner`, `release_lock_owner`, `update_lease_simple`, and reference release helpers.
- `nfs4_op_release_lockowner_Free` is a no-op.

## Control Flow
The handler rejects minorversion greater than 0 with `NFS4ERR_NOTSUPP`, looks up a confirmed clientid, reserves the lease, converts the wire lock owner to a SAL owner name, looks up or creates the owner in lookup-only semantics, releases it when found, drops owner/client refs, updates the lease, and returns converted status.

## State and Persistence Behavior
Mutates in-memory lock-owner state by releasing an owner and may expire a client lease if stale. It updates the client's lease time on normal completion. It does not alter filesystem data.

## Dependencies and Integration Points
Depends on NFSv4.0 clientid and lease management, SAL owner lookup/refcounting, and lock-owner release semantics. This op is intentionally not available in v4.1 because sessions replace its use.

## Risks
Owner lookup behavior is subtle: unknown lock owners are treated as success. Lease reservation must be balanced with reference releases. `create_nfs4_owner` is used as a find/create API with flags that need to preserve protocol semantics.

## Test Signals
Test v4.1 rejection, stale/unknown/expired clientids, unknown lock owner success, lock owner with outstanding locks, release success, lease update, and concurrent release against lock-owner deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_release_lockowner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_remove.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_remove.c

## Purpose
Implements NFSv4 REMOVE for unlinking a named child from the current directory and returning directory change info.

## Important APIs, Types, and Functions
- `nfs4_op_remove` handles `NFS4_OP_REMOVE`.
- Uses `nfs4_sanity_check_FH`, `nfs4_utf8string_scan`, `nfs_get_grace_status`, `fsal_remove`, `fsal_get_changeid4`, and FSAL attr preparation/release.
- `nfs4_op_remove_Free` is a no-op.

## Control Flow
The operation prepares parent pre/post change attribute lists, validates CurrentFH as a directory, validates the target as a path component, rejects during grace with `NFS4ERR_GRACE`, captures initial parent change, calls `fsal_remove`, and fills `cinfo.before`, `cinfo.after`, and `cinfo.atomic` from FSAL-returned attrs when available or live changeid fallback otherwise. It releases attr lists and the grace reservation on the path that acquired it.

## State and Persistence Behavior
Mutates filesystem namespace by removing a child. Also returns change info describing the parent directory before/after mutation. It does not mutate compound CurrentFH.

## Dependencies and Integration Points
Depends on FSAL namespace mutation, NFS grace-state gating, UTF-8 path-component validation, NFS status conversion, and tracing.

## Risks
Grace handling must call `nfs_put_grace_status` only after a successful `nfs_get_grace_status`. Change-info atomicity depends on whether the FSAL supplied both pre and post `ATTR_CHANGE`. UTF-8 validation must reject empty or path-like names.

## Test Signals
Test removing regular files and empty directories, non-directory CurrentFH, invalid names, removal during grace, FSAL errors such as NOENT/NOTEMPTY/ACCESS, and change-info atomic true/false cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_remove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_rename.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_rename.c

## Purpose
Implements NFSv4 RENAME from SavedFH directory/oldname to CurrentFH directory/newname, enforcing same-export behavior and returning source and target directory change info.

## Important APIs, Types, and Functions
- `nfs4_op_rename` handles `NFS4_OP_RENAME`.
- Uses `nfs4_utf8string_scan`, `nfs4_sanity_check_FH`, `nfs4_sanity_check_saved_FH`, `nfs_get_grace_status`, `fsal_rename`, `fsal_get_changeid4`, and FSAL attr helpers.
- `nfs4_op_rename_Free` is a no-op.

## Control Flow
The handler validates both names as path components, verifies CurrentFH and SavedFH are directories, rejects cross-export renames with `NFS4ERR_XDEV`, gates mutation during grace, initializes source/target `before` change values, calls `fsal_rename`, then fills `source_cinfo` and `target_cinfo` from FSAL pre/post attrs or fallback changeids and sets atomic flags according to attr availability.

## State and Persistence Behavior
Mutates filesystem namespace across two directories. Reads SavedFH and CurrentFH but does not replace either handle. Returns cinfo for both old and new parent directories.

## Dependencies and Integration Points
Depends on SAVEFH/RESTOREFH-established saved directory state, FSAL rename semantics, export identity, grace management, and status conversion.

## Risks
The code computes post-change info even after `fsal_rename` returns an error because it does not branch before cinfo fill; callers must rely on status, but tests should ensure error responses do not expose misleading ok payloads. Same-export checks use export ids, not FSAL filesystem identity. Grace release must be balanced.

## Test Signals
Test same-directory and cross-directory rename, cross-export `XDEV`, invalid names, missing SavedFH, non-directory handles, grace rejection, FSAL failures, overwrites, and cinfo atomic combinations for one or both directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_renew.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_renew.c

## Purpose
Implements NFSv4.0 RENEW to refresh a client's lease and report callback-path problems when delegations are active.

## Important APIs, Types, and Functions
- `nfs4_op_renew` handles `NFS4_OP_RENEW`.
- Uses `nfs_client_id_get_confirmed`, `reserve_lease_or_expire`, `get_cb_chan_down`, `dec_client_id_ref`, and delegation/callback fields on `nfs_client_id_t`.
- `nfs4_op_renew_Free` is a no-op.

## Control Flow
The handler zeroes the response, rejects minorversion greater than 0, resolves the confirmed clientid, reserves or expires the lease, and if delegations are enabled and callback path is down while delegations exist, returns `NFS4ERR_CB_PATH_DOWN` and records the first response time. Otherwise it returns OK and resets the path-down response timestamp.

## State and Persistence Behavior
Updates the client lease through `reserve_lease_or_expire` and may mutate `first_path_down_resp_time`. No filesystem data changes occur.

## Dependencies and Integration Points
Tightly integrated with NFSv4.0 clientid lease lifecycle, callback channel tracking, delegation state, and server stats/logging. NFSv4.1+ clients use SEQUENCE rather than RENEW.

## Risks
The source comments note callback-channel state may not be obviously thread-safe. The operation must distinguish unknown clientid, expired lease, callback-down-with-delegations, and normal renewal correctly.

## Test Signals
Test v4.1 rejection, valid renew, stale clientid, expired lease, callback path down with and without current delegation grants, timestamp initialization/reset, and repeated renew calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_renew.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_restorefh.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_restorefh.c

## Purpose
Implements NFSv4 RESTOREFH. It replaces CurrentFH and current compound context with the filehandle, object, export, pNFS DS, file type, and stateid snapshot saved by SAVEFH.

## Important APIs, Types, and Functions
- `nfs4_op_restorefh` handles `NFS4_OP_RESTOREFH`.
- Uses `nfs4_Is_Fh_Empty`, `nfs4_sanity_check_saved_FH`, `export_ready`, `get_gsh_export_ref`, `set_op_context_export`, `set_current_entry`, and `pnfs_ds_get_ref`.
- `nfs4_op_restorefh_Free` is a no-op.

## Control Flow
The handler clears the response, checks that SavedFH exists, sanity-checks the saved filehandle, takes a new export reference if the saved export is still ready, copies saved FH bytes into CurrentFH, restores export permissions and pNFS DS context, points the current entry at `saved_obj`, restores saved stateid validity/value, and handles DS-handle current fields.

## State and Persistence Behavior
Mutates only compound/request context. It changes CurrentFH, current object reference, current export context, pNFS DS reference, file type, and current stateid. It does not alter persistent filesystem or client state.

## Dependencies and Integration Points
Depends on SAVEFH creating a coherent snapshot. It integrates with export refcounting, op context export management, pNFS data-server refs, filehandle helpers, and compound stateid tracking.

## Risks
RESTOREFH assumes saved export/object lifetimes are valid and refcounted. If saved export is no longer ready, it returns stale. DS-handle handling only updates `current_ds` fields when `data->current_ds != NULL`, so mixed DS/non-DS restore paths need coverage.

## Test Signals
Test missing SavedFH, stale saved export, normal save/restore around LOOKUP or PUTFH, saved stateid restoration, pNFS DS restore, export permission restoration, and object reference balance under repeated SAVEFH/RESTOREFH.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_restorefh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_savefh.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_savefh.c

## Purpose
Implements NFSv4 SAVEFH and helper `set_saved_entry`. It snapshots CurrentFH-related object, export, pNFS DS, file type, permissions, and current stateid for later RESTOREFH or operations that use SavedFH.

## Important APIs, Types, and Functions
- `set_saved_entry` manages saved object replacement and old saved object/DS release.
- `nfs4_op_savefh` handles `NFS4_OP_SAVEFH`.
- Uses `nfs4_sanity_check_FH`, `nfs4_AllocateFH`, `export_ready`, `get_gsh_export_ref`, `put_gsh_export`, `pnfs_ds_get_ref`, `pnfs_ds_put`, `save_op_context_export_and_set_export`, and `restore_op_context_export`.
- `nfs4_op_savefh_Free` is a no-op.

## Control Flow
SAVEFH validates CurrentFH, allocates SavedFH storage if necessary, checks/export-refs the current export, copies FH bytes, updates saved object through `set_saved_entry` when different, saves current stateid validity and value, drops old saved export and pNFS DS refs, then stores current export permissions and pNFS DS refs. `set_saved_entry` temporarily switches op context to the saved export when releasing a previous saved object/DS, clears saved stateid validity, releases old resources, refs the new object, and records file type.

## State and Persistence Behavior
Mutates compound saved state only. It manages references on saved object, export, pNFS DS, and DS handle. It preserves a saved stateid snapshot for restore and later SavedFH-based operations.

## Dependencies and Integration Points
Tightly paired with RESTOREFH and operations such as RENAME that consume SavedFH. Relies on export readiness/refcounting, FSAL object refs, pNFS DS lifetimes, and op-context switching for correct release semantics.

## Risks
Reference ordering is the major risk: old saved export/DS/object must be released after new refs are acquired or while the right op context is active. Saved DS handles are not separately refcounted in the same way as pNFS DS objects, so equality checks matter.

## Test Signals
Test repeated SAVEFH on same object and different objects, saving after PUTFH/LOOKUP across exports, pNFS DS handle saving, subsequent RESTOREFH, SavedFH use by RENAME, stale export handling, and leak/refcount checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_savefh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_secinfo.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_secinfo.c

## Purpose
Implements NFSv4 SECINFO for a named child of the current directory. It resolves the target, crosses junctions when needed, checks export access, builds the ordered security flavor list, and clears CurrentFH for minorversion greater than 0.

## Important APIs, Types, and Functions
- `nfs4_op_secinfo` handles `NFS4_OP_SECINFO`.
- Uses `nfs4_utf8string_scan`, `nfs4_sanity_check_FH`, `fsal_lookup`, `export_ready`, `save_op_context_export_and_set_export`, `nfs4_export_check_access`, `nfs_export_get_root_entry`, `check_resp_room`, and `set_current_entry`.
- Builds `secinfo4` entries for RPCSEC_GSS privacy/integrity/none when GSS is compiled, plus AUTH_UNIX and AUTH_NONE from export permissions.
- `nfs4_op_secinfo_Free` frees the allocated `SECINFO4resok_val`.

## Control Flow
The handler validates the name and CurrentFH directory, looks up the child object, checks for a directory junction under `jct_lock`, refs the junction export when ready, and if crossing a junction saves/restores op context while running export access checks and replacing the child object with the junction export root. ACCESS hides the export as NOENT, while WRONGSEC is expected and still allows reporting security info. It counts enabled security entries, checks response room, allocates the result array, fills flavors in preferred order, and for v4.1+ clears CurrentFH and export context as required by SECINFO semantics.

## State and Persistence Behavior
No persistent state changes occur. It temporarily mutates op context during junction traversal and may clear CurrentFH/current export for minorversion greater than 0. It owns and frees the result flavor array.

## Dependencies and Integration Points
Depends on export permissions, GSS compile-time support, FSAL lookup/root-entry access, pseudo/junction metadata, request credential rebuilding, response sizing, and current filehandle management.

## Risks
Junction traversal must not leak export references or leave altered credentials. ACCESS is intentionally converted to NOENT for hidden exports. Response-size estimation must include GSS OID payloads. v4.1+ CurrentFH clearing is protocol-visible and can affect following compound ops.

## Test Signals
Test normal child SECINFO, invalid name, non-directory CurrentFH, missing child, junction to allowed export, junction ACCESS hidden as NOENT, WRONGSEC export, GSS and non-GSS builds, response overflow, v4.0 CurrentFH retention, and v4.1 CurrentFH clearing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_secinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_secinfo_no_name.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_secinfo_no_name.c

## Purpose
Implements NFSv4.1 SECINFO_NO_NAME for the current object or its parent, returning security flavors from the active export permissions and clearing CurrentFH.

## Important APIs, Types, and Functions
- `nfs4_op_secinfo_no_name` handles `NFS4_OP_SECINFO_NO_NAME`.
- Uses `nfs4_sanity_check_FH`, optional `nfs4_op_lookupp` for `SECINFO_STYLE4_PARENT`, `check_resp_room`, `set_current_entry`, and `clear_op_context_export`.
- Builds `secinfo4` arrays using the same flavor ordering as SECINFO.
- `nfs4_op_secinfo_no_name_Free` frees allocated results on success.

## Control Flow
The operation validates that a CurrentFH exists, optionally invokes LOOKUPP to replace CurrentFH with the parent, counts enabled GSS/AUTH entries from `op_ctx->export_perms`, checks response room, allocates and fills the result array, clears CurrentFH and current export context, sets `resp->resop`, and returns status.

## State and Persistence Behavior
No persistent filesystem state changes occur. The operation intentionally clears CurrentFH and releases current export context after successful result construction. Parent style may mutate CurrentFH before flavor collection through LOOKUPP.

## Dependencies and Integration Points
Depends on LOOKUPP semantics, export permission bits, GSS build options, response room tracking, and compound filehandle state management.

## Risks
Because it delegates parent-style lookup to `nfs4_op_lookupp` using the same response union location, `resp->resop` must be reset on error. Clearing CurrentFH is required but can surprise following compound operations if applied on the wrong status path.

## Test Signals
Test current and parent styles, missing CurrentFH, LOOKUPP failure at pseudo root or inaccessible parent, flavor list ordering, GSS and AUTH combinations, response overflow, CurrentFH clearing, and result free behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_secinfo_no_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_sequence.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_sequence.c

## Purpose
Implements NFSv4.1 SEQUENCE, which establishes session/slot context for a compound, enforces exactly-once sequencing, handles replay cache lookup, reserves the client lease, returns session status flags, and serializes slot use.

## Important APIs, Types, and Functions
- `nfs4_op_sequence` handles `NFS4_OP_SEQUENCE`.
- `check_replay_request` compares the current compound opcode list against the slot's last request for diagnostics when a repeated sequence id is not an actual replay.
- Uses `nfs41_Session_Get_Pointer`, `reserve_lease_or_expire`, `release_nfs4_res_compound`, `release_slot`, `check_resp_room`, `check_session_conn`, `has_revoked_delegations_for_client`, and session/client refcount helpers.
- `nfs4_op_sequence_Free` is a no-op.

## Control Flow
SEQUENCE rejects v4.0, resolves the session, reserves the client lease, preserves a clientid ref in compound data, validates slot id, locks the slot, checks whether the request sequence id is the next expected value, a replay of the previous value, or misordered. For cached replay, it replaces the current compound result with the cached result and returns `NFS_REQ_REPLAY`. For uncached replay it returns `NFS4ERR_RETRY_UNCACHED_REP`; for other mismatches, `NFS4ERR_SEQ_MISORDERED`.

On a new valid request, it records session/sequence/slot in compound data, increments the slot sequence, releases any previous slot cache, fills `SEQUENCE4resok`, sets callback-path and revoked-delegation flags, records `sa_cachethis`, sets `op_ctx->clientid`, verifies response room, checks session connection binding, and deliberately keeps the slot lock held for the rest of compound execution.

## State and Persistence Behavior
Mutates in-memory session slot sequence and cached-result state, preserves client/session refs in compound data, updates the lease reservation, and may clear `session->has_revoked_delegations` after verification. It controls duplicate request cache behavior for the whole compound.

## Dependencies and Integration Points
Integrated with the NFSv4.1 session table, DRC/cached result lifecycle, compound response allocator, client lease management, callback channel state, revoked delegation tracking, and connection binding checks.

## Risks
Slot lock ownership crosses function boundaries; the compound engine must release it after completing/caching the result. Replay response replacement must correctly manage result refs. Misidentifying replay vs misordered requests can cause client hangs. Response-room checks happen after session establishment because max response sizing depends on session attrs.

## Test Signals
Test v4.0 invalid, bad session, expired client, bad slot, next sequence success, cached replay, uncached replay, misordered sequence, opcode mismatch diagnostics, callback path down flag, revoked delegation flag set/cleared, cachethis behavior, and slot lock/release under concurrent compounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_sequence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_set_ssv.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_set_ssv.c

## Purpose
Provides a minimal NFSv4.1 SET_SSV handler. It validates protocol minorversion and otherwise returns success without implementing secret state verifier updates.

## Important APIs, Types, and Functions
- `nfs4_op_set_ssv` handles `NFS4_OP_SET_SSV`.
- `nfs4_op_set_ssv_Free` is a no-op.

## Control Flow
The handler sets `resp->resop`, initializes status to OK, rejects minorversion 0 with `NFS4ERR_INVAL`, and returns the status converted to a request result. The request argument is explicitly marked unused.

## State and Persistence Behavior
No state is mutated. The operation is effectively a stub for NFSv4.1+.

## Dependencies and Integration Points
Only depends on basic NFS operation structures and minorversion in compound data. It does not integrate with session cryptographic state.

## Risks
Clients that require real SSV behavior will observe a success response without actual state changes. This is a protocol-compliance risk if the server advertises capabilities implying SET_SSV semantics.

## Test Signals
Test v4.0 invalid response, v4.1/v4.2 success, no allocations, and no side effects in session/client records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_set_ssv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setattr.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setattr.c

## Purpose
Implements NFSv4 SETATTR, converting requested NFS attributes to FSAL attributes, enforcing writeability/support/stateid rules, gating mutations during grace, and applying the attributes through `fsal_setattr`.

## Important APIs, Types, and Functions
- `nfs4_op_setattr` handles `NFS4_OP_SETATTR`.
- Uses `nfs4_sanity_check_FH`, `nfs_get_grace_status`, `nfs4_Fattr_Check_Access`, `nfs4_Fattr_Supported`, `nfs4_Fattr_To_FSAL_attr`, `nfs4_Check_Stateid`, `squash_setattr`, `fsal_setattr`, and FSAL attr release.
- `nfs4_op_setattr_Free` is a no-op.

## Control Flow
The handler validates CurrentFH, rejects during grace, checks that requested attrs are writable and supported, converts them to an FSAL attrlist, and when size or space reservation is being set, rejects directories/non-regular files, validates the stateid, resolves open state from share/lock/delegation state, and requires write open access when an open state applies. It validates nanosecond ranges, squashes owner/group changes for squashed credentials, calls `fsal_setattr`, releases attrs, and returns the original attrmask in `attrsset` on success.

## State and Persistence Behavior
Mutates filesystem metadata and possibly file size through the FSAL. It only mutates NFS state by taking and releasing state refs during validation. Owner/group attributes may be transformed by credential squashing before persistence.

## Dependencies and Integration Points
Depends on NFS attribute conversion helpers, FSAL metadata mutation, SAL state validation, grace-state management, credential squashing, and CurrentFH object/filetype tracking.

## Risks
The function calls `nfs_put_grace_status` at the common `done` label even for failures before a successful grace reservation in some paths; this relies on grace helper semantics and deserves regression coverage. Size changes require correct open-mode enforcement across share, lock, delegation, and special stateids. Attribute conversion may allocate nested structures that must be released on every path after conversion.

## Test Signals
Test unsupported attrs, read-only attrs, invalid time nanoseconds, owner/group squashing, size truncate with read-only open, size on directory/non-file, special stateids, lock/delegation stateids, grace rejection, FSAL errors, ACL release, and `attrsset` echo on success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setclientid.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setclientid.c

## Purpose
Implements NFSv4.0 SETCLIENTID, creating or replacing unconfirmed clientid records according to RFC client identity cases, validating credential conflicts, and returning a short clientid plus confirm verifier.

## Important APIs, Types, and Functions
- `nfs4_op_setclientid` handles `NFS4_OP_SETCLIENTID`.
- Uses `get_client_record`, `nfs_compare_clientcred`, `clientid_has_state`, `new_clientid`, `new_clientid_verifier`, `remove_unconfirmed_client_id`, `create_client_id`, `nfs_set_client_location`, `nfs_client_id_insert`, and display/logging helpers.
- `nfs4_op_setclientid_Free` frees `client_using.r_addr` for `NFS4ERR_CLID_INUSE`.

## Control Flow
The handler rejects minorversion greater than 0, gathers local/remote RPC addresses for recovery backends, obtains a stable client record for the long-form client id, locks it, inspects the confirmed record, and follows RFC cases: principal mismatch with live state returns `CLID_INUSE`; matching confirmed verifier updates callback info using the same clientid and new verifier; verifier mismatch or absent confirmed record creates a new clientid/verifier. It removes any prior unconfirmed record, creates a new unconfirmed clientid, validates and copies callback address/program/ident, inserts it into clientid tables, and returns the clientid plus setclientid_confirm verifier.

## State and Persistence Behavior
Mutates in-memory client record tables by replacing unconfirmed records and possibly allocating new clientid records. It stores callback location and incoming/confirm verifiers. Persistent recovery effects are indirect through client manager APIs, not explicit file I/O here.

## Dependencies and Integration Points
Depends on client manager, credential comparison, RPC transport address helpers, callback location parsing, clientid hashing/insertion, and v4.0-only protocol flow. SETCLIENTID_CONFIRM consumes the unconfirmed record built here.

## Risks
The RFC case matrix is sensitive to principal matching, live state, verifier equality, and race handling with confirm/reaper threads. Callback `r_addr` length validation must free the partially built record on error. `CLID_INUSE` response allocates an address string that must be freed only on that status.

## Test Signals
Test new client, repeated same verifier update, verifier replacement, principal mismatch with and without live state, existing unconfirmed replacement, callback address too long, insert conflict, minorversion rejection, `CLID_INUSE` payload/free, and concurrent SETCLIENTID/CONFIRM races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setclientid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setclientid_confirm.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setclientid_confirm.c

## Purpose
Implements NFSv4.0 SETCLIENTID_CONFIRM, promoting an unconfirmed clientid to confirmed state or updating an existing confirmed record after SETCLIENTID, with race handling, credential checks, callback testing, and old-client expiration.

## Important APIs, Types, and Functions
- `nfs4_op_setclientid_confirm` handles `NFS4_OP_SETCLIENTID_CONFIRM`.
- Uses `nfs_client_id_get_unconfirmed`, `nfs_client_id_get_confirmed`, `nfs_compare_clientcred`, `nfs_client_id_expire`, `remove_unconfirmed_client_id`, `nfs_client_id_confirm`, `nfs4_chk_clid`, `nfs_test_cb_chan`, `set_cb_chan_down`, and refcount helpers.
- `nfs4_op_setclientid_confirm_Free` is a no-op.

## Control Flow
The handler rejects minorversion greater than 0, first tries to find an unconfirmed clientid and otherwise a confirmed clientid, refs the client record, and locks it. For unconfirmed records it verifies principal/client address, treats already-confirmed matching records as successful races, and stale non-unconfirmed records as stale. For confirmed records it validates principal and verifier for idempotent retry or returns `CLID_INUSE`.

For a matching unconfirmed record, it fetches any current confirmed record. If the existing confirmed record has a different clientid, it expires it. If the same clientid is already confirmed, it updates callback fields and verifier from the unconfirmed record, removes the unconfirmed entry, refreshes the lease, and tests callback channel. Otherwise it confirms the new record, checks reclaim eligibility, tests callback channel, and returns OK.

## State and Persistence Behavior
Mutates clientid confirmation state, callback channel state, lease timestamps, expired-client lists, and potentially expires old client state. It removes unconfirmed records and may trigger recovery eligibility checks.

## Dependencies and Integration Points
Tightly coupled with SETCLIENTID, client manager tables, callback RPC channel creation/testing, NFSv4 recovery/reclaim code, credential matching, and delayed cleanup lists.

## Risks
Concurrency is the core risk: records may be confirmed or expired while this handler runs, so refcounts and record mutex ordering are critical. Principal mismatches must avoid hijacking live client state. Callback testing can mark channels down immediately after confirmation, influencing delegation behavior.

## Test Signals
Test confirming a new client, retrying confirm with same verifier, wrong verifier, confirmed-record retry, principal mismatch, stale clientid, old confirmed client expiration, update of same confirmed client callback data, callback up/down transitions, reclaim eligibility, and concurrent duplicate confirms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setclientid_confirm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_test_stateid.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_test_stateid.c

## Purpose
Implements NFSv4.1 TEST_STATEID, returning per-stateid validation status codes without failing the whole operation for individual invalid stateids.

## Important APIs, Types, and Functions
- `nfs4_op_test_stateid` handles `NFS4_OP_TEST_STATEID`.
- Uses `nfs4_Check_Stateid` with `STATEID_NO_SPECIAL`.
- Allocates `tsr_status_codes_val` with `gsh_calloc`.
- `nfs4_op_test_stateid_Free` frees the status-code array on success.

## Control Flow
The handler rejects minorversion 0, allocates an array sized to the number of input stateids, loops over each stateid, validates it without an object and without special stateids, releases any returned state ref, stores the returned `nfsstat4` in the output array, sets output length, and returns top-level OK.

## State and Persistence Behavior
Does not mutate persistent state. It temporarily obtains and releases state references during validation.

## Dependencies and Integration Points
Depends on SAL stateid lookup/validation and compound minorversion. It gives clients a batch state-validity probe for sessions.

## Risks
Input count directly drives allocation; very large requests rely on upstream XDR/request limits. Special stateids are intentionally not accepted. Free hook must run only when top-level status is OK and allocation occurred.

## Test Signals
Test v4.0 invalid, empty stateid list, valid open/lock/delegation stateids, stale/revoked/bad stateids, special all-zero/all-one stateids rejected, mixed result arrays, and cleanup of allocated status arrays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_test_stateid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_verify.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_verify.c

## Purpose
Implements NFSv4 VERIFY, comparing supplied attributes against the current object's attributes and returning OK, NOT_SAME, INVAL, or ATTRNOTSUPP.

## Important APIs, Types, and Functions
- `nfs4_op_verify` handles `NFS4_OP_VERIFY`.
- Uses `nfs4_sanity_check_FH`, `nfs4_Fattr_Check_Access`, `nfs4_Fattr_Supported`, `bitmap4_to_attrmask_t`, `file_To_Fattr`, `nfs4_Fattr_cmp`, `nfs4_Fattr_Free`, and FSAL attr helpers.
- `nfs4_op_verify_Free` is a no-op.

## Control Flow
The handler validates CurrentFH, checks requested attrs are readable and supported, converts the requested bitmap to an FSAL request mask, obtains current attributes into a generated `fattr4`, compares supplied and actual attrs, maps compare result `1` to OK, `-1` to INVAL, and all other mismatch to NOT_SAME, then frees generated fattr memory.

## State and Persistence Behavior
No state is changed. It reads object attributes and allocates temporary attribute structures.

## Dependencies and Integration Points
Depends on NFS attribute conversion/comparison and FSAL attribute retrieval through `file_To_Fattr`. It is part of compound conditional workflows that may gate later operations.

## Risks
Early returns after `fsal_prepare_attrs` but before `fsal_release_attrs` can leak attr resources if conversion or `file_To_Fattr` fails after allocation. Attribute comparison semantics must stay aligned with NFS VERIFY/NVERIFY protocol behavior.

## Test Signals
Test exact match, mismatch, unsupported attr, unreadable attr, invalid attr encoding, missing CurrentFH, attributes requiring allocated fattr memory, and cleanup under conversion/retrieval failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_write.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_write.c

## Purpose
Implements NFSv4 WRITE, pNFS data-server WRITE, unsupported WRITE_SAME, and QoS write callbacks. It validates filehandle/state/access/quota/limits, dispatches async FSAL writes, completes stable-write metadata and verifier fields, and records write statistics.

## Important APIs, Types, and Functions
- `struct nfs4_write_data` is the async continuation for writes.
- `nfs4_op_write`, `nfs4_op_write_resume`, `op_dswrite`, `nfs4_complete_write`, and `nfs4_write_cb` are the core write path.
- Uses `nfs4_Check_Stateid`, `state_deleg_conflict`, `check_quota`, `obj_ops->test_access`, `obj_ops->write2`, `get_write_verifier`, `server_stats_io_done`, QoS `qos_process`, and pNFS DS `dsh_write`.
- `nfs4_op_write_same` returns `NFS4ERR_NOTSUPP`.

## Control Flow
The handler traces and sets response op, routes v4.1+ DS handles to `op_dswrite`, checks CurrentFH regular-file sanity, checks quota, validates the input stateid, resolves share/lock/delegation state, enforces write open access or delegation write type, checks delegation conflicts for special stateids, tests FSAL write access, enforces `MaxOffsetWrite` and clamps `MaxWrite`, handles zero-length writes by returning FILE_SYNC and a write verifier, optionally sets v4.0 owner clientid, allocates `nfs4_write_data`, fills `fsal_io_arg`, runs QoS if enabled, and calls `write2`.

Async completion converts FSAL status, sets done flags, and resumes the request if needed. Completion sets committed mode based on `fsal_stable`, count from `io_amount`, write verifier from the export, stats, and releases owner/state refs. Resume handles QoS continuation, FSAL resume requests, completion, and freeing `data->op_data`.

## State and Persistence Behavior
Writes mutate file contents through FSAL or DS operations and may require stable storage depending on requested stability or export `EXPORT_OPTION_COMMIT`. The operation temporarily holds NFS state and owner refs across async execution and updates stats. It does not directly persist client state.

## Dependencies and Integration Points
Depends on FSAL object write APIs, pNFS DS write ops, SAL state/delegation logic, quota checks, export write limits and commit policy, QoS throttling, write-verifier generation, and compound async resume machinery.

## Risks
The expression `(offset + size) > MaxOffsetWrite` can overflow if offset is near `UINT64_MAX`; tests should cover boundary behavior. Async/QoS paths must free `write_data` exactly once. Stable/unstable commit semantics depend on FSAL setting `fsal_stable`. DS write path asserts a single iovec. Zero-length writes must still return a valid verifier.

## Test Signals
Test normal writes, zero-length writes, quota failure, access failure, share/openmode errors, delegation write/non-write stateids, special stateid delegation conflicts, max write clamping, max offset/fbig, async callback-before/after-exit, FSAL resume, QoS delay/rate paths, pNFS DS writes, forced sync export option, and WRITE_SAME not supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_xattr.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_xattr.c

## Purpose
Implements NFSv4 extended attribute operations: GETXATTR, SETXATTR, LISTXATTR, and REMOVEXATTR. It gates on FSAL xattr support, handles xattr value/list memory, performs response-size checks, and returns change info for mutating operations.

## Important APIs, Types, and Functions
- `nfs4_op_getxattr`, `nfs4_op_setxattr`, `nfs4_op_listxattr`, and `nfs4_op_removexattr` are the handlers.
- Uses FSAL object ops `getxattrs`, `setxattrs`, `listxattrs`, and `removexattrs`.
- Checks `ATTR4_XATTR` through `fs_supported_attrs`.
- Uses `nfs_get_grace_status`, `fsal_get_changeid4`, `check_resp_room`, and status conversion helpers.
- Free hooks release GETXATTR value strings and LISTXATTR name arrays.

## Control Flow
GETXATTR validates CurrentFH, checks xattr support, tries a 1024-byte value buffer, handles `ERR_FSAL_XATTR2BIG` by querying required size with a null buffer and retrying, checks response room, and transfers the value to the response. SETXATTR validates support and grace state, fills non-atomic before change info, calls `setxattrs`, sets after change on success, and releases grace. LISTXATTR validates support, enforces minimum `lxa_maxcount`, subtracts XDR overhead to compute the FSAL name budget, calls `listxattrs`, computes exact response size, and transfers the FSAL-allocated list. REMOVEXATTR mirrors SETXATTR using `removexattrs`.

## State and Persistence Behavior
SETXATTR and REMOVEXATTR mutate filesystem xattrs and return change info with `atomic = false`. GETXATTR and LISTXATTR allocate response memory. No NFS client/session state is changed.

## Dependencies and Integration Points
Depends on FSAL xattr capability and object xattr ops, NFSv4 xattr XDR types, grace-state gating for mutation, response room checks, and FSAL changeid retrieval.

## Risks
LISTXATTR performs the same sanity check twice, likely harmless but noisy. Mutating xattr ops call `nfs_put_grace_status` only after successful grace acquisition, but early error paths must stay balanced. GETXATTR's two-step size query depends on FSAL convention for `ERR_FSAL_XATTR2BIG`. Response-size overflow or allocation failure handling is sparse.

## Test Signals
Test unsupported xattrs, GETXATTR small/large/missing values, LISTXATTR too-small maxcount, paginated LISTXATTR cookies and EOF, response-room overflow cleanup, SETXATTR create/replace modes, REMOVEXATTR missing names, grace rejection, change-info before/after behavior, and free hooks under partial allocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_pseudo.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_pseudo.c

## Purpose
Manages the NFSv4 pseudo filesystem export tree. It mounts exports at pseudopath junctions, creates intermediate pseudo directories, unmounts exports and cleans unused pseudo nodes, and prunes/remounts subtrees during export configuration updates.

## Important APIs, Types, and Functions
- `struct pseudofs_state` carries the export being mounted, current pseudo object, and refcounted pseudopath/fullpath strings.
- `is_export_pseudo` detects PSEUDO and MDCACHE-on-PSEUDO exports.
- `cleanup_pseudofs_node` recursively removes empty pseudo directories after unmount.
- `make_pseudofs_node` looks up or creates a pseudo directory path component.
- `pseudo_mount_export` builds a mount path, records junction object/parent export, and sets `junction_export`.
- `create_pseudofs` processes the export mount work queue under a root op context.
- `pseudo_unmount_export`, `pseudo_unmount_export_tree`, and `prune_pseudofs_subtree` detach exports and descendants.

## Control Flow
Mounting skips non-v4 exports and the pseudo root, snapshots pseudopath/fullpath with RCU/refstrs, finds the parent export for the pseudopath prefix, gets the parent root object, walks remaining path components using `make_pseudofs_node`, then under export locks records mounted-on fileid, junction object refs, parent export refs, and parent mounted-export list membership. It sets `export->is_mounted` and only then writes `state_hdl->dir.junction_export` and `jct_pseudopath` under the junction lock, making the junction visible.

Unmounting locks the export, detaches junction metadata, clears export junction/parent fields, removes the mounted-export list node, clears `is_mounted`, initializes an op context for the parent export, either removes unused PSEUDO FS nodes recursively or calls the parent FSAL `unmount`, then releases export/object/refstr refs. Pruning walks descendants depth-first under export list locks, unmounts defunct or flagged subtrees, and queues eligible exports for remount.

## State and Persistence Behavior
Mutates in-memory export graph state (`exp_junction_obj`, `exp_parent_exp`, `mounted_exports_list`, `is_mounted`, `exp_mounted_on_file_id`, update flags) and pseudo FSAL namespace directories. It also mutates junction fields inside object state handles. It relies on the export admin mutex externally for update serialization.

## Dependencies and Integration Points
Depends on export manager work queues and lookups, FSAL lookup/create/remove/lookupp/unmount operations, object refs, export refs, RCU refstrs, op context initialization/release, PSEUDO and MDCACHE FSAL naming conventions, and junction traversal consumers such as LOOKUP/READDIR/SECINFO.

## Risks
Refcount and lock ordering are complex: export locks, parent export locks, junction locks, RCU refstr refs, object LRU/active/root refs, and op context export refs all interact. `cleanup_pseudofs_node` edits the path string in place and assumes it will not walk past pseudo root. `make_pseudofs_node` treats any PSEUDO lookup error as create-needed during updates. Junction visibility depends on setting `junction_export` last.

## Test Signals
Test mounting root and nested exports, creating missing pseudo directories, existing non-directory path component failure, non-PSEUDO parent create failure, export update prune/remount, unmount of leaf and subtree exports, cleanup of now-empty pseudo directories, mounted-on non-PSEUDO unmount callback, READDIR/LOOKUP junction visibility after mount, and refcount/leak checks across repeated reloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_pseudo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs_null.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs_null.c

## Purpose
Implements the NFS NULL procedure for all protocol versions. NULL is a liveness/no-op RPC that returns success without inspecting inputs.

## Important APIs, Types, and Functions
- `nfs_null` logs request processing and returns `NFS3_OK`.
- `nfs_null_free` is a no-op result cleanup hook.

## Control Flow
`nfs_null` ignores `arg`, `req`, and `res`, emits a debug log on `COMPONENT_NFSPROTO`, and returns success. The free hook does nothing.

## State and Persistence Behavior
No state is read or mutated beyond logging.

## Dependencies and Integration Points
Integrated as the NULL procedure entry point in the NFS RPC dispatch table. Includes common NFS headers for shared types, but does not call NFSv4-specific machinery.

## Risks
Minimal. The return value uses `NFS3_OK`, which is numerically appropriate for NULL success across versions but can be confusing to readers.

## Test Signals
Test that NULL succeeds for supported NFS program versions, ignores malformed/empty arguments, does not allocate response resources, and can be used as a cheap server liveness probe.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs_null.c -->
