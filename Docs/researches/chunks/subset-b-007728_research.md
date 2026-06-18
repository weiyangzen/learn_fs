# `sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRFunction.c` lines 1-6595

## Purpose

This chunk is the user-mode bridge between the Windows AFS redirector driver and the OpenAFS cache manager/service. It converts redirector request structures into cache-manager operations, maps cache-manager errors back to NT status values, packages result buffers for the kernel redirector, and manages the shared cache extent handoff between user-mode cache buffers and the file system driver.

The covered lines include initialization data returned to the redirector, FID conversion helpers, authentication-group-to-user lookup, directory enumeration, file lookup by name/FID, create/update/cleanup/delete/rename/hard-link/symlink/flush/open/share-access operations, extent fetch/release plumbing, pioctl and pipe wrappers, byte-range locking, volume information queries, and redirector-held FID tracking. The chunk ends inside the comment prologue for `RDR_PipeTransceive`; its implementation, plus `RDR_ReadFile` and `RDR_WriteFile`, continue in the next chunk.

## Important APIs, Types, And Functions

- Basic request and identity helpers:
  - `RDR_InitReq` initializes `cm_req_t` and stamps redirector-origin and WOW64 flags.
  - `RDR_fid2FID` and `RDR_FID2fid` copy between cache-manager `cm_fid_t` and redirector `AFSFileID`.
  - `RDR_ExtAttributes` derives Windows/SMB attributes from `cm_scache_t` type bits, vnode parity, symlink/mount/DFS state, and Unix write permissions.
  - `RDR_GetLocalSystemUser`, `RDR_UserFromCommRequest`, `RDR_UserFromAuthGroup`, and `RDR_ReleaseUser` map kernel auth groups or LocalSystem to `cm_user_t` references through `smb_username_t`.

- Redirector initialization:
  - `RDR_SetInitParams` builds an `AFSRedirectorInitInfo` blob for the kernel, including cache location, dump/temp path, root FID, cache block/chunk sizing, name-array limits, reparse policy, short-name/dot-file/direct-I/O flags, and either memory-cache extents or cache-file path.
  - `RDR_extentBaseAddress` is set here and later used to translate `cm_buf_t->datap` pointers to redirector cache offsets.

- Directory and metadata response packing:
  - `RDR_BulkStatLookup` uses `cm_BeginDirOp`, `cm_BPlusDirEnumerate`, and `cm_BPlusDirEnumBulkStatOne` to refresh one entry with nearby directory status.
  - `RDR_PopulateCurrentEntry` fills an `AFSDirEnumEntry` from an existing `cm_scache_t`, optionally fetching status, bulk-statting, following mount points, evaluating symlinks/DFS links, generating target names, and faking metadata if callbacks/access are unavailable.
  - `RDR_PopulateCurrentEntryNoScp` creates a minimal placeholder entry when enumeration has a FID/error but no scache object.
  - `RDR_EnumerateDirectory` drives initial or continued `cm_direnum_t` enumerations and returns packed `AFSDirEnumResp` entries plus an enumeration handle.

- Name/FID lookup and create/update/delete flows:
  - `RDR_EvaluateNodeByName` validates the parent directory, runs `cm_Lookup` with optional case-folding, handles root volume references and Freelance root cell fallback, generates short names, and returns an `AFSFileEvalResultCB`.
  - `RDR_EvaluateNodeByID` resolves a source FID and parent directory, then returns the current entry by FID.
  - `RDR_CreateFileEntry`, `RDR_UpdateFileEntry`, `RDR_CleanupFileEntry`, `RDR_DeleteFileEntry`, `RDR_RenameFileEntry`, `RDR_HardLinkFileEntry`, and `RDR_CreateSymlinkEntry` wrap the corresponding cache-manager create, attribute, cleanup, unlink/rmdir, rename, link, and symlink operations.
  - `RDR_FlushFileEntry` validates a file scache and calls `cm_FSync`.

- Open/share access and locks:
  - `RDR_CheckAccess` maps requested NT access bits to AFS ACL bits, fetches access rights if needed, and maps granted AFS rights back to NT access bits.
  - `RDR_OpenFileEntry` runs `cm_CheckNTOpen`, skips the open check for LocalSystem, then optionally installs a synthetic byte-range share lock when write sharing is denied.
  - `RDR_ReleaseFileAccess` releases that synthetic share lock.
  - `RDR_ByteRangeLockSync`, `RDR_ByteRangeUnlock`, and `RDR_ByteRangeUnlockAll` translate redirector byte-range lock batches into `cm_Lock`, `cm_Unlock`, and `cm_UnlockByKey` calls keyed by process ID.

- Extent/cache handoff:
  - `RDR_BkgFetch` is the background fetch worker that obtains buffers, fills them from AFS, queues clean buffers on the redirector queue, sends `AFSSetFileExtentsCB` records with cache offsets, and reports fatal status through `RDR_SetFileStatus`.
  - `RDR_RequestFileExtentsAsync` tries to satisfy a requested byte range immediately from existing clean buffers, zero-fills EOF/clean extents where appropriate, queues missing ranges to `RDR_BkgFetch`, and returns any immediately available extents.
  - `RDR_ReleaseFileExtents` accepts extents back from the redirector, updates length, removes released buffers from the redirector queue, detects dirty extents, and queues background stores.
  - `RDR_ProcessReleaseFileExtentsResult` performs the same release/dirty/store logic for batched result callbacks containing multiple files/auth groups.
  - `RDR_ReleaseFailedSetFileExtents` unwinds buffers already handed to the redirector when a set-extents response failed.
  - `HexCheckSum` is a debug helper for optional MD5 checksum validation.

- Pioctl, pipe, and volume wrappers:
  - `RDR_PioctlOpen`, `RDR_PioctlClose`, `RDR_PioctlWrite`, and `RDR_PioctlRead` register pioctl request IDs and proxy mapped-buffer reads/writes through `RDR_Ioctl*`.
  - `RDR_PipeOpen`, `RDR_PipeClose`, `RDR_PipeWrite`, `RDR_PipeRead`, `RDR_PipeSetInfo`, and `RDR_PipeQueryInfo` proxy named-pipe request IDs through `RDR_Pipe_*` helpers. Static UUID/name constants define the supported SRVSVC, WKSSVC, and NDR assumptions.
  - `RDR_GetVolumeInfo` and `RDR_GetVolumeSizeInfo` fetch volume quota/status via volume cache and `RXAFS_GetVolumeStatus`, with special handling for the Freelance local root and cached read-only volume size.
  - `RDR_HoldFid` and `RDR_ReleaseFid` toggle `CM_SCACHEFLAG_RDR_IN_USE` for scache entries the redirector wants pinned.

## Control Flow And State Behavior

Most public functions follow the same service-call shape: allocate an `AFSCommResult`, initialize a `cm_req_t`, convert incoming `AFSFileID` structures to `cm_fid_t`, obtain one or more `cm_scache_t` references, synchronize state/callbacks with `cm_SyncOp`, perform the operation, populate a redirector result structure, map cache-manager errors through `cm_MapRPCError` and `smb_MapNTError`, and release scache/user references before returning.

Directory operations are callback-sensitive. `RDR_PopulateCurrentEntry` tries to avoid per-entry server round trips by bulk-statting a directory when the scache lacks a callback. If access is cached as denied or status still cannot be obtained, it returns fake-but-stable metadata so the kernel can continue path processing with an NT error status embedded in the entry. Reparse target fields are filled only after status is valid and link/mount content has been read.

Create, update, cleanup, and delete operations separate length changes from other attribute updates. Both update and cleanup first set length alone when needed, then set Unix write-bit/read-only and client modification time attributes. Cleanup also clears `CM_SCACHEFLAG_RDR_IN_USE` on last handle, releases redirector-held extents, flushes dirty file data when appropriate, releases synthetic share locks and byte-range locks, and optionally deletes the object after locks have been dropped.

Rename and hard-link paths validate both source and target parent directories before mutating directory entries. Rename performs `cm_Rename`, then looks up the new target and returns a freshly populated entry. Hard-link supports Windows `ReplaceIfExists` behavior by checking/removing an existing target before `cm_Link`, while relying on `cm_Link` to reject unsupported cross-directory AFS hard links.

Symlink creation is a two-step adaptation for Windows reparse behavior. The redirector has already created a temporary object, so `RDR_CreateSymlinkEntry` removes that object, converts the Windows target path into AFS symlink or DFS-link syntax, calls `cm_SymLink`, emits change notification when watched, and returns the new symlink entry.

Extent handling is a queue-based ownership protocol around `cm_buf_t`. Buffers handed to the redirector are marked with `CM_BUF_QREDIR` and have cache offsets computed relative to `RDR_extentBaseAddress`. Immediate extent requests return clean buffers already available in the user-mode cache; missing or busy ranges are queued to `RDR_BkgFetch`. Release paths always attempt to take buffers back even when the file is deleted or scache lookup fails, then mark dirty ranges and queue contiguous background stores up to `cm_chunkSize`.

## State And Persistence Behavior

- Persistent file-system state is changed through cache-manager/server calls such as `cm_Create`, `cm_MakeDir`, `cm_SetAttr`, `cm_RemoveDir`, `cm_Unlink`, `cm_Rename`, `cm_Link`, `cm_SymLink`, `cm_FSync`, `cm_BkgStore`, and `RXAFS_GetVolumeStatus`.
- In-memory redirector/cache state includes `CM_SCACHEFLAG_RDR_IN_USE`, scache callback/data-version fields, directory enumeration handles, synthetic share locks, byte-range locks, and `CM_BUF_QREDIR` queue membership.
- `RDR_SetInitParams` chooses whether the redirector sees a memory extent interface or cache-file path based on physical-memory sizing, `cm_virtualCache`, and `cm_data.bufferSize`; this choice affects all later cache-offset calculations.
- Volume-size data for read-only volumes can be cached in `cm_volume_t` via `CM_VOLUMEFLAG_RO_SIZE_VALID`.
- Pioctl and pipe request IDs persist across open/write/read/close calls in helper-owned indexes created by `RDR_SetupIoctl` and `RDR_SetupPipe`.

## Dependencies And Integration Points

- Windows/user-mode APIs: `GetFullPathNameA`, `ExpandEnvironmentStringsA`, `GlobalMemoryStatusEx`, `GetComputerNameW`, RPC UUID string conversion, `StringCch*`/`StringCb*`, `FILE_ATTRIBUTE_*`, NT status values, and file-system access/share constants.
- OpenAFS cache manager APIs: scache lookup/reference, directory B+ tree enumeration, ACL/right checks, sync operations, create/remove/link/symlink/rename/setattr/fsync, buffer cache operations, background fetch/store queues, volume lookup, connection analysis, and RXAFS volume status calls.
- SMB/user abstractions: `smb_username_t`, `smb_FindUserByName`, `smb_MapNTError`, `smb_NotifyChange`, Unix-mode defaults, short-name generation, and synthetic lock key conventions.
- Redirector IPC/contracts: `AFSCommResult`, `AFSRedirectorInitInfo`, `AFSDirEnumEntry`, `AFSFile*CB` request/result structures, `AFSFileExtentCB`, pioctl/pipe callbacks, `RDR_SetFileExtents`, `RDR_SetFileStatus`, `RDR_RequestExtentRelease`, `RDR_Ioctl*`, and `RDR_Pipe_*`.
- Global configuration/state: `cm_data`, `cm_CachePath`, `cm_NetbiosName`, `cm_rootUserp`, `cm_shortNames`, `cm_directIO`, `cm_virtualCache`, `cm_volumeInfoReadOnlyFlag`, `cm_chunkSize`, `rdr_ReparsePointPolicy`, and `afsd_logp`.

## Risks And Edge Cases

- Several early allocation or lookup error paths return without releasing objects already acquired in nearby branches, so reference and result-buffer ownership should be audited with leak instrumentation.
- `RDR_PopulateCurrentEntry` requires enough space for a worst-case entry before calculating the exact packed length. Callers must pass realistic `ResultBufferLength`, and tests should cover boundary-sized buffers and `CM_ERROR_TOOBIG`.
- The `RDR_PopulateCurrentEntryNoScp` branch places `EaSize = 0` inside the non-directory `else` block, leaving the directory placeholder path without the explicit assignment visible in the file.
- `RDR_EvaluateNodeByID` releases `dscp` and then reads `dscp->dataVersion` when populating `ParentDataVersion`; that is a suspicious use-after-release pattern in this chunk.
- `RDR_OpenFileEntry` obtains a LocalSystem user reference and compares pointer identity with `userp`. Correctness depends on stable user object interning for LocalSystem.
- Extent release uses both file offsets and cache offsets to verify buffer identity. Stale redirector reports, recycled buffers, or mismatched `RDR_extentBaseAddress` can leave buffers queued or cause dirty data to be missed; the code logs these cases but often continues.
- Dirty extent detection is weaker when `VALIDATE_CHECK_SUM` is disabled; it trusts the dirty flags and dirty ranges supplied by the redirector.
- `RDR_RequestFileExtentsAsync` returns `FALSE` even after filling immediate extents, so callers must interpret the output buffer/extent count according to this API's convention rather than a simple Boolean success.
- The path conversion in `RDR_CreateSymlinkEntry` assumes specific `\??\UNC\...` and `\??\<drive>:` prefixes and uses fixed offsets; malformed absolute paths could be converted incorrectly.
- Several functions use fixed `WCHAR FileName[260]` buffers with counted input. Long component names must be validated before reaching these copies, or truncation/failure behavior depends on `StringCchCopyNW`.
- `RDR_ReleaseFileAccess` allocates a result but returns early for `AFS_FILE_ACCESS_NOLOCK` without setting an explicit success status beyond the zeroed buffer.
- This chunk stops before `RDR_PipeTransceive` logic, so MSRPC pipe transaction handling must be researched in the next chunk before drawing whole-file conclusions.

## Test Signals

- Initialization: run redirector startup with memory cache, virtual cache, and file cache modes; verify `AFSRedirectorInitInfo` lengths, offsets, flags, cache path/temp path conversion, and `RDR_extentBaseAddress`.
- Directory enumeration: test first and continued enumeration handles, zero-length bulk-stat calls, small result buffers, denied entries, missing callbacks, short-name generation, symlink/DFS target reporting, and skipped `.`/`..`.
- Lookup/evaluation: cover case-sensitive and case-folded lookup, root volume reference syntax, Freelance root cell fallback, `bNoFollow`, `bHoldFid`, invalid parent FIDs, and non-directory parents.
- Mutation: exercise create file/dir, update length/read-only/time, cleanup last-handle with dirty extents, delete check-only versus real delete, rename across parents, hard-link replacement, symlink conversion for relative, AFS UNC, non-AFS UNC, and local-drive targets.
- Open/locking: verify LocalSystem open bypass, `cm_CheckNTOpen` retry behavior, share-lock installation/release, byte-range batch lock statuses, exact-range unlock, and unlock-all-by-process.
- Extents: test immediate clean extent return, background fetch queueing, EOF zero-fill, clean-write allocation, dirty release, flush release, unknown/in-use extents, failed set-extents unwind, deleted-file release, checksum-enabled and checksum-disabled builds, and contiguous background store coalescing.
- Volume info: test Freelance root, RW/RO/BACK volumes, cached RO size, quota versus partition free space, `RXAFS_GetVolumeStatus` failure fallback, read-only volume flags, and label/cell UTF-16 lengths.
- Pioctl/pipe wrappers: open/write/read/close pioctl and pipe request IDs, LocalSystem pioctl read flagging, pipe info query/set, and buffer-size failure paths.
