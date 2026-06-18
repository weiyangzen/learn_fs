# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSFlushBuffers.cpp

## Purpose
Implements the Windows redirector flush-buffer dispatch path for OpenAFS file objects. The handler flushes dirty cached file data through the Windows cache manager and, when the redirector is not in direct-service-I/O mode, asks the OpenAFS extent layer/service path to push modified extents to the remote AFS server.

## Important APIs, Types, and Functions
The file exports `AFSFlushBuffers(PDEVICE_OBJECT LibDeviceObject, PIRP Irp)`. It uses `AFSRDRDeviceObject->DeviceExtension` as `AFSDeviceExt`, pulls `AFSFcb` and `AFSCcb` from the `FILE_OBJECT`, and relies on `AFSNonPagedFcb::SectionObjectResource` plus `SectionObjectPointers`. Important external helpers and APIs are `CcFlushCache`, `AFSFlushExtents`, `AFSReleaseExtentsWithFlush`, `AFSAcquireShared`, `AFSReleaseResource`, `AFSExceptionFilter`, `AFSDbgTrace`, and `AFSCompleteRequest`.

## Control Flow
The handler ignores the library device object, retrieves the current IRP stack location, file object, FCB, CCB, and redirector device extension, then enters the common OpenAFS `__Enter`/`try_return` flow. A null FCB returns `STATUS_INVALID_DEVICE_REQUEST`. Root FCBs (`AFS_ROOT_FCB` and `AFS_ROOT_ALL`) return success without flushing, with a comment that directory alternate data stream support would require real flushing later. Any non-file FCB other than root returns `STATUS_INVALID_PARAMETER` because those object types are considered write-through.

For regular file FCBs, it acquires `SectionObjectResource` shared and calls `CcFlushCache` on the FCB's section object pointers inside structured exception handling. A failed cache-manager `IO_STATUS_BLOCK.Status` becomes the IRP status. If cache flush succeeds and `AFS_DEVICE_FLAG_DIRECT_SERVICE_IO` is not set, the handler releases the section-object resource before remote flushing, then calls `AFSFlushExtents(Fcb, &Ccb->AuthGroup)`. If extent flush fails, it calls `AFSReleaseExtentsWithFlush(Fcb, &Ccb->AuthGroup, TRUE)` and deliberately converts the result to `STATUS_SUCCESS`. The common exit path releases the section-object resource if still held and completes the IRP with the final status.

## State and Persistence Behavior
The local persistence boundary is the Windows cache manager: `CcFlushCache` writes dirty cached pages represented by `SectionObjectPointers` and reports low-level failures in `iosb`. The remote persistence boundary is the OpenAFS extent layer: `AFSFlushExtents` pushes modified extents for the caller's auth group when the device is not configured for direct service I/O. On remote flush failure, `AFSReleaseExtentsWithFlush(..., TRUE)` releases extent state with a flush-oriented cleanup request, but the IRP still completes successfully, so callers may not see remote writeback failure through this path.

No metadata fields are directly changed in this file. State changes are limited to cache-manager writeback, extent flush/release side effects, lock ownership, trace output, and IRP completion status.

## Dependencies and Integration Points
This handler depends on `AFSCommon.h`, the global redirector device object, FCB/CCB layout, cache-manager section-object integration, and OpenAFS extent-management functions. It integrates with write and cleanup paths through shared extent state and with memory-mapped I/O through the section object resource. The auth group from the CCB is passed to extent flushing, tying remote writeback to the security context associated with the open.

## Risks and Edge Cases
The code assumes `pCcb` is valid for file FCBs; a malformed file object with valid FCB but null CCB would fault before or during extent flush. Root and non-file objects skip cache flushing, so future directory stream support must revisit the root/directory early-return logic. The most notable semantic risk is converting `AFSFlushExtents` failure to success after release/cleanup; this may be intentional to avoid surfacing transient remote failures after local cache flush, but it weakens caller-visible durability guarantees. Direct-service-I/O mode skips explicit extent flushing entirely and relies on another path for remote durability.

Locking is intentionally narrow: the section-object resource is held across `CcFlushCache` and released before `AFSFlushExtents` to avoid holding memory-manager/cache-manager locks during service/extent I/O. Any future change that keeps this lock across remote flushing would raise deadlock risk.

## Test Signals
Tests should exercise null FCB rejection, root FCB no-op success, non-file non-root rejection, successful file flush with and without `AFS_DEVICE_FLAG_DIRECT_SERVICE_IO`, `CcFlushCache` failure propagation, exception handling around `CcFlushCache`, extent flush success, extent flush failure triggering `AFSReleaseExtentsWithFlush` while returning success, and lock release on every early-return path. Integration tests should include dirty cached writes, memory-mapped writes, concurrent flush and cleanup/close, and auth-group-specific extent flushing.
