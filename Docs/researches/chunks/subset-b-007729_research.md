# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRFunction.c lines 6596-6954

## Purpose

This chunk closes `RDR_PipeTransceive` and implements the user-mode redirector handlers for file reads and writes. These handlers are reached from `RDRInit.cpp` request dispatch for `AFS_REQUEST_TYPE_PIPE_TRANSCEIVE`, `AFS_REQUEST_TYPE_PROCESS_READ_FILE`, and `AFS_REQUEST_TYPE_PROCESS_WRITE_FILE`. The read/write paths translate a kernel-supplied `AFSFileID` into a cache-manager `cm_scache_t`, verify access and object type, perform either cache-backed or cache-bypassing I/O, then return an `AFSCommResult` containing an `AFSFileIOResultCB`.

## Important APIs, Types, and Functions

- `RDR_PipeTransceive(...)` writes an incoming pipe RPC payload with `RDR_Pipe_Write`, then reads the reply with `RDR_Pipe_Read`. The comments explain that the redirector is emulating LAN Manager pipe services for WKSSVC/SRVSVC calls such as share/server/workstation queries.
- `RDR_ReadFile(...)` handles mapped-buffer file reads. Inputs include `AFSFileID`, `LARGE_INTEGER *Offset`, byte count, mapped kernel I/O buffer, WOW64 flag, cache-bypass flag, result capacity, and result out pointer.
- `RDR_WriteFile(...)` handles mapped-buffer file writes. It additionally receives `AFSFileIOCB`, using `EndOfFile` to reconcile length before writing.
- `AFSCommResult` is the common service-to-redirector envelope with `ResultStatus`, `ResultBufferLength`, and flexible `ResultData`.
- `AFSFileIOCB` carries `IOOffset`, `IOLength`, `MappedIOBuffer`, timestamp fields, and `EndOfFile`.
- `AFSFileIOResultCB` returns `Length`, `DataVersion`, and callback `Expiration`.
- `cm_GetSCache`, `cm_SyncOp`, `cm_SyncOpDone`, `cm_ReleaseSCache`, and `lock_ObtainWrite`/`lock_ReleaseWrite` are the cache-manager synchronization and lifetime primitives around `cm_scache_t`.
- `raw_ReadData` / `raw_WriteData` use the AFS cache buffers; `cm_GetData` / `cm_DirectWrite` bypass those cache buffers for direct server I/O or queued direct write.
- `smb_MapNTError(cm_MapRPCError(...))` translates AFS/cache-manager failures to NTSTATUS values returned in the result block.

## Control Flow

`RDR_PipeTransceive` allocates a result buffer sized as `sizeof(AFSCommResult) + ResultBufferLength`, initializes an `cm_req_t`, writes the incoming pipe data by request id and buffer length, then reads the response into `ResultData`. Either pipe phase maps nonzero errors into `ResultStatus`; success sets status to zero and leaves the pipe read to set `ResultBufferLength`.

`RDR_ReadFile` first allocates enough response space for `AFSFileIOResultCB`, returning `STATUS_BUFFER_OVERFLOW` if the redirector-provided result capacity is too small. It rejects a null mapped I/O buffer and a zero cell id. For valid file ids it copies the wire `AFSFileID` fields into `cm_fid_t`, obtains the scache, takes `scp->rw` exclusively, and calls `cm_SyncOp` with `PRSFS_READ` plus `CM_SCACHESYNC_NEEDCALLBACK | CM_SCACHESYNC_GETSTATUS`. Once callback/status is acquired, directories return `STATUS_FILE_IS_A_DIRECTORY`, non-file objects such as mount points or symlinks return `STATUS_REPARSE_POINT_NOT_RESOLVED`, and regular files are read through `cm_GetData` when `bCacheBypass` is true or `raw_ReadData` otherwise. Success returns bytes read, `scp->dataVersion`, and `scp->cbExpires`; all terminal paths after scache acquisition release the lock and scache reference.

`RDR_WriteFile` mirrors the setup and validation flow but requests `PRSFS_WRITE | PRSFS_LOCK` so the write is not blocked solely by Unix-mode readonly attributes after Windows has already accepted cached data. If that fails with `CM_ERROR_NOACCESS` and the scache creator is the same user, it retries with `PRSFS_INSERT`, allowing creator insertion semantics. It then rejects directories and non-file objects as above. Before copying data, it compares `FileIOCB->EndOfFile` against `scp->length`; on mismatch it builds a `cm_attr_t` length update and calls `cm_SetAttr` with the scache lock temporarily released. The return code is intentionally reset to zero afterward, so length-set failures are logged but not directly returned. The write length is then clipped so no bytes beyond the current scache EOF are written; if the offset is already beyond EOF, the call returns success without reporting written bytes. The actual write goes through `cm_DirectWrite(..., CM_DIRECT_SCP_LOCKED, ...)` for cache bypass, or `raw_WriteData` for cache-backed writes. Success returns bytes written, data version, and callback expiration.

## State and Persistence Behavior

The persistent object identity is the AFS FID copied from `AFSFileID` into `cm_fid_t`; all file state is mediated through the referenced `cm_scache_t`. The chunk reads and mutates scache state under `scp->rw`, including file type, length, data version, and callback expiration. `cm_SyncOp` with `GETSTATUS` refreshes status, and `NEEDCALLBACK` ensures a callback lease before I/O proceeds. `raw_WriteData` may update cached buffers and scache length/dirty state; `cm_DirectWrite` queues a background direct write after copying the caller buffer into its own allocation and reports the full length as written. The returned `DataVersion` and `Expiration` let the kernel redirector correlate file cache state with the user-mode cache manager's view.

The write EOF adjustment is stateful and subtle: `cm_SetAttr` can change server/cache length before the data write, but this handler ignores that call's failure and rechecks/clips against whatever `scp->length` is afterward. That makes the final bytes-written result dependent on post-attribute scache state, not simply the requested `EndOfFile`.

## Dependencies and Integration Points

- Dispatch integration is in `RDRInit.cpp`: pipe transceive passes `AFSPipeIORequestCB` plus inline pipe data; read/write pass `AFSFileIOCB->IOOffset`, `IOLength`, and `MappedIOBuffer`, plus the global `bCacheBypass` decision.
- The wire/control structures come from `AFSUserStructs.h`, especially `AFSCommRequest`, `AFSCommResult`, `AFSFileID`, `AFSFileIOCB`, and `AFSFileIOResultCB`.
- Cache-manager dependencies are in the WINNT `afsd` layer: scache lookup/status/access, raw cached I/O, direct server I/O, attribute setting, and AFS-to-NT error mapping.
- Locking assumes `raw_ReadData`, `raw_WriteData`, `cm_GetData`, and `cm_DirectWrite(... CM_DIRECT_SCP_LOCKED ...)` are called with `scp->rw` held and will preserve or restore the expected lock state on return.
- Logging uses `afsd_logp` with function-specific messages that are useful test or diagnostic signals, but the unconditional "cm_SetAttr failure" log in the write EOF path should be interpreted with the actual code value.

## Risks and Edge Cases

- Both read and write allocate `Length + sizeof(AFSCommResult)` but zero only `Length`, leaving part of the envelope allocation not explicitly cleared in this chunk. Fields that are not assigned before return may rely on caller-side initialization conventions or may contain allocator residue.
- `RDR_WriteFile` dereferences `FileIOCB` without a null check; dispatch normally supplies it from the request payload, so malformed request construction would be the risk surface.
- EOF reconciliation ignores `cm_SetAttr` failures. This can hide quota, permission, network, or server-side length-update failures until the subsequent write or until the caller observes length/data-version state.
- Writes past EOF are silently trimmed or treated as success with no write when `Offset > scp->length`. This is consistent with the comment about discarding data beyond EOF, but tests need to distinguish accepted-zero-byte writes from actual extension writes.
- `cm_DirectWrite` queues asynchronous direct write work and reports the requested length as written, so success from this handler may precede actual server persistence.
- The access check deliberately uses `PRSFS_WRITE | PRSFS_LOCK` rather than Unix mode attributes; behavior differs from earlier open-time readonly checks and is meant to avoid denying data already accepted by the Windows cache.
- Non-regular file FIDs return `STATUS_FILE_IS_A_DIRECTORY` for directories and `STATUS_REPARSE_POINT_NOT_RESOLVED` for mount points/symlinks/other non-file scache types.

## Test Signals

- Read success should return `STATUS_SUCCESS`, `AFSFileIOResultCB.Length == bytes read`, and matching `DataVersion`/`Expiration` from the scache.
- Write success should return `STATUS_SUCCESS`, `Length == bytes written`, and updated scache freshness fields; cache-bypass writes may report success before background direct write completion.
- Small result buffers must produce `STATUS_BUFFER_OVERFLOW` with only an `AFSCommResult` envelope.
- Null mapped I/O buffers must produce `STATUS_INVALID_PARAMETER`.
- Zero-cell file ids must produce `STATUS_OBJECT_NAME_INVALID`.
- Directory FIDs must produce `STATUS_FILE_IS_A_DIRECTORY`; symlink or mount-point FIDs must produce `STATUS_REPARSE_POINT_NOT_RESOLVED`.
- Permission failures from `cm_SyncOp` should map through `cm_MapRPCError`/`smb_MapNTError`; for writes, include coverage for the creator fallback from `PRSFS_WRITE | PRSFS_LOCK` to `PRSFS_INSERT`.
- EOF-sensitive write tests should cover `EndOfFile` mismatch, offset equal to EOF, offset beyond EOF, and buffers whose requested range extends beyond current scache length.
- Pipe transceive tests should assert that write failure stops before read, read failure maps status, and successful transceive returns pipe output length from `RDR_Pipe_Read`.
