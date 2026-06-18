# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSLockControl.cpp

## Purpose

`AFSLockControl.cpp` implements `IRP_MJ_LOCK_CONTROL` for byte-range locks. It validates target FCBs, coordinates lock/unlock operations with the OpenAFS service, flushes cached data before unlock release, and then delegates local lock processing to the Windows FsRtl lock package.

## Important APIs, types, and functions

`AFSLockControl(PDEVICE_OBJECT, PIRP)` uses `AFSFcb` from `FileObject->FsContext` and `AFSCcb` from `FsContext2`. Service protocol blocks include `AFSByteRangeLockRequestCB`, `AFSByteRangeLockResultCB`, `AFSByteRangeUnlockRequestCB`, and `AFSByteRangeUnlockResultCB`. It sends synchronous `AFSProcessRequest` calls for byte-range lock, unlock-all, and unlock-single request types. Local processing uses `FsRtlProcessFileLock`, while unlock paths flush through `CcFlushCache`.

## Control flow

The function obtains the IRP stack, extracts FCB/CCB, rejects null FCBs, acquires the main FCB resource shared, and rejects IOCTL, special-share, and invalid FCB node types. For `IRP_MN_LOCK`, it sends a one-entry exclusive lock request with current process id, byte offset, length, auth group, file name, file id, and volume cell identity. If the service denies the lock, the IRP is completed with that status.

For `IRP_MN_UNLOCK_ALL` and `IRP_MN_UNLOCK_ALL_BY_KEY`, it acquires the section-object resource shared, flushes the whole file, releases the resource, builds an unlock-all request for the current process id, and sends it to the service. For `IRP_MN_UNLOCK_SINGLE`, it flushes the requested byte range, then sends a one-entry exclusive unlock request. After service-side work, the code sets `bCompleteRequest = FALSE` and calls `FsRtlProcessFileLock`, which owns IRP completion.

## State and persistence behavior

Local byte-range state lives in `pFcb->Specific.File.FileLock`. Server-side state is managed through synchronous service requests keyed by process id and file identity. Unlocks flush cache-manager state before release. The file does not persist data directly, but it governs ongoing access semantics and server lock consistency.

## Dependencies and integration points

This dispatch is registered in `AFSInit.cpp`. It bridges Windows lock IRPs, OpenAFS FCB/CCB structures, service request protocol, cache-manager flushing, ERESOURCE synchronization, volume cell metadata, auth groups, and `FsRtlProcessFileLock`.

## Risks and test signals

Unlock-all-by-key is treated like unlock-all and does not send the key to the service. All service lock requests use exclusive lock type, so shared lock intent is not represented here. Single-range flush passes `Length->LowPart`, which cannot represent ranges above 4 GiB. Flush errors are logged but the path may continue into service unlock and FsRtl processing. Tests should verify service request contents, invalid FCB rejection, lock denial completion, unlock flush behavior, key semantics, large range handling, local/server lock consistency, and exception handling around `CcFlushCache`.
