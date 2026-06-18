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
