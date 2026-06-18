# Research Group subset-b-007705

This grouped report covers four OpenAFS Windows cache-manager vnode and volume-status files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_vnodeops.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_vnodeops.c

## Purpose

`cm_vnodeops.c` is the main Windows cache-manager vnode operation implementation for OpenAFS. It translates Windows/SMB/redirector operations into AFS cache-manager actions and RXAFS RPCs: path lookup, mount-point and symlink traversal, directory enumeration, create/remove/rename/link/symlink/mkdir/rmdir, attribute and length updates, open permission checks, DFS-link handling, bulk status prefetch, and byte-range lock emulation.

The file sits on the boundary between the Windows front ends (`smb`, redirector, pioctl-style callers), cache-manager state (`cm_scache_t`, buffers, DNLC, directory caches, volume/cell objects), and AFS file-server RPCs. Most operations follow the same pattern: validate client-visible semantics, acquire scache/dir/cache locks, use `cm_SyncOp` to serialize with callbacks/data/status/store operations, call an `RXAFS_*` routine through `cm_ConnFromFID`, run `cm_Analyze` retry/failover handling, map the RPC error into a cache-manager error, merge returned status with `cm_MergeStatus`, and update local caches or redirector invalidation state.

## Important APIs, Types, and Functions

Lookup and path traversal:

- `cm_stricmp` implements a DOS/SMB-oriented case-insensitive byte-string compare using the global `cm_foldUpper` table, including selected 8-bit character folding.
- `cm_ApplyDir` iterates AFS directory entries from cache buffers, supports directory listing callbacks, lookup callbacks, and optional return of a scache found through DNLC.
- `cm_LookupSearchProc` performs normalized exact or case-folded name matching, includes 8.3 short-name matching when enabled, and records match quality in `cm_lookupSearch_t`.
- `cm_LookupInternal` resolves one directory component, including `.`/`..`, DNLC/BPlus/legacy directory lookup paths, case-fold behavior, freelance-root dynamic mount insertion, mount-point chasing, and DNLC insertion for exact matches.
- `cm_Lookup` wraps `cm_LookupInternal`, handles root-only `@vol:` volume references, rejects special SMB ioctl names, and expands `@sys` through `cm_ExpandSysName`.
- `cm_NameI` walks a full path across `tidPathp` and `pathp`, follows symlinks when requested, detects symlink/fid cycles, limits expanded fid count, tracks directory context for relative links, and handles root/freelance volume-reference fallbacks.
- `cm_EvaluateVolumeReference` parses direct `@vol:<cell>{%,#}<volume>` references and returns the root scache for the chosen RW/RO/BACK volume.

Mount points, symlinks, DFS links:

- `cm_ReadMountPoint` fetches and caches mount-point string data in `scp->mountPointStringp`, keyed by `scp->mpDataVersion`.
- `cm_FollowMountPoint` parses mount-point contents, resolves cell and volume, applies `.backup`/`.readonly` and `cm_followBackupPath` rules, caches `scp->mountRootFid`, and returns the target root scache.
- `cm_HandleLink` fetches symlink contents into `mountPointStringp`, updates `mpDataVersion`, and marks `msdfs:` targets as DFS links.
- `cm_AssembleLink` turns symlink contents plus remaining path suffix into a new path buffer and optional new root. It recognizes OpenAFS mount-root links, local UNC links to the client NetBIOS name, DFS links, unsupported absolute links, and relative links.
- `cm_EvaluateSymLink` evaluates a symlink target from a directory-enumeration context so listing code can report target attributes.

Mutation and status APIs:

- `cm_StatusFromAttr` maps `cm_attr_t` masks and deferred scache fields into `AFSStoreStatus`.
- `cm_SetLength` coordinates buffer truncation/extension, quota preflight through `cm_IsSpaceAvailable`, scache length masks, and deferred mini-store state.
- `cm_SetAttr` dispatches length changes to `cm_SetLength` and otherwise calls `RXAFS_StoreStatus`.
- `cm_Create`, `cm_MakeDir`, `cm_Link`, `cm_SymLink`, `cm_Unlink`, `cm_RemoveDir`, and `cm_Rename` wrap the corresponding AFS directory mutation RPCs and reconcile local directory cache, DNLC, scache status, callbacks, and redirector invalidations.
- `cm_FSync` flushes dirty buffers and deferred truncate/modtime/length state via `buf_CleanVnode` and `cm_StoreMini`.
- `cm_CheckOpen`, `cm_CheckNTOpen`, `cm_CheckNTOpenDone`, and `cm_CheckNTDelete` implement Windows open/delete preflight checks, including rights calculation and mandatory-share-lock probing.
- `cm_Open` resets per-scache prefetch state.

Bulk status:

- `cm_TryBulkProc` collects directory child fids that lack usable callbacks/status and are within the current buffer page.
- `cm_TryBulkStatRPC` batches `RXAFS_InlineBulkStatus` or `RXAFS_BulkStatus`, handles inline per-entry errors, records EACCES entries, and merges callback/status data conservatively.
- `cm_TryBulkStat` releases the directory scache write lock while walking the directory and issuing bulk status RPCs, then reacquires it.

Byte-range locks:

- Lock state macros classify `cm_file_lock_t` objects as active, wait-for-server-lock, wait-for-unlock, lost, deleted, accepted, or client-only.
- `cm_LockCheckRead` and `cm_LockCheckWrite` enforce cache-manager byte-range lock semantics before I/O.
- `cm_Lock`, `cm_RetryLock`, `cm_Unlock`, `cm_UnlockByKey`, `cm_CheckLocks`, `cm_LockMarkSCacheLost`, and `cm_ReleaseAllLocks` implement Windows byte-range lock emulation with optional AFS server lock assertion.
- `cm_IntSetLock`/`cm_IntReleaseLock` wrap `RXAFS_SetLock` and `RXAFS_ReleaseLock`; `cm_CheckLocks` periodically extends active server locks with `RXAFS_ExtendLock`.
- `cm_GenerateKey` and `cm_KeyEquals` define lock owner identity across SMB, redirector, and internal sessions.

## Control Flow

Name lookup starts with `cm_NameI` for full paths or `cm_Lookup` for one component. `cm_NameI` splits `tidPathp` and `pathp` into components, maps `/` to `\`, and repeatedly calls `cm_Lookup`. For root names it may synthesize `@vol:` references from `<cell>{%,#}<volume>` or freelance-root names. `cm_Lookup` expands `@sys` by trying configured sysname values, handles explicit `@vol:` only at the root, and delegates normal names to `cm_LookupInternal`. `cm_LookupInternal` first handles `.`/`..`, converts client names into normalized and filesystem strings, consults BPlus/legacy directory lookup and DNLC paths, falls back to scanning through `cm_ApplyDir`, and chases mount points unless `CM_FLAG_NOMOUNTCHASE` is set.

Directory iteration in `cm_ApplyDir` obtains directory status through `cm_SyncOp`, validates that the scache is a directory, tries DNLC or direct hash lookup for lookup callers, then scans cache buffers page by page. It aligns offsets away from AFS directory headers, obtains buffers with `buf_Get`, fills missing buffers with `cm_GetBuffer`, validates entry flags and name size, and invokes a caller-supplied callback for live entries. Invalid directory entries mark the buffer version bad and return an error.

Mutation operations share a common RPC control path. For example, create/mkdir/symlink/link/remove/rename begin a `cm_dirOp_t`, establish `CM_SCACHESYNC_STOREDATA` on the directory or directories, increment active RPC counters, call the corresponding `RXAFS_*` function in a `cm_Analyze` retry loop, map the error, merge returned directory/file status, update local directory entries if the cached directory changed only in the expected single way, and release sync/dir-op state. Delete and rename also discard or invalidate affected scaches because file servers invalidate callbacks on moved or destroyed objects.

Attribute changes split on length. Non-length changes call `RXAFS_StoreStatus`; length changes are staged locally through `cm_SetLength` and later pushed by `cm_FSync`/`cm_StoreMini`. `cm_SetLength` holds `bufCreateLock` to prevent concurrent buffer creation while it truncates or extends, drops `scp->rw` around potentially blocking buffer truncation and quota checks, and sets scache masks that drive later storeback.

Bulk stat is driven by directory reads. `cm_TryBulkStat` builds a `cm_bulkStat_t`, scans only entries from the buffer page of interest, skips entries with useful cached callbacks, and calls `cm_TryBulkStatRPC` in AFSCBMAX-sized chunks. Inline bulk failures can be per-entry; non-inline bulk failures are treated as untrustworthy for all returned entries and collapse to `CM_ERROR_BULKSTAT_FAILURE`.

Byte-range lock acquisition first checks for conflicting accepted or lost locks in the in-memory queue. If compatible, it either reuses an existing sufficient server lock, waits behind an in-flight server-lock transition, obtains/upgrades a server lock, or falls back to client-only locks for read-only volumes or permission edge cases. Unlock removes matching lock records from the scache queue, adjusts accepted/client-only counters, marks records deleted for later global cleanup, and may downgrade or release the server lock in `cm_IntUnlock`. `cm_CheckLocks` periodically walks all locks, reclaims deleted records, extends active server locks once per scache per cycle, and marks active locks lost if extension/reacquisition cannot safely preserve the lock contract.

## State and Persistence Behavior

The primary persistent runtime state is in memory, not on disk:

- `cm_scache_t` holds fid identity, callback state, file type, length, deferred store masks, mount/symlink string cache, mount-root fid cache, lock queues, lock counters, server lock type, lock data version, active RPC counters, and prefetch state.
- Directory contents are cached in `cm_buf_t` buffers and optionally BPlus directory structures. Local directory updates are applied only when `cm_CheckDirOpForSingleChange` says the cached directory can be updated safely.
- DNLC entries are inserted for exact, callback-protected lookups and removed around create/delete/rename operations.
- Symlink and mount-point data are cached in `mountPointStringp` with `mpDataVersion == dataVersion`.
- File size/modtime/truncation changes can be deferred in scache masks and persisted to servers later via `cm_FSync` and `cm_StoreMini`.
- Lock state persists as process memory in `cm_file_lock_t` queues. It is periodically refreshed with server RPCs; lost locks remain until clients unlock them.

The file does not create repository artifacts or durable local databases. Durability is through AFS file-server RPCs and cache-manager in-memory state that reflects server callbacks/status.

## Dependencies and Integration Points

Major dependencies include:

- Windows headers and semantics: `windows.h`, `winsock2.h`, `FILE_GENERIC_*`, `FILE_SHARE_*`, `DELETE`, `LARGE_INTEGER`, and NT/SMB lock/open conventions.
- Cache-manager infrastructure from `afsd.h`, `smb.h`, `cm_btree.h`, buffer management (`buf_Get`, `cm_GetBuffer`, `buf_Truncate`, `buf_CleanVnode`), locks (`lock_ObtainWrite`, `cm_scacheLock`), DNLC (`cm_dnlcLookup`, `cm_dnlcEnter`, `cm_dnlcRemove`), directory ops (`cm_BeginDirOp`, `cm_DirLookup`, `cm_DirCreateEntry`, `cm_DirDeleteEntry`, BPlus variants), and status/callback helpers (`cm_SyncOp`, `cm_MergeStatus`, `cm_StartCallbackGrantingCall`, `cm_EndCallbackGrantingCall`).
- Cell and volume management (`cm_GetCell`, `cm_FindCellByID`, `cm_FindVolumeByName`, `cm_FindVolumeByID`, `cm_VolumeStateByType`, volume type constants).
- RPC layer (`cm_ConnFromFID`, `cm_GetRxConn`, `RXAFS_CreateFile`, `RemoveFile`, `RemoveDir`, `MakeDir`, `Rename`, `Link`, `Symlink`, `StoreStatus`, `BulkStatus`, `InlineBulkStatus`, `SetLock`, `ReleaseLock`, `ExtendLock`, `GetVolumeStatus`, `cm_Analyze`, `cm_MapRPCError*`).
- Optional features: `AFS_FREELANCE_CLIENT`, `USE_BPLUS`, server byte-range lock capabilities, write-lock ACL capability, aggressive/advisory lock build flags, debug refcount logging.
- Redirector integration through `RDR_InvalidateObject`, `RDR_Initialized`, DFS-link notification via `cm_VolStatus_Notify_DFS_Mapping`, and request fields such as `tidPathp` and `relPathp`.

## Risks and Edge Cases

- The file is highly concurrency-sensitive. Many functions intentionally release and reacquire `scp->rw`, buffer mutexes, and `cm_scacheLock`; ordering mistakes can deadlock or race with callback revocation, buffer storeback, or lock cleanup.
- `cm_ApplyDir` relies on AFS directory layout invariants and marks buffers bad on malformed entries. Any directory layout or encoding change must preserve these assumptions.
- Name handling crosses client strings, normalized strings, filesystem strings, short names, case-fold matching, `@sys`, `@vol:`, mount points, symlinks, DFS links, UNC paths, and freelance dynamic mounts. Bugs can produce wrong-object lookup, ambiguous filename handling errors, or symlink loops.
- Mount and symlink contents share `mountPointStringp`/`mpDataVersion`; callers must respect file type and locking expectations.
- Local directory cache updates are intentionally conservative. If `cm_CheckDirOpForSingleChange` logic or BPlus/legacy directory updates diverge, local cache can become stale or inconsistent until callback invalidation.
- Some code paths use RPC active counters and callback-granting calls manually; mismatched increment/decrement or missed `cm_EndCallbackGrantingCall` would leak in-flight state or corrupt callback accounting.
- Lock handling is particularly risk-heavy: server lock upgrades/downgrades release locks temporarily and depend on `dataVersion` checks. Permission fallbacks can create client-only locks, and lost-lock behavior intentionally returns hard errors to preserve data integrity.
- `cm_TryBulkStatRPC` must treat non-inline bulk failures as untrustworthy because classic bulk status does not identify which entry failed. Relaxing this can merge wrong or partial status.
- Memory allocation is generally assumed successful in older style code in some paths; allocation failures are not uniformly handled.

## Test Signals

Useful tests and runtime signals include:

- Path lookup: exact/case-fold/ambiguous names, 8.3 short-name lookups, `.`/`..`, missing intermediary versus missing final component, `@sys` expansion order, direct `@vol:` and `<cell>{%,#}<volume>` root references.
- Mount/symlink: normal/cellular mount points, `.readonly` and `.backup` selection, `cm_followBackupPath`, symlink relative and absolute targets, local UNC symlinks, DFS-link detection and notification, loop detection at `MAX_SYMLINK_COUNT` and `MAX_FID_COUNT`.
- Directory operations: create/mkdir/link/symlink/unlink/rmdir/rename with and without BPlus, same-directory and cross-directory rename, case-only rename, target exists, read-only volume, freelance root denial, local directory cache update after single expected change.
- Attribute and length: chmod/owner/group/modtime store, truncate shrink with dirty buffers, extend past quota threshold, deferred `cm_FSync`, overquota/out-of-space flag propagation.
- Open/delete: read/write/delete access calculation, share-lock conflict mapping to sharing violation, delete-on-close precheck for non-empty directories.
- Bulk status: inline-bulk supported and unsupported servers, per-entry access failures, volume-global failures, fallback after `CM_ERROR_BULKSTAT_FAILURE`.
- Locks: shared/exclusive overlap matrix, unlock by exact range and range match, wait/retry paths, client death timeout, read-only/client-only locks, lock upgrade/downgrade with data-version changes, periodic `cm_CheckLocks` extension and lost-lock marking.
- Logging assertions in this file are important test or diagnostic signals: invalid directory entries, fid mismatch in debug lock records, lock counter assertions, and RPC success/failure traces.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_vnodeops.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_vnodeops.h

## Purpose

`cm_vnodeops.h` declares the Windows cache-manager vnode-operation interface implemented mostly by `cm_vnodeops.c`. It exposes path lookup, directory traversal, mount/symlink handling, file and directory mutation, attribute changes, open/delete permission checks, byte-range locks, bulk status prefetch, and direct volume-reference support to the rest of the Windows AFS client.

This header is the contract between higher-level SMB/redirector/pioctl code and low-level vnode operations. It also defines the small request/operation structs needed by callers: attribute masks, lookup search state, lock-open data, and bulk-stat request storage.

## Important APIs, Types, and Functions

Global configuration/exported data:

- `cm_mountRootGen` tracks mount-root generation.
- `cm_enableServerLocks` controls whether cache-manager byte-range locks are asserted with AFS server locks.
- `cm_followBackupPath` controls backup-volume traversal behavior through mount points.
- `cm_foldUpper[]` is the 8-bit case-folding table used by `cm_stricmp`.

Types and constants:

- `cm_attr_t` carries optional attribute updates: client modification time, length, Unix mode bits, owner, and group.
- `CM_ATTRMASK_*` flags identify valid `cm_attr_t` fields.
- `cm_lookupSearch_t` is the directory lookup callback state: target fid, filesystem and normalized search names, match flags, case-fold flag, and tilde/short-name marker.
- `cm_DirFuncp_t` is the callback signature for `cm_ApplyDir`.
- `CM_PREFIX_VOL` and `CM_PREFIX_VOL_CCH` define the direct volume-reference syntax `@vol:<cell>{%,#}<volume>`.
- `MAX_FID_COUNT` limits fid expansion during path walks; `MAX_SYMLINK_COUNT` limits symlink traversal.
- `AFS_ACCESS_READ`, `AFS_ACCESS_WRITE`, and `AFS_ACCESS_EXECUTE` map Windows generic file rights into AFS open checks while excluding `SYNCHRONIZE` and selected attribute rights.
- `cm_lock_data_t` carries temporary share-lock data from `cm_CheckNTOpen` to `cm_CheckNTOpenDone`.
- `CM_UNLOCK_FLAG_BY_FID` and `CM_UNLOCK_FLAG_MATCH_RANGE` alter unlock-key matching behavior.
- `CM_SESSION_SMB`, `CM_SESSION_IFS`, `CM_SESSION_CMINT`, and `CM_SESSION_RESERVED` define lock-key session namespaces.
- `CM_BULKMAX` and `cm_bulkStat_t` define the maximum and storage layout for batched bulk-status calls.

Public functions are grouped around:

- Path and lookup: `cm_NameI`, `cm_Lookup`, `cm_LookupInternal`, `cm_EvaluateVolumeReference`, `cm_ExpandSysName`.
- Directory traversal and bulk status: `cm_ApplyDir`, `cm_TryBulkStat`, `cm_TryBulkStatRPC`.
- Mounts and symlinks: `cm_ReadMountPoint`, `cm_FollowMountPoint`, `cm_HandleLink`, `cm_AssembleLink`, `cm_EvaluateSymLink`.
- Mutations and attributes: `cm_SetAttr`, `cm_Create`, `cm_FSync`, `cm_StatusFromAttr`, `cm_Unlink`, `cm_MakeDir`, `cm_RemoveDir`, `cm_Rename`, `cm_Link`, `cm_SymLink`, `cm_IsSpaceAvailable`.
- Open/delete checks: `cm_Open`, `cm_CheckOpen`, `cm_CheckNTOpen`, `cm_CheckNTOpenDone`, `cm_CheckNTDelete`.
- Locks: `cm_Lock`, `cm_UnlockByKey`, `cm_Unlock`, `cm_LockCheckRead`, `cm_LockCheckWrite`, `cm_CheckLocks`, `cm_ReleaseAllLocks`, `cm_LockMarkSCacheLost`, `cm_RetryLock`, `cm_GenerateKey`, `cm_KeyEquals`.

`DEBUG_REFCOUNT` changes `cm_NameI` and `cm_Lookup` declarations into debug variants with file/line tracking macros.

## Control Flow

The header itself has no executable control flow, but it defines call sequencing contracts used by callers:

- Callers use `cm_NameI`/`cm_Lookup` to obtain held `cm_scache_t` pointers and must release them later.
- `cm_CheckNTOpen` may return a `cm_lock_data_t` through `ldpp`; callers must pass it to `cm_CheckNTOpenDone` so the temporary share lock is released and the scache sync state is completed.
- `cm_ApplyDir` invokes a caller-provided function while the directory buffer is locked but the directory scache is not locked.
- `cm_AssembleLink` returns an optional held new-root scache and allocated `cm_space_t`; callers must release/free them according to implementation rules.
- Lock functions assume the relevant scache lock state described in implementation comments; misuse can corrupt lock counters or queue state.

## State and Persistence Behavior

The header defines in-memory state structures rather than persistent storage. `cm_attr_t` is transient input for status/length changes. `cm_lookupSearch_t` is transient state for directory scanning and DNLC/BPlus lookup. `cm_lock_data_t` temporarily bridges NT open and open completion. `cm_bulkStat_t` stores one page-oriented batch of fids, statuses, and callbacks for immediate RPC processing.

No durable files or registry entries are managed here. Persistence of vnode changes occurs through implementation RPCs declared by this header.

## Dependencies and Integration Points

The header depends on cache-manager types such as `cm_scache_t`, `cm_user_t`, `cm_req_t`, `cm_fid_t`, `cm_key_t`, `cm_file_lock_t`, `cm_space_t`, directory entry types from `cm_dir.h`, AFS RPC structs such as `AFSStoreStatus`, `AFSFid`, `AFSFetchStatus`, and Windows rights/locking types such as `FILE_GENERIC_READ`, `LARGE_INTEGER`, and lock flags.

It is included by modules that need vnode operations: SMB request handlers, redirector integration, directory enumeration, pioctl helpers, volume status mapping, and cache-manager maintenance code. The `@vol:` and DFS/symlink declarations also tie it to volume and volume-status subsystems.

## Risks and Edge Cases

- Several APIs transfer ownership or hold references through output pointers. Callers must follow implementation-specific release rules.
- The `DEBUG_REFCOUNT` macro layer changes function names at compile time, so prototypes and callsites must stay consistent.
- The access-bit macros are Windows-specific and intentionally deviate from naive generic-right handling; changing them can break application compatibility.
- `CM_BULKMAX` depends on `AFSCBMAX` and directory-buffer assumptions; increasing it affects stack/heap use and RPC batching behavior.
- Lock-key equality can ignore `process_id` under `CM_UNLOCK_FLAG_BY_FID`; callers must use flags carefully to avoid releasing another owner’s locks.

## Test Signals

- Compile coverage with and without `DEBUG_REFCOUNT`, `USE_BPLUS`, `_WIN64`, and lock capability flags.
- API-level tests should verify temporary `cm_lock_data_t` cleanup, `cm_attr_t` mask conversion, `@vol:` parsing entry points, `@sys` expansion, and unlock flag behavior.
- Static analysis should check every function returning held scaches or allocated spaces has documented cleanup in callers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_vnodeops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_volstat.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_volstat.c

## Purpose

`cm_volstat.c` implements the Windows AFS cache-manager Volume Status Event Notification API. It dynamically loads an optional external volume-status handler DLL configured in the Windows registry, passes a bidirectional function table to that DLL, forwards service/network/volume/DFS-mapping events to it, and exposes callbacks that let the DLL map SMB/redirector paths back to AFS cell and volume IDs or DFS-link targets.

The file also bridges volume/network events to the native redirector (`RDR_*`) through an internal event queue and a delivery thread when redirector volume-status notifications are enabled.

## Important APIs, Types, and Functions

Global state:

- `hVolStatus` is the loaded handler DLL module handle. A non-NULL value means the external handler is active.
- `dll_funcs` stores callbacks supplied by the external DLL.
- `cm_funcs` stores cache-manager callbacks passed to the DLL.
- `volstat_NetbiosName` is read from registry and used to build UNC-style DFS mapping source paths.
- `RDR_Notifications` enables redirector notification forwarding.
- `rdr_evtH`/`rdr_evtT`, `rdr_q_event`, and `rdr_evt_lock` implement the redirector event queue.

Lifecycle and notification functions:

- `cm_VolStatus_SetRDRNotifications` toggles redirector notifications.
- `cm_VolStatus_Active` reports whether a handler DLL is loaded.
- `cm_VolStatus_Initialization` reads registry configuration, loads the handler DLL, resolves `VolStatus_Initialization`, initializes function tables, validates handler version, and starts redirector notification delivery if configured.
- `cm_VolStatus_Finalize` closes the redirector event handle and unloads the handler DLL.
- `cm_VolStatus_Service_Started`/`Service_Stopped` notify the DLL about AFS service lifecycle; service start also notifies network start if SMB networking is already active.
- `cm_VolStatus_Network_Started`/`Network_Stopped` notify both redirector queue and DLL of NetBIOS availability.
- `cm_VolStatus_Network_Addr_Change` reports IP address changes.
- `cm_VolStatus_Change_Notification` reports volume online/offline-like state changes to redirector and DLL.
- `cm_VolStatus_DeliverNotifications` is the long-running redirector queue consumer that calls `RDR_NetworkAddrChange`, `RDR_VolumeStatus`, or `RDR_NetworkStatus`.

Path and DFS functions:

- `cm_VolStatus_Notify_DFS_Mapping` informs version-2 DLL handlers about a DFS mapping for a scache, converting client paths to UTF-8 and normalizing slashes for UNC-style paths.
- `cm_VolStatus_Invalidate_DFS_Mapping` invalidates a previously reported DFS mapping by fid components.
- `cm_VolStatus_Path_To_ID` resolves a share/path into an scache via `cm_NameI`, fetches status/callback, returns cell and volume IDs, and optionally returns cached volume status.
- `cm_VolStatus_Path_To_DFSlink` resolves a share/path, verifies the target scache is a DFS link, and returns its mount-point string with size-query semantics.

## Control Flow

Initialization reads `AFSREG_CLT_SVC_PARAM_SUBKEY` under `HKEY_LOCAL_MACHINE`. If `VolStatusHandler` is configured, it optionally reads `NetbiosName`, loads the DLL path with `LoadLibrary`, resolves the decorated initialization export, fills `cm_funcs` with cache-manager path callbacks, sets `dll_funcs.version`, and calls into the DLL. Any missing export, non-zero initialization code, or version mismatch unloads the DLL and disables external notifications. It then separately reads `RDRVolStatNotify`; if the redirector is initialized and notifications are enabled, it initializes a mutex, starts `cm_VolStatus_DeliverNotifications`, and creates a manual-reset event named `rdr_q_event`.

Service/network/volume notification functions are no-op success paths when no DLL is loaded. When redirector forwarding is enabled, they allocate an `rdr_volstat_evt_t`, fill its event type/data, append it to the queue under `rdr_evt_lock`, and signal `rdr_q_event`. They then call the corresponding function pointer in `dll_funcs` if `hVolStatus` is active.

The path-to-ID and path-to-DFS-link callbacks convert incoming filesystem strings to client strings, initialize a root-user request, resolve the path relative to `cm_RootSCachep(cm_rootUserp, &req)` using case-fold and follow flags, obtain current status under the scache write lock with `cm_SyncOp`, and extract the requested information. Both free converted strings and release scaches before returning. `Path_To_DFSlink` supports a size query when `pBuffer == NULL`, checks buffer capacity when a buffer is supplied, and returns `CM_ERROR_TOOBIG` on insufficient capacity.

`cm_VolStatus_DeliverNotifications` waits forever on `rdr_q_event`, drains queued events from tail to head under `rdr_evt_lock`, releases the mutex while making redirector calls, frees each event, and reacquires the mutex to continue draining.

## State and Persistence Behavior

Persistent configuration comes from the Windows registry values `VolStatusHandler`, `NetbiosName`, and `RDRVolStatNotify`. Runtime state is process-local: the loaded module handle, function tables, NetBIOS name buffer, redirector notification flag, event queue, event handle, and mutex.

Path mapping state is not stored by this file. DFS mapping notifications are forwarded to an external DLL; invalidation is also delegated. Redirector events are transient heap allocations that are freed by the delivery thread.

## Dependencies and Integration Points

Key dependencies include:

- Windows APIs: registry (`RegOpenKeyEx`, `RegQueryValueEx`, `RegCloseKey`), dynamic loading (`LoadLibrary`, `GetProcAddress`, `FreeLibrary`), events (`CloseHandle`, `GetLastError`), WinSock/NetBIOS headers, and `HMODULE`.
- OpenAFS Windows cache-manager headers: `afsd.h`, `smb.h`, `afsreg.h`, string conversion helpers, request/scache/volume APIs, and logging.
- External handler ABI from `cm_volstat.h`: `dll_VolStatus_Funcs_t` and `cm_VolStatus_Funcs_t`.
- Redirector hooks declared as externs: `RDR_NetworkAddrChange`, `RDR_VolumeStatus`, `RDR_NetworkStatus`.
- Path lookup and DFS-link integration with `cm_NameI`, `cm_RootSCachep`, `cm_SyncOp`, `cm_GetVolumeByFID`, `cm_GetVolumeStatus`, and scache mount-point strings.

## Risks and Edge Cases

- Redirector event allocations are not checked for `malloc` failure before dereference.
- `cm_VolStatus_DeliverNotifications` runs forever and `Finalize` only closes the event handle; shutdown ordering must ensure the thread cannot use a closed handle or freed synchronization object.
- The event is created as manual-reset and initially signaled. The code drains the queue but does not reset the event in this file; behavior depends on the thread/event wrapper semantics and may spin if the event remains signaled.
- External DLL ABI relies on decorated export name `@VolStatus_Initialization@8` and exact version matching.
- Registry value sizes and string termination depend on registry data correctness. The fixed 64-byte NetBIOS buffer and 1024-byte DFS source buffer are potential truncation points.
- `cm_VolStatus_Notify_DFS_Mapping` uses `strncat(src, ..., sizeof(src))`, which is not the usual remaining-capacity pattern; while the fixed buffer limits writes, truncation behavior should be reviewed carefully.
- `Path_To_DFSlink` has error paths after status sync that jump to `done` without releasing the scache write lock and scache reference in the visible code. The `fileType != DFSLINK` and `TOOBIG` branches are especially important to audit or test for lock/reference leaks.
- Path resolution uses root user credentials and case-fold/follow behavior, so handler queries can see root-user access semantics rather than the original application user.

## Test Signals

- Initialization matrix: no registry key, handler path missing, DLL missing export, DLL returns failure, version mismatch, successful version-1 and version-2 handler.
- Service/network notifications with and without loaded DLL, and with `_WIN64` versus 32-bit signatures.
- Redirector queue tests for network up/down, address change, volume online/offline transitions, concurrent enqueue/drain, service shutdown, and memory cleanup.
- Path callbacks for invalid parameters, conversion failure, missing paths, successful file/dir paths, volume status known/unknown, DFS-link size query, exact-size buffer, too-small buffer, and non-DFS-link target.
- DFS mapping tests for slash normalization, trailing/leading slash joins, UTF-8 conversion, version-1 handler no-op, and invalidation by fid.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_volstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_volstat.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_volstat.h

## Purpose

`cm_volstat.h` defines the public/private ABI for OpenAFS Windows cache-manager volume-status notifications. It declares cache-manager entry points for service, network, volume, DFS mapping, path-to-volume, path-to-DFS-link, redirector delivery, and redirector notification toggling. It also defines the function-table ABI exchanged with optional external volume-status handler DLLs.

The header is the shared contract for `cm_volstat.c`, handler DLLs, pioctl test structures, and redirector volume-status event integration.

## Important APIs, Types, and Functions

Core status type:

- `enum volstatus` describes volume state as `vl_online`, `vl_busy`, `vl_offline`, `vl_alldown`, or `vl_unknown`.

Cache-manager functions:

- `cm_VolStatus_Initialization` and `cm_VolStatus_Finalize` load/unload handler state.
- `cm_VolStatus_Service_Started` and `cm_VolStatus_Service_Stopped` report service lifecycle.
- `cm_VolStatus_Network_Started` and `cm_VolStatus_Network_Stopped` have architecture-dependent signatures: two NetBIOS names on `_WIN64`, one on 32-bit builds.
- `cm_VolStatus_Network_Addr_Change` reports address list changes.
- `cm_VolStatus_Change_Notification` reports cell/volume status updates.
- `cm_VolStatus_Path_To_ID` maps share/path strings to cell ID, volume ID, and volume status.
- `cm_VolStatus_Path_To_DFSlink` maps share/path strings to DFS-link target data.
- `cm_VolStatus_Notify_DFS_Mapping` and `cm_VolStatus_Invalidate_DFS_Mapping` notify or invalidate DFS mappings by scache/path.
- `cm_VolStatus_DeliverNotifications` is the redirector event delivery thread routine.
- `cm_VolStatus_SetRDRNotifications` toggles redirector forwarding.

DLL ABI:

- `DLL_VOLSTATUS_FUNCS_VERSION` is `2`.
- `dll_VolStatus_Funcs_t` contains handler-supplied callbacks for service, network, address-change, volume-state, DFS mapping notify, and DFS mapping invalidate. Version 2 adds DFS mapping functions.
- `CM_VOLSTATUS_FUNCS_VERSION` is `1`.
- `cm_VolStatus_Funcs_t` contains cache-manager callbacks the DLL can call: path-to-ID and path-to-DFS-link.

Test and redirector structures:

- `struct VolStatTest` carries pioctl test flags, fid, cell name, volume name, and state.
- `VOLSTAT_TEST_*` flags request server apply, volume check, network up, or network down behavior.
- `enum rdr_event_type` distinguishes redirector address-change, volume-status, and network-status events.
- `rdr_volstat_evt_t` is a queue element with event type and union payload for volume online state or network status.

## Control Flow

The header defines an ABI flow rather than implementing behavior. During initialization, `cm_volstat.c` passes a `dll_VolStatus_Funcs_t` to the external DLL to be populated and a `cm_VolStatus_Funcs_t` containing callable cache-manager path helpers. Later, cache-manager events call the populated `dll_funcs` entries, while the DLL can call back into `cm_VolStatus_Path_To_ID` or `cm_VolStatus_Path_To_DFSlink`.

Redirector notification control uses `cm_VolStatus_SetRDRNotifications` to enable queueing of `rdr_volstat_evt_t` objects, then `cm_VolStatus_DeliverNotifications` consumes those objects asynchronously.

## State and Persistence Behavior

The header’s structs are runtime ABI data. `VolStatTest` is request/test payload state. `rdr_volstat_evt_t` is transient queued event state. Persistent configuration for enabling handlers or redirector forwarding is outside this header and is read by `cm_volstat.c` from the Windows registry.

No on-disk repository or cache data is declared here.

## Dependencies and Integration Points

This header depends on OpenAFS types (`afs_uint32`, `cm_fid_t`, `cm_scache_t`, `clientchar_t`, `osi_queue_t`), Windows types (`DWORD`, `ULONG`, `BOOLEAN`), and constants such as `CELL_MAXNAMELEN` and `VL_MAXNAMELEN`.

Integration points include:

- External volume-status handler DLLs that must honor `dll_VolStatus_Funcs_t` versioning and calling convention.
- Cache-manager path resolution via `cm_VolStatus_Funcs_t`.
- Redirector event delivery through `rdr_volstat_evt_t`.
- Pioctl or diagnostic code using `VolStatTest` and `VOLSTAT_TEST_*`.

## Risks and Edge Cases

- The architecture-dependent network-start/stop prototypes require matching caller and implementation signatures across 32-bit and 64-bit builds.
- Function-table versioning must remain backward-compatible; adding fields without version bumps can break handler DLLs.
- The `__fastcall` calling convention is part of the ABI and must match external DLL expectations.
- `rdr_volstat_evt_t` uses an anonymous union-style layout; compiler compatibility and C mode assumptions matter.
- The header does not declare `cm_VolStatus_Active`, although `cm_volstat.c` defines it. Callers needing that function rely on another declaration or implicit knowledge.

## Test Signals

- Compile tests for `_WIN64` and non-`_WIN64` prototypes.
- ABI tests that a handler compiled against the header receives the expected version and function pointer layout.
- Unit or integration tests for `VolStatTest` flag handling in pioctl code.
- Redirector queue tests should validate `rdr_volstat_evt_t` layout for address-change, volume-status, and network-status payloads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_volstat.h -->
