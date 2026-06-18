# Group Research: group_497_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_bbd5c8cf7cfd

Scope: `Docs/research_subset_a.md`. This group covers illumos SMB server common filesystem operations under `usr/src/uts/common/fs/smbsrv`, centered on oplock state management, open/create, rename/link, set-file information, SMB1 transaction assembly, credentials, and delete.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_oplock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_oplock.c

This file is the filesystem-level SMB oplock and lease state machine shared by SMB1 and SMB2. It intentionally follows MS-FSA sections for requesting oplocks, acknowledging breaks, and checking whether filesystem operations require an oplock break. Protocol-specific indication and wait plumbing is outside this file, mainly through `smb_oplock_ind_break`, `smb_oplock_ind_break_in_ack`, and callers that run `smb_oplock_wait_break`.

Primary entry points are `smb_oplock_request`, `smb_oplock_request_LH`, `smb_oplock_ack_break`, operation-specific break helpers (`smb_oplock_break_OPEN`, `smb_oplock_break_BATCH`, `smb_oplock_break_HANDLE`, `smb_oplock_break_CLOSE`, `smb_oplock_break_READ`, `smb_oplock_break_WRITE`, `smb_oplock_break_SETINFO`, `smb_oplock_break_DELETE`, `smb_oplock_break_PARENT`), and `smb_oplock_move`. Internal helpers include `CompareOplockKeys`, `RecomputeOplockState`, `smb_oplock_req_excl`, `smb_oplock_req_shared`, and `smb_oplock_break_cmn`.

The core state is `node->n_oplock`, protected by `node->n_oplock.ol_mutex` while the node open-file list lock is held as a reader. The state uses counters and per-ofile flags for Level II (`cnt_II`, `onlist_II`), read (`cnt_R`, `onlist_R`), read-handle (`cnt_RH`, `onlist_RH`), read-handle break queue (`cnt_RHBQ`, `onlist_RHBQ`, `BreakingToRead`), and exclusive open state (`excl_open`). `RecomputeOplockState` derives `ol_state` from those lists, including mixed R/RH and RH break-to-read or break-to-none states. First grants install FEM hooks through `smb_fem_oplock_install`; transitions to `NO_OPLOCK` remove them with `smb_fem_oplock_uninstall`.

`CompareOplockKeys` implements MS-FSA oplock key comparison, with argument order mattering. It treats non-SMB callers as non-matching by accepting `OperOpen == NULL`, handles empty target and parent lease keys, and supports `PARENT_OBJECT` by comparing an operation open's parent key against an oplock open's target key. This is important for parent directory lease break semantics, although this implementation notes directory leases are not yet supported.

`smb_oplock_request_LH` validates directory versus file requests, rejects unsupported directory leases, maps old oplock levels and granular lease cache flags, rejects requests conflicting with byte-range locks or write-through state, and delegates to exclusive or shared grant algorithms. Exclusive requests can upgrade same-key shared leases to exclusive, reject mismatched keys, and move existing same-lease grants by issuing `STATUS_OPLOCK_SWITCHED_TO_NEW_HANDLE`. Shared requests allow Level II, R, and RH grants according to current state, reject incompatible same-key RH/RHBQ combinations, and may return `NT_STATUS_OPLOCK_BREAK_IN_PROGRESS` when the new grant is immediately in a breaking state.

`smb_oplock_ack_break` handles both legacy break acknowledgements and granular lease break acknowledgements. It validates protocol state strictly, clears or converts break states, broadcasts `WaitingOpenCV` to release waiters, and can request replacement shared oplocks while acknowledging. Several comments document illumos-specific corrections for cases missing or unclear in MS-FSA, such as clients acknowledging break-to-none with R/RH and requiring another break indication.

`smb_oplock_break_cmn` is the central algorithm for operations that may conflict with caching. Its callers encode desired break direction and cache classes into `BreakCacheLevel`. It compares operation keys against exclusive and shared holders, sends appropriate break indications, marks RH holders into `RHBQ`, recomputes state, and returns `NT_STATUS_OPLOCK_BREAK_IN_PROGRESS` when the caller must wait. The operation-specific wrappers map OPEN, READ, WRITE, SETINFO, DELETE, CLOSE, and parent operations to MS-FSA break rules. `smb_oplock_break_CLOSE` is special because it also clears per-ofile oplock state and may notify the SMB layer with `NT_STATUS_OPLOCK_HANDLE_CLOSED`.

Integration notes: callers must honor the lock preconditions on `_LH` and close paths, and must wait when `NT_STATUS_OPLOCK_BREAK_IN_PROGRESS` is returned. The file assumes open-file list traversal is stable under the list reader lock and `ol_mutex`. Many transitions rely on counters matching per-ofile flags; future changes must update both. `smb_oplock_move` swaps FSA and SMB-level oplock state between ofiles for durable/lease close behavior, so it is sensitive to callers passing an empty destination ofile and holding `ol_mutex`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_oplock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_rename.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_rename.c

This file contains common rename and hard-link implementation for SMB1 Trans2 set info, SMB2 set info, and path-based SMB1 operations. It translates SMB rename/link semantics into path reduction, source and destination node validation, oplock breaking, share and byte-range conflict checks, filesystem operations, and change notifications.

Primary entry points are `smb_setinfo_rename`, `smb_common_rename`, `smb_setinfo_link`, and `smb_make_link`. Helpers are `smb_rename_check_stream`, `smb_rename_lookup_src`, `smb_rename_check_src`, `smb_rename_release_src`, `smb_rename_check_attr`, and `smb_rename_errno2status`.

`smb_setinfo_rename` and `smb_setinfo_link` are small wrappers for handle-based set-info calls. They fill `sr->arg.dirop` source and destination FQI state, set the relevant information level (`FileRenameInformation` or `FileLinkInformation`), validate the destination pathname relative to the share root, and delegate to common code. The overwrite flag is normalized to the local `SMB_RENAME_FLAG_OVERWRITE` bit.

`smb_common_rename` supports both handle-provided and path-looked-up source nodes. It rejects unsupported stream rename forms, obtains references on source directory and file nodes, and calls `smb_rename_check_src` to break oplocks and enter a critical section on the source node. It then resolves the destination directory and final component, detects exact no-op renames, and handles same-directory case-only renames differently depending on tree case-sensitivity. If the destination exists, overwrite must be allowed; the destination receives delete-style oplock breaks, delete permission checks, node critical-section entry, and NBL conflict checks before the underlying `smb_fsop_rename`.

Rename cleanup is explicit and stateful. On success, the file sends paired change notifications for same-directory renames (`FILE_ACTION_RENAMED_OLD_NAME` then `FILE_ACTION_RENAMED_NEW_NAME`) or remove/add notifications for cross-directory moves. `smb_rename_release_src` leaves the source critical section and releases both source node references. Destination critical sections and references are released separately when an existing target was overwritten.

`smb_make_link` mirrors the path and source lookup portions of rename but does not call `smb_rename_check_src`, because the source remains linked. It disallows named streams and directories as hard-link sources, enters a read critical section on the source, resolves and validates the destination name, requires that the destination not exist, calls `smb_fsop_link`, and notifies the destination directory on success.

`smb_rename_check_src` is the key concurrency hook. For handle-based rename it breaks `FileRenameInformation` oplocks using the actual ofile, waits if needed, and starts a node critical section. For path-based SMB1 rename it simulates delete/open behavior: it breaks delete-style oplocks with no ofile, checks rename sharing rules, breaks setinfo oplocks, enters NBL critical section, and checks `NBL_RENAME` conflicts. This path explicitly notes a future internal-open cleanup.

Important constraints: stream renames are not implemented and return access denied for destination stream forms or invalid parameter for other stream involvement. Hidden and system source attributes are filtered by search attributes during path-based source lookup. Error mapping preserves legacy SMB behavior for collisions, sharing violations, not-found cases, invalid parameters, access denied, directories, and internal I/O errors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_setfile.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_setfile.c

This file implements common SMB1 Trans2 and SMB2 set-file information handlers for basic metadata, end-of-file size, allocation size, and delete-on-close disposition. The handlers decode wire data from `smb_setinfo_t.si_data`, validate SMB/FSCC semantics, break relevant oplocks when the operation changes data or handle caching, then apply attributes through node-level filesystem helpers.

Public entry points are `smb_set_basic_info`, `smb_set_eof_info`, `smb_set_alloc_info`, and `smb_set_disposition_info`.

`smb_set_basic_info` decodes `FileBasicInformation` times and attributes. It rejects temporary attributes on directories and directory attributes on non-directories. Nonzero timestamp fields are converted from NT time to Unix time and placed into `smb_attr_t`; negative special values less than `-2` are invalid. Attribute handling follows Windows compatibility: zero means no attribute update, while a nonzero value is set as DOS attributes through `SMB_AT_DOSATTR`. The final update goes through `smb_node_setattr` with the request user's credential and current ofile.

`smb_set_eof_info` decodes a 64-bit EOF, rejects directories, breaks `FileEndOfFileInformation` oplocks with `smb_oplock_break_SETINFO`, optionally moves SMB2 requests async while waiting, and then sets `SMB_AT_SIZE` through `smb_node_setattr`. `smb_set_alloc_info` is structurally the same but uses `FileAllocationInformation` and writes `SMB_AT_ALLOCSZ`.

`smb_set_disposition_info` toggles delete-on-close for the open file. It requires a real ofile and `DELETE` granted access. Clearing disposition resets the node delete-on-close state immediately. Setting disposition checks the current DOS readonly attribute with `smb2_ofile_getattr` and returns `NT_STATUS_CANNOT_DELETE` if readonly, breaks handle-caching oplocks for `FileDispositionInformation`, waits as needed, and then calls `smb_node_set_delete_on_close`. CATIA tree support is propagated through flags.

Integration notes: EOF and allocation changes are data-affecting and must not bypass oplock breaks. Disposition handling distinguishes ofile state from node delete-on-close state and follows documented Windows 2000 behavior. All functions return NT status values rather than SMB dispatch result codes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cmn_setfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_common_open.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_common_open.c

This file is the common open/create implementation used by multiple SMB command front ends. It converts legacy open modes to NT create semantics, validates path and object options, performs lookup or creation, handles streams, enforces access and share rules, coordinates oplock breaks before share checks, opens the backing vnode, creates the SMB ofile, applies deferred open attributes, and unwinds partial state on error.

Public helpers are `smb_omode_to_amask`, `smb_denymode_to_sharemode`, `smb_ofun_to_crdisposition`, and `smb_common_open`. Internal helpers are `smb_access_generic_to_file`, `smb_set_open_attributes`, and `smb_delete_new_object`.

The conversion helpers implement SMB compatibility mapping. `smb_access_generic_to_file` expands `GENERIC_*` access bits to file access masks while excluding synchronize in selected cases. `smb_omode_to_amask` maps SMB open access modes to generic read/write/execute/all file masks. `smb_denymode_to_sharemode` maps deny modes to NT share access, with compatibility mode allowing executable files less sharing. `smb_ofun_to_crdisposition` maps SMB open-function bits to create dispositions and returns an out-of-range disposition for invalid row values.

`smb_common_open` begins with cancellation and create-option validation, maximum-allowed handling, per-session open limits, and FID allocation from the tree pool. IPC opens are routed to named-pipe handling with a threshold on pipe instances. Disk tree opens validate the pathname, reduce it to parent directory plus final component, lock the parent directory for create/lookup serialization, and select link-following behavior based on delete-only access.

For existing objects, it validates node type against directory/non-directory requirements, resolves named streams when present, rejects delete-pending nodes, enforces create disposition collisions, applies overwrite/supersede access adjustments, checks readonly semantics, rejects delete-on-close on dataset roots, performs access checks and maximum allowed expansion, grants owner read-control/read-attributes where appropriate, and creates missing streams if allowed. It allocates a proposed ofile before oplock and share checks so oplock key comparisons can use the pending open.

The concurrency sequence for existing streams/files is important: increment opening count, break batch oplocks before share checking, attempt share reservation with `smb_fsop_shrlock`, break handle caching once on sharing violation, optionally close same-client orphaned durable handles for SMB2, delay SMB1 sharing violations up to the historical 1-second behavior, then run the open-related oplock break. If a break causes delete-on-close to commit deletion, the code tears down the proposed ofile and re-enters the create path as if lookup had failed.

For new objects, it rejects unsupported dispositions and temporary directory attributes, handles readonly plus delete-on-close, checks security privilege for `ACCESS_SYSTEM_SECURITY`, validates the final name, rejects creation under delete-on-close directories, builds creation attributes for file, stream, or directory, defers applying readonly until after the ofile exists, optionally records create time, calls `smb_fsop_create` or `smb_fsop_mkdir`, and stakes a share lock. Parent oplock breaks are sent after creation through `smb_oplock_break_PARENT`.

After lookup/create and conflict handling, the function checks that the tree is still connected, opens the underlying FS object with `smb_fsop_open`, calls `smb_ofile_open`, applies deferred attributes via `smb_set_open_attributes`, refreshes all attributes for the response, propagates write-through to the node flag, fills response fields, and returns success. Oplock acquisition itself is protocol-specific and is done by callers.

The `errout` block is a dense but central invariant: close or free any ofile, remove share locks, roll back newly created objects, free stream-name memory, unlock held nodes, decrement opening counts, release node references, and free unused FIDs. Future edits must preserve the boolean state flags that drive this cleanup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_common_open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_common_transact.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_common_transact.c

This file implements common SMB1 transaction, transaction2, and NT transaction request assembly, secondary-fragment reassembly, dispatch, response encoding, selected legacy RAP handlers, named-pipe transaction support, and the lifetime management for `smb_xa_t` transaction contexts.

Top-level SMB dispatch entry points include pre/post hooks and handlers for `SMB_COM_TRANSACTION`, `SMB_COM_TRANSACTION_SECONDARY`, `SMB_COM_IOCTL`, `SMB_COM_TRANSACTION2`, `SMB_COM_TRANSACTION2_SECONDARY`, `SMB_COM_NT_TRANSACT`, and `SMB_COM_NT_TRANSACT_SECONDARY`. Internal dispatchers are `smb_trans_dispatch`, `smb_trans2_dispatch`, and `smb_nt_trans_dispatch`. Transaction context functions are `smb_xa_create`, `smb_xa_delete`, `smb_xa_hold`, `smb_xa_rele`, `smb_xa_open`, `smb_xa_close`, `smb_xa_complete`, and `smb_xa_find`.

Initial transaction handlers decode counts, offsets, flags, timeout, setup words, parameter bytes, and data bytes into a newly allocated `smb_xa_t`. They copy request fragments from the incoming command mbuf into the XA request mbufs, open the XA, attach it to `sr->r_xa`, and either return an empty interim response or mark the XA complete and dispatch it. Secondary handlers look up an existing XA by request identity, verify signing when enabled, reject mismatched command families, adjust total counts downward when the secondary reports lower totals, honor parameter/data displacements by setting mbuf offsets, append fragment bytes, and dispatch only when the advertised total parameter and data counts have arrived.

`smb_nt_trans_dispatch` routes NT transaction functions including NT create, notify change, query/set security descriptor, IOCTL, quota query/set, and rename. It validates handler result codes, verifies response size limits against requested maxima, computes setup/parameter/data offsets and padding, and encodes the NT transaction response. `smb_trans2_dispatch` similarly routes Trans2 opcodes including open2, create directory, find first/next, query/set filesystem information, query/set path/file information, and DFS referrals. Query path/file information gets a special padding/converter value so protocol analyzers decode the data format correctly. `smb_trans_dispatch` handles named-pipe setup opcodes and legacy mailslot/RAP APIs.

Legacy RAP support is intentionally limited. Share enumeration and share get-info are guarded by global tunables defaulting to disabled because modern clients use MS-RPC and these paths do not implement access-based enumeration. Workstation, user, server get-info, and NetServerEnum2 provide small compatibility responses from server configuration. The mailslot filter only accepts LANMAN and browser mailslot names.

Named-pipe transaction support is in `smb_trans_nmpipe`. It looks up the fid, builds an `smb_fsctl_t` for `FSCTL_PIPE_TRANSCEIVE`, treats transaction send data as pipe write input and response data as pipe read output, and allows warning statuses such as buffer overflow while treating error severity as dispatch failure.

`smb_xa_create` is the allocation and admission-control point. It caps setup, parameter, and data counts (`200`, `32 KiB`, `64 KiB`), limits response allocation requests to those caps, copies SMB header identity into the XA, initializes request and reply mbuf maximum sizes, and rejects duplicate incomplete transactions with the same MID and PID on the session XA list. `smb_xa_complete` marks completion and rewinds request mbuf offsets for parsing. Close/release code removes closed unreferenced XAs from the session list and frees all mbuf chains plus pipe-name memory.

Important risks and assumptions: offset/displacement handling allows out-of-order secondary fragments but relies on mbuf copy bounds. NT transaction secondary checks `xa->smb_com != SMB_COM_TRANSACTION2`, matching the code as read, which is notable because the primary NT transaction command has a distinct command code. Response encoders must keep exact SMB header offset and padding formulas for wire compatibility. XA lifetime depends on correct pairing of `smb_xa_open`, `smb_xa_close`, and reference release.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_common_transact.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_create.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_create.c

This file implements legacy SMB1 create command front ends and funnels them into `smb_common_open` through `smb_common_create`. It handles `SMB_COM_CREATE`, `SMB_COM_CREATE_NEW`, and `SMB_COM_CREATE_TEMPORARY`.

Entry points are `smb_pre_create`, `smb_post_create`, `smb_com_create`, `smb_pre_create_new`, `smb_post_create_new`, `smb_com_create_new`, `smb_pre_create_temporary`, `smb_post_create_temporary`, `smb_com_create_temporary`, and `smb_common_create`.

The `pre` functions zero `sr->arg.open`, decode DOS attributes, modification time, and path data from the SMB request, set create disposition and options appropriate to the command, and emit DTrace start probes. `SMB_COM_CREATE` uses `FILE_OVERWRITE_IF` and forces `FILE_NON_DIRECTORY_FILE`; `SMB_COM_CREATE_NEW` uses `FILE_CREATE`; temporary create also uses `FILE_CREATE` but takes a directory path and later synthesizes a filename.

`smb_com_create` and `smb_com_create_new` call `smb_common_create` and encode a one-word response containing the FID. `smb_com_create_temporary` increments a static `tmp_id`, builds a name like `ttNNNNN.tmp`, replaces the request path with `directory\name`, calls `smb_common_create`, and returns both FID and generated name.

`smb_common_create` normalizes legacy create parameters. It converts nonzero and non-`UINT_MAX` local modification time to GMT, sets size to zero, uses compatibility read/write open mode, derives desired access and share access through `smb_omode_to_amask` and `smb_denymode_to_sharemode`, maps SMB1 oplock header flags to batch, exclusive, or none, calls `smb_common_open`, and then runs `smb1_oplock_acquire` when an oplock was requested and open succeeded. If no oplock is granted/requested, it clears the SMB header oplock flags before responding.

Integration notes: this file is protocol-front-end glue rather than filesystem logic. The static temporary-name counter is process-local and simple; collision behavior is delegated to the create path. Error reporting is handled by setting `smbsr_status` after `smb_common_open` returns a nonzero NT status.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_create.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cred.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cred.c

This file builds kernel credentials from authenticated SMB access tokens. It bridges SMB identity mapping, Windows SID metadata, POSIX group membership, and illumos credential structures.

Primary entry points are `smb_cred_create` and `smb_kcred_create`. Internal helpers are `smb_cred_set_sid` and `smb_cred_set_sidlist`.

`smb_cred_create` allocates a fresh cred with `crget`, preserves `PRIV_SYS_SMB` in the permitted privilege set, selects a primary gid, sets uid/gid with `crsetugid`, installs POSIX supplementary groups with `crsetgroups`, and attaches Windows SID identities for user, primary group, owner, and group list. If the SMB user maps to a non-ephemeral Unix ID and has POSIX groups, the first POSIX group is used as credential gid; otherwise the token primary group mapping is used. Failures during uid/gid or group setup free the cred and return `NULL`.

`smb_cred_set_sid` converts an SMB SID to string form, splits it into domain plus RID, copies the mapped numeric ID and SID attributes, and resolves the kernel SID domain with `ksid_lookupdomain`. The helper asserts the token identity and SID are present. `smb_cred_set_sidlist` allocates a variable-sized `ksidlist_t`, initializes each group SID through `smb_cred_set_sid`, and counts non-ephemeral IDs by comparing against `IDMAP_WK__MAX_GID`.

`smb_kcred_create` creates a blank `crget` credential for SMB-internal kcred uses such as durable-handle import, where the returned cred must later be accepted by `smb_user_setcred`.

Integration notes: this code assumes `token->tkn_posix_grps` is populated. SID-domain references obtained by `ksid_lookupdomain` become part of the cred SID structures. The normal user credential and backup/restore intent credential are separate; this file only constructs the normal token-derived cred and the minimal internal kcred variant.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_cred.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_delete.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_delete.c

This file implements legacy `SMB_COM_DELETE`, including single-file and wildcard deletion. It validates the path, resolves the parent directory, checks directory listing access, filters candidates by search attributes and DOS attributes, breaks oplocks, enforces share and byte-range conflict rules, and removes files through filesystem operations.

Entry points are `smb_pre_delete`, `smb_post_delete`, and `smb_com_delete`. Internal helpers are `smb_delete_single_file`, `smb_delete_multiple_files`, `smb_delete_find_fname`, `smb_delete_check_dosattr`, `smb_delete_remove_file`, `smb_delete_check_path`, and `smb_delete_error`.

`smb_pre_delete` decodes search attributes and path into `sr->arg.dirop.fqi`. `smb_com_delete` initializes and validates the pathname, performs delete-specific path checks, detects wildcards, reduces the path to parent directory and last component, validates the parent is a directory, rejects deleting `..` at the share root, checks `FILE_LIST_DIRECTORY` access on the parent, then dispatches to single or wildcard deletion. On success it returns an empty SMB response; on failure it uses the populated `smb_error_t`.

`smb_delete_single_file` validates the object name, performs a direct lookup in the parent directory, checks DOS attributes, calls the remove helper, and releases the file node. `smb_delete_multiple_files` opens an odir over the search path with broad search attributes, iterates matching names via `smb_odir_read`, does case-sensitive lookup of each returned name, applies delete-specific attribute filtering, and deletes candidates. Readonly matches abort with `NT_STATUS_CANNOT_DELETE`. Directory matches either end the search when directories were requested or are skipped through error handling. If no file is deleted, it reports `NT_STATUS_NO_SUCH_FILE`.

`smb_delete_check_dosattr` obtains DOS attributes with kcred and enforces SMB delete rules: directories are not deleted by this command, readonly files return cannot-delete, and hidden/system files are invisible unless the corresponding search attribute was requested. It also uses `SMB_PATHFILE_IS_READONLY`, so path-specific readonly behavior is respected.

`smb_delete_remove_file` performs the concurrency-sensitive removal. It first breaks delete-style oplocks with `smb_oplock_break_DELETE` and waits if necessary, then locks the node, checks delete/share state with `smb_node_delete_check`, enters an NBL critical section, checks `NBL_REMOVE` conflicts across the whole file range, applies CATIA flags when needed, and calls `smb_fsop_remove` using the node's parent and object name. Cleanup exits the critical section before returning.

`smb_delete_check_path` rejects missing final components as directory access errors and rejects `.` or wildcard patterns resolving to `.` when directory search attributes are involved. `smb_delete_error` is a small helper for consistent NT status plus DOS error class/code population.

Integration notes: this is SMB1 path-based deletion, not handle-based set-disposition deletion. It deliberately breaks oplocks before share and lock checks so clients holding batch/handle caching can flush or close before the server decides whether deletion is blocked. Wildcard deletion can skip transient not-found races after a directory entry is enumerated.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_delete.c -->