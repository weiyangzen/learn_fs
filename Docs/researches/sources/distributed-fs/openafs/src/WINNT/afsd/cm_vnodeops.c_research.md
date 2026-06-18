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
