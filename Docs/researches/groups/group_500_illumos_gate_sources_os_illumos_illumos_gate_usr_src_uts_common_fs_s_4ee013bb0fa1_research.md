# Group Research: group_500_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_4ee013bb0fa1

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_node.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_node.c

## Summary
Implements the SMB server's `smb_node_t` layer: a cached vnode wrapper with SMB-specific state for parent/stream relationships, open-handle lists, share checks, delete-on-close, change notify fanout, sticky timestamps, simulated allocation size, reparse/DFS flags, and system-file marking.

## Main Responsibilities
- Initializes and destroys the global SMB node kmem cache and hash table.
- Looks up or allocates nodes from vnode identity, share fsid, and file attributes.
- Maintains node references and the AVAILABLE/DESTROYING state machine.
- Tracks parent directory nodes and unnamed-stream backing nodes.
- Applies open/share/delete/rename conflict checks across open files.
- Manages delete-on-close credentials and final removal.
- Provides change notification subscription and event dispatch to open handles.
- Exposes node path, mount path, file type, reparse, system, and readonly helpers.
- Applies SMB timestamp and allocation-size semantics around filesystem setattr/getattr.

## Key APIs
- `smb_node_init()`, `smb_node_fini()`.
- `smb_node_lookup()`, `smb_stream_node_lookup()`.
- `smb_node_ref()`, `smb_node_release()`.
- `smb_node_set_delete_on_close()`, `smb_node_reset_delete_on_close()`, `smb_node_delete_on_close()`.
- `smb_node_open_check()`, `smb_node_rename_check()`, `smb_node_delete_check()`.
- `smb_node_fcn_subscribe()`, `smb_node_fcn_unsubscribe()`, `smb_node_notify_change()`, `smb_node_notify_modified()`.
- `smb_node_setattr()`, `smb_node_getattr()`.

## Important Behavior
`sm b_node_lookup()` uses `smb_vop_getattr()` with zone credentials, chooses the tree fsid for share-relative objects, searches a hash bucket by hash key and vnode pointer, and ignores nodes already in DESTROYING state. A new node takes its own vnode hold and optional holds on parent and unnamed-stream nodes.

Reference teardown moves a zero-ref node to DESTROYING before dropping `n_mutex`, preventing concurrent lookup from resurrecting a node while `smb_node_release()` removes it from the hash table.

Delete-on-close is stored on the node with the credential and case flags that will be used for final `smb_fsop_remove()` or `smb_fsop_rmdir()`. Directories are checked for emptiness before accepting delete-on-close. A delete-pending notify event is sent so change-notify waiters stop using the handle.

The file simulates Windows semantics not directly represented by illumos VFS. Allocation size persists only while opens exist. Special NT time values `-1` and `-2` pause or resume per-handle sticky timestamps; sticky values are returned through handle-based getattr and committed on close.

## State and Synchronization
Node lifetime is governed by the hash-bucket list lock plus `n_mutex`; the documented lock order is bucket lock before node mutex. `n_ofile_list` is protected separately and is used by share checks, notifications, and oplock/open-handle walkers. Share-reservation critical regions combine `n_lock` with `nbl_start_crit()`/`nbl_end_crit()`.

## Dependencies
Depends on SMB fsop/vop wrappers, FEM hooks, oplock state, named streams/xattr directories, reparse parsing, DFS reparse type detection, change notify, DOS attributes, and illumos vnode/pathname APIs.

## Risks
The node hash uses fsid and nodeid but final identity includes vnode pointer, so correctness depends on stable vnode identity for the lifetime of cached nodes.

`sm b_node_rename()` updates parent and on-disk name but explicitly notes that attributes may need updating.

The delete-on-close path can run filesystem remove/rmdir during final close/release, so failures are logged but cannot be surfaced cleanly to the original client operation.

Directory emptiness checking reads a single readdir buffer and treats malformed or partial records conservatively as non-empty.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_notify.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_notify.c

## Summary
Provides the common SMB1/SMB2 file change notification engine. It maintains per-open-directory notification buffers, records events even when no request is waiting, and implements a three-act async flow for long-lived notify requests.

## Main Responsibilities
- Validates notify requests against directory handles and `FILE_LIST_DIRECTORY`.
- Subscribes an ofile to node-level change events on first notify.
- Buffers `FILE_NOTIFY_INFORMATION` records per ofile.
- Parks notify requests without a worker thread and resumes them via taskq.
- Handles cancellation, close, delete-pending, subdirectory-change, and overflow events.
- Maps internal file actions to client completion filters.

## Key APIs
- `smb_notify_act1()`.
- `smb_notify_act2()`.
- `smb_notify_act3()`.
- `smb_notify_ofile()`.

## Important Behavior
`act1` validates parameters, subscribes the ofile if needed, and returns already buffered events immediately. If no events exist, it returns `NT_STATUS_PENDING`.

`act2` transitions the request from ACTIVE to WAITING_FCN1, clears `sr_worker`, installs `smb_notify_cancel()` as the cancel method, links the request into `nc_waiters`, and wakes it immediately if an event raced in.

`act3` runs after wakeup or cancel, restores the worker thread, removes the request from the waiter list, and consumes buffered events.

Notify buffers are destructive only when the last waiter consumes them. Multiple simultaneous waiters see the same pending events; the last waiter clears normal events while persistent close/delete indicators remain.

## Event Encoding
Normal actions append aligned `FILE_NOTIFY_INFORMATION` records to `nc_buffer`; the last entry's `NextEntryOffset` is patched to zero on consumption. Overflow, zero-length output, or too-small caller buffers result in `NT_STATUS_NOTIFY_ENUM_DIR`.

Internal actions such as delete pending and handle closed set event bits without appending response records.

## Dependencies
Used by SMB1 NT transact notify and SMB2 change notify finish paths. Relies on `smb_node_fcn_subscribe()`, taskq dispatch, request cancel states, mbuf-chain encoding/copying, and per-ofile mutex/list state.

## Risks
Recursive `WatchTree` support is represented as a subdirectory-change enum-dir signal, not true recursive monitoring. The source comments state recursive notify is optional and intentionally not implemented.

The notify buffer size is fixed on the first notify call for an ofile, matching Windows behavior but making later smaller buffers produce enum-dir fallback.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_notify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_cancel.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_cancel.c

## Summary
Implements SMB1 `SMB_COM_NT_CANCEL`, which cancels a pending request from the same session without sending a response to the cancel command itself.

## Main Responsibilities
- Emits DTrace start/done probes.
- Searches the session request list for matching UID, PID, TID, and MID.
- Calls `smb_request_cancel()` on matching requests other than the cancel request.
- Handles cancel immediately in the SMB1 reader path.

## Key APIs
- `smb_pre_nt_cancel()`.
- `smb_post_nt_cancel()`.
- `smb_com_nt_cancel()`.
- `smb1sr_newrq_cancel()`.

## Important Behavior
The command walks `session->s_req_list` under the session list lock and cancels every matching request except itself. It expects exactly one match and emits a DTrace error probe if the match count differs. It returns `SDRC_NO_REPLY`.

`sm b1sr_newrq_cancel()` bypasses normal taskq dispatch so cancellation can hurry blocked work as early as possible.

## Dependencies
Relies on request identity fields and common `smb_request_cancel()` semantics, including the documented race between cancellation and natural request completion.

## Risks
Cancellation is inherently racy. A zero or multiple match count is observable and traced but not otherwise recoverable, and no protocol reply is sent to clarify the outcome.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_cancel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_create_andx.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_create_andx.c

## Summary
Implements SMB1 `NT_CREATE_ANDX`, the main SMB1 open/create command for files, directories, pipes, and printers. It decodes protocol parameters into `open_param`, delegates the real work to `smb_common_open()`, optionally acquires SMB1 oplocks, and encodes normal or extended create responses.

## Main Responsibilities
- Decodes name, desired access, share access, allocation size, attributes, disposition, create options, impersonation, and security flags.
- Converts NT create flags into requested oplock level.
- Validates create options, disposition, delete-on-close access, and file-id opens.
- Handles root-directory-relative opens through an existing directory FID.
- Applies backup-intent credentials.
- Sets delete-on-close on successful disk/printer opens.
- Encodes standard or Windows-compatible extended responses.

## Key APIs
- `smb_pre_nt_create_andx()`.
- `smb_post_nt_create_andx()`.
- `smb_com_nt_create_andx()`.

## Important Behavior
`FILE_OPEN_BY_FILE_ID` is rejected as unsupported. `FILE_DELETE_ON_CLOSE` requires `DELETE` access. `FILE_FLAG_WRITE_THROUGH`, `FILE_FLAG_DELETE_ON_CLOSE`, and `FILE_FLAG_BACKUP_SEMANTICS` are translated into create options before the common open path.

If `RootDirectoryFid` is nonzero, the handler looks up that ofile and uses its node as the path root; `smb_post_nt_create_andx()` releases that directory ofile.

Extended responses deliberately encode 50 real words while reporting a fake word count of 42 to match Windows SMB1 behavior. The extended response includes `MaxAccess`, while the file-id field is left zero for compatibility.

## Dependencies
Depends on `smb_common_open()`, SMB1 oplock acquisition, ofile lookup/close, `smb_fsop_eaccess()`, node type checks, and SMB result mbuf encoding.

## Risks
After `smb_common_open()` succeeds, every later encode or resource-type failure must close the newly allocated ofile. The handler does this via `errout`; future edits need to preserve that invariant.

The extended-response path intentionally violates normal SMB word-count encoding rules, so generic response helpers cannot be used there.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_create_andx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_create.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_create.c

## Summary
Implements SMB1 `NT_TRANSACT_CREATE`, a create/open variant that can carry extended attributes or a security descriptor. Extended attributes are not decoded, while an optional security descriptor is decoded and passed into the common open path.

## Main Responsibilities
- Decodes NT transact create parameters and pathname.
- Converts create flags to requested oplock level.
- Decodes optional self-relative security descriptors from request data.
- Frees decoded security descriptor memory after dispatch.
- Performs the same create-option validation and common-open flow as `NT_CREATE_ANDX`.
- Encodes normal or extended NT transact create response parameters.

## Key APIs
- `smb_pre_nt_transact_create()`.
- `smb_post_nt_transact_create()`.
- `smb_nt_transact_create()`.

## Important Behavior
The pre-handler decodes `sd_len` and, when nonzero, calls `smb_decode_sd()` over the request data mbuf, stores a kmem-allocated `smb_sd_t` on `op->sd`, and leaves cleanup to the post-handler.

The main create handler rejects unsupported file-id opens, invalid create options/dispositions, and delete-on-close without delete access. It maps backup intent to privileged credentials and delegates creation to `smb_common_open()`.

Responses are written to `xa->rep_param_mb`; extended responses include volume GUID space, file id, max access, and guest access fields.

## Dependencies
Shares the same open machinery as `smb_nt_create_andx.c`, plus security descriptor decode/free helpers from `smb_nt_transact_security.c`.

## Risks
The file comment says EAs are unsupported and not decoded. Clients sending non-empty EAs through this path do not get full EA application semantics.

Security descriptor ownership is split between decode, `op->sd`, and post-cleanup; early errors after allocation must keep cleanup paths intact.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_create.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_ioctl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_ioctl.c

## Summary
Implements SMB1 NT transact FSCTL/IOCTL dispatch for a small supported set of Windows filesystem control codes.

## Main Responsibilities
- Decodes function code, FID, FSCTL flag, and command flags.
- Dispatches recognized FSCTLs through a static table.
- Implements sparse attribute toggling.
- Validates but does not implement zero-data punching.
- Returns simple allocated-range information.
- Delegates snapshot enumeration to VSS support.
- Rejects or no-ops selected FSCTLs for compatibility.

## Key APIs
- `smb_nt_transact_ioctl()`.
- `smb_nt_trans_ioctl_set_sparse()`.
- `smb_nt_trans_ioctl_set_zero_data()`.
- `smb_nt_trans_ioctl_query_alloc_ranges()`.
- `smb_nt_trans_ioctl_enum_snaps()`.

## Important Behavior
Unsupported function codes return `NT_STATUS_NOT_SUPPORTED`. `FSCTL_GET_OBJECT_ID` returns invalid parameter, and `FSCTL_FIND_FILES_BY_SID` succeeds as a no-op.

`SET_SPARSE` requires writable tree, non-IPC disk file, non-directory handle, then reads and updates DOS attributes through `smb_node_getattr()` and `smb_node_setattr()`.

`QUERY_ALLOCATED_RANGES` returns no data for zero-length files. Otherwise it decodes the requested offset/length and returns exactly that single range, regardless of real sparse extents.

`SRV_ENUMERATE_SNAPSHOTS` validates the handle and calls `smb_vss_enum_snapshots()` with response data in `xa->rep_data_mb`.

## Dependencies
Relies on ofile lookup/release, node attribute helpers, DOS sparse attribute support, VSS snapshot enumeration, SMB FSCTL constants, and mbuf-chain encoding.

## Risks
`FSCTL_SET_ZERO_DATA` is explicitly marked as a no-op bug and does not punch or zero file ranges. The comment notes that proper support must break oplocks.

`QUERY_ALLOCATED_RANGES` is a compatibility approximation, not an accurate sparse extent query.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_notify_change.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_notify_change.c

## Summary
Provides the SMB1-specific wrapper around the common change-notify engine in `smb_notify.c`.

## Main Responsibilities
- Decodes SMB1 NT transact notify setup words.
- Looks up the watched directory FID.
- Maps `WatchTree` to the internal subdirectory-change event bit.
- Calls `smb_notify_act1()` and `smb_notify_act2()`.
- Finishes async notify replies from the notify taskq.
- Builds SMB1 NT transact response framing around common notify data.

## Key APIs
- `smb_nt_transact_notify_change()`.
- `smb_nt_transact_notify_finish()`.

## Important Behavior
If `act2` parks the request, the handler returns `SDRC_SR_KEPT`; later `smb_nt_transact_notify_finish()` calls `smb_notify_act3()`, encodes a transact reply, sends it, cleans up the request, marks it completed, and frees it.

`NT_STATUS_NOTIFY_CLEANUP` is converted to a successful empty SMB1 transaction response after the watched handle closes.

The common notify code places output in `sr->raw_data`; the synchronous path swaps `raw_data` with `xa->rep_param_mb` so NT transact dispatch sees the data in the expected parameter buffer.

## Dependencies
Depends on common notify request states, SMB1 NT transact layout math, dispatcher statistics, DTrace completion probes, and `smbsr_send_reply()`/cleanup.

## Risks
The async finish function copies response-layout logic from NT transact dispatch. Changes to SMB1 transact reply framing need to be mirrored here.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_notify_change.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_quota.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_quota.c

## Summary
Implements SMB1 NT transact quota query and set operations for trees with quota support enabled.

## Main Responsibilities
- Validates tree quota feature availability.
- Decodes query parameters for SID list, start SID, restart, and single-entry behavior.
- Builds quota root paths from the tree root mount path.
- Initializes and frees quota SID lists and quota response data.
- Encodes quota query results and resume state.
- Restricts quota setting to administrators.
- Decodes and submits quota set records.

## Key APIs
- `smb_nt_transact_query_quota()`.
- `smb_nt_transact_set_quota()`.

## Important Behavior
Query requires exactly 16 parameter bytes and rejects requests that specify both SID list and start SID. It chooses `SMB_QUOTA_QUERY_SIDLIST`, `SMB_QUOTA_QUERY_STARTSID`, or `SMB_QUOTA_QUERY_ALL`, computes maximum response capacity, initializes SIDs from request data, calls `smb_quota_query()`, and encodes returned quotas.

`NT_STATUS_NO_MORE_ENTRIES` is converted to warning status plus successful completion with zero returned length, and the ofile quota resume SID is cleared.

Set quota requires exactly 2 parameter bytes, an admin user, a disk ofile, and a decoded quota list. It submits the list to `smb_quota_set()` and returns only status.

## Dependencies
Depends on quota feature flags, user admin checks, ofile lookup, `smb_node_getmntpath()`, quota XDR/free helpers, mbuf-chain quota encoders/decoders, and per-ofile quota resume storage.

## Risks
The quota root path is derived from the tree root mount path, so quota behavior follows the mounted filesystem boundary rather than arbitrary share path semantics.

The set path returns `-1` for non-admin access instead of the usual `SDRC_ERROR`, matching local convention only if dispatch treats nonzero as error.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_security.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_security.c

## Summary
Implements SMB1 NT transact query/set security descriptor operations and the local encoder/decoder for SMB self-relative security descriptors, SIDs, ACLs, and ACEs.

## Main Responsibilities
- Reads security descriptors for disk file handles.
- Writes security descriptors for disk file handles.
- Masks SACL requests on filesystems that do not support `ACE_T`.
- Rejects writes on readonly trees.
- Encodes self-relative security descriptors into response data.
- Decodes self-relative security descriptors from request data.
- Allocates and frees decoded SID/ACL structures through SMB security helpers.

## Key APIs
- `smb_nt_transact_query_security_info()`.
- `smb_nt_transact_set_security_info()`.
- `smb_encode_sd()`, `smb_encode_sid()`.
- `smb_decode_sd()`, `smb_decode_sid()`.

## Important Behavior
Query decodes FID and `secinfo`, looks up a disk ofile, adopts the ofile credential, reads the descriptor with `smb_sd_read()`, calculates the encoded length, and either returns `NT_STATUS_BUFFER_TOO_SMALL` with a size hint or encodes the descriptor.

Set decodes FID and `secinfo`, rejects readonly trees, decodes the supplied descriptor, validates required owner/group fields, and skips writes to system nodes. Non-`ACE_T` targets have SACL bits removed from requested security information.

`sm b_encode_sd()` writes a self-relative header and offsets for owner, group, SACL, and DACL, then serializes the selected components. DACL ACEs are emitted from the sorted ACL list; SACL ACEs are emitted in array order.

`sm b_decode_sd()` shadows the request chain, validates component offsets against the descriptor header, ensures SACL/DACL present bits agree with nonzero offsets, and decodes pointed-to SIDs/ACLs.

## Dependencies
Depends on SMB security descriptor model helpers, SID/ACL allocation/free, filesystem security read/write functions, mbuf-chain shadowing, ofile credentials, tree ACL type, and readonly tree checks.

## Risks
`sm b_decode_sid()` checks `bytes_left < sizeof (smb_sid_t)`, which is larger than the minimum wire SID header. Very short but otherwise valid SIDs may be rejected depending on `smb_sid_t` layout.

Set-security returns success without writing when the target node is marked system, silently protecting special files.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_odir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_odir.c

## Summary
Implements SMB open-directory search handles (`smb_odir_t`). It manages directory-search lifetime, VOP readdir buffering, wildcard/name matching, file-info lookup, named-stream enumeration, access-based enumeration, short-name/case-conflict behavior, and resume cookies.

## Main Responsibilities
- Opens directory searches by path, by existing directory handle, or on xattr stream directories.
- Maintains the OPEN/IN_USE/CLOSING/CLOSED odir state machine.
- Reads directory entries through `smb_vop_readdir()`.
- Converts `dirent64_t` or `edirent_t` records into `smb_odirent_t`.
- Returns basic directory entries, full `smb_fileinfo_t`, or named stream info.
- Saves and restores search cookies, last filename, and resume offsets.
- Applies wildcard matching, DOS reserved-name filtering, short-name matching, CATIA conversion, ABE, and search-attribute checks.
- Follows symlinks for attribute reporting where policy permits.

## Key APIs
- `smb_odir_openpath()`, `smb_odir_openfh()`, `smb_odir_openat()`.
- `smb_odir_hold()`, `smb_odir_release()`, `smb_odir_close()`.
- `smb_odir_read()`, `smb_odir_read_fileinfo()`, `smb_odir_read_streaminfo()`.
- `smb_odir_save_cookie()`, `smb_odir_save_fname()`, `smb_odir_resume_at()`.
- `smb_odir_reopen()`.

## Important Behavior
`sm b_odir_openpath()` reduces a client path to parent directory plus pattern, checks directory type and list access, allocates an odir id, and creates the search object. `openfh` uses an already opened directory handle. `openat` opens the xattr directory of an unnamed node and searches stream-prefixed entries.

Wildcard searches repeatedly read entries until a valid UTF-8 name matches the pattern and attributes. Single-name searches perform a direct lookup once, then force EOF.

`sm b_odir_next_odirent()` refills an internal fixed buffer when needed, requests extended dirent flags when supported, optionally requests filesystem ABE, and stops when offsets reach `SMB_MAXDIRSIZE`.

For file info, symlinks are followed to report target attributes unless directory symlinks are disabled. Case conflicts can cause generated 8.3 short names to be returned in place of long names.

## State and Synchronization
The odir is listed on the tree odir list and protected by `d_mutex`. Lookups can hold OPEN or IN_USE odirs; close transitions to CLOSING; final release posts deferred deletion so tree-list iteration is not modified in place.

## Dependencies
Depends on tree/session/user references, SMB pathname reduction, VOP readdir/lookup/traverse/access, SMB wildcard and mangling helpers, CATIA translation, xattr directories, stream name policy, and access-based enumeration feature flags.

## Risks
Filename resume handling appears inverted: the `SMB_ODIR_RESUME_FNAME` branch uses the saved last cookie when `strcmp(resume->or_fname, od->d_last_name)` is nonzero, even though the comment says to use it when the names match.

ABE performed in VOP readdir is disabled by default because it can stall large directories; manual per-entry ABE is safer but more expensive.

The source documents resume-by-filename as not fully supported; callers fall back to cookie or current offset behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_odir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_ofile.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_ofile.c

## Summary
Implements SMB open-file handles (`smb_ofile_t`): allocation, open completion, close, lookup, sharing checks, durable/persistent handle state, notification cleanup, delete-on-close transfer, per-tree/per-node list membership, NetFile enumeration, and quota resume state.

## Main Responsibilities
- Allocates proposed ofiles before open completion.
- Inserts open handles into tree AVL lists and node ofile lists.
- Maintains the full open/save-durable/orphan/reconnect/expired/closing/closed state machine.
- Looks up handles by SMB FID, unique id, or persistent id.
- Saves durable handles as orphaned handles for reclaim.
- Generates durable and persistent IDs and maintains the server persistent-id hash.
- Closes disk, printer, and pipe handles and releases associated resources.
- Enforces granted-access and share-mode checks.
- Supports delete-on-close, file seek, flush, service enumeration, and quota resume storage.

## Key APIs
- `smb_ofile_alloc()`, `smb_ofile_open()`, `smb_ofile_close()`, `smb_ofile_free()`.
- `smb_ofile_close_all()`, `smb_ofile_drop()`.
- `smb_ofile_hold()`, `smb_ofile_hold_olbrk()`, `smb_ofile_release()`.
- `smb_ofile_lookup_by_fid()`, `smb_ofile_lookup_by_uniqid()`, `smb_ofile_lookup_by_persistid()`.
- `smb_ofile_set_persistid_dh()`, `smb_ofile_set_persistid_ph()`, `smb_ofile_insert_persistid()`, `smb_ofile_del_persistid()`.
- `smb_ofile_open_check()`, `smb_ofile_rename_check()`, `smb_ofile_delete_check()`.
- `smb_ofile_set_delete_on_close()`.

## Important Behavior
`sm b_ofile_alloc()` fills stable open metadata and references user/tree credentials but does not link the object. `smb_ofile_open()` transitions to OPEN, attaches disk/printer handles to the node, inserts into the tree AVL, and increments counters.

`sm b_ofile_close()` first breaks/cleans oplocks for disk files, transitions to CLOSING, closes pipes or disk resources, handles persistent close cleanup, applies delete-on-close, releases share locks and byte-range locks, closes directory searches, cancels notify watchers, commits pending attributes, sends final modified notifications, and decrements counters.

Durable handle preservation uses SAVE_DH and SAVING transient states, removes the handle from tree/user/session ownership, frees the FID, keeps node/lease/notify/open-state data, and exposes the handle as ORPHANED for reconnect by persistent id.

Share checks are symmetric: requested share access is checked against existing granted access, and requested desired access is checked against existing share access. Rename and delete checks implement narrower protocol-specific sharing rules.

## State and Synchronization
The tree ofile AVL lock must be taken before `f_mutex` when both are needed. Persistent-id hash operations must not run while holding `f_mutex`. Oplock-break lookup can hold ofiles in states that normal FID lookup cannot, and waits through RECONNECT/SAVING transitions.

## Dependencies
Depends on SMB2 durable/persistent handle code, oplocks and leases, node open lists, tree/user/session references, ID pools, persistent-id hash tables, pipe support, share-lock and byte-range-lock helpers, file system close/commit, notify state, and NetFile encoding.

## Risks
Durable handle state is deliberately kept on the node ofile list after tree/user/session references are removed. Callers must respect state-specific field validity, especially during ORPHANED and RECONNECT.

`sm b_ofile_flush()` notes that named-pipe flush should drain writes but currently does nothing for pipe types.

Close and durable-save paths use deferred list posts to avoid deleting while iterating; refcount leaks can keep handles in SAVE_DH until durable timers force closure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_ofile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_open_andx.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_open_andx.c

## Summary
Implements legacy SMB1 open commands: `SMB_COM_OPEN`, `SMB_COM_OPEN_ANDX`, and `TRANS2_OPEN2`. These handlers translate old open-mode/ofun encodings into the common open path and encode legacy SMB1 responses.

## Main Responsibilities
- Decodes classic open and open-andx request formats.
- Converts SMB open mode to desired access and share access.
- Converts SMB open function to NT create disposition.
- Applies write-through and oplock request flags.
- Rejects or ignores legacy fields for Windows compatibility.
- Delegates actual open/create to `smb_common_open()`.
- Acquires SMB1 oplocks when requested.
- Encodes standard and extended legacy open responses.
- Rejects non-empty EA lists in `TRANS2_OPEN2`.

## Key APIs
- `smb_pre_open()`, `smb_post_open()`, `smb_com_open()`.
- `smb_pre_open_andx()`, `smb_post_open_andx()`, `smb_com_open_andx()`.
- `smb_com_trans2_open2()`.

## Important Behavior
`SMB_COM_OPEN` always uses `FILE_OPEN` and `FILE_NON_DIRECTORY_FILE`; it supports old SMB oplock flags from the SMB header and returns a 7-word response.

`OPEN_ANDX` ignores request search attributes for Windows compatibility, maps extended open flags to oplock and extended-response flags, handles creation time conversion, and encodes either 15-word or 19-word responses. Extended responses include max access and guest access.

`TRANS2_OPEN2` decodes transaction parameters, checks the data block for a non-empty EA list, and returns `NT_STATUS_EAS_NOT_SUPPORTED` when one is supplied. It clamps invalid create dispositions to `FILE_CREATE`.

## Dependencies
Depends on common open, SMB open-mode/share-mode conversion helpers, time conversion helpers, SMB1 oplock acquisition, ofile close on response failure, and transaction mbuf encoding.

## Risks
`sm b_open_dsize_check` is a tunable defaulting to disabled, so oversized legacy allocation sizes are normally passed through common open logic after 32-bit protocol truncation in responses.

`TRANS2_OPEN2` accepts only an empty EA payload; clients depending on EAs receive an explicit unsupported status.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_open_andx.c -->