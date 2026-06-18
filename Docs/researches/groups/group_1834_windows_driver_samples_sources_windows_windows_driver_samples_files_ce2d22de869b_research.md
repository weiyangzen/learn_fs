# Group Research: group_1834_windows_driver_samples_sources_windows_windows_driver_samples_files_ce2d22de869b

Scope: `Docs/research_subset_a`

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/workque.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/workque.c

## Purpose

Implements CDFS request posting from the FSD path to worker-thread/FSP processing. It prepares IRPs for asynchronous continuation, handles oplock completion reposting, and throttles per-volume work items with an overflow queue.

## Key routines

- `CdFsdPostRequest`: common FSD posting entry point. Calls `CdPrePostIrp`, enqueues through `CdAddToWorkque`, and returns `STATUS_PENDING`.
- `CdPrePostIrp`: performs pre-post cleanup. It locks user buffers for reads, writes, and directory queries; handles create teardown state from oplock paths; marks the IRP pending; sets `IRP_CONTEXT_FLAG_MORE_PROCESSING`; and cleans the IRP context for reposting.
- `CdOplockComplete`: oplock package callback. If the IRP completed successfully, performs create teardown cleanup and queues the request; otherwise completes the request with the IRP status.
- `CdAddToWorkque`: queues the IRP context either to the per-volume overflow queue or to `CriticalWorkQueue` using `ExInitializeWorkItem` / `ExQueueWorkItem`.

## Control flow and state

`CdAddToWorkque` derives the `VOLUME_DEVICE_OBJECT` from the current IRP stack device object when a file object exists. It uses `OverflowQueueSpinLock` to guard `PostedRequestCount`, `OverflowQueue`, and `OverflowQueueCount`. If `PostedRequestCount > FSP_PER_DEVICE_THRESHOLD` where the threshold is `2`, it appends the context to the volume overflow list. Otherwise it increments `PostedRequestCount` and queues a worker item to `CdFspDispatch`.

`CdPrePostIrp` is also careful about create-time teardown state. When `IrpContext->TeardownFcb` still names an FCB, it calls `CdTeardownStructures`, releases the FCB if the teardown did not remove it, then clears both the referenced pointer and `IrpContext->TeardownFcb`.

## Dependencies

This file depends on CDFS core types and helpers from `CdProcs.h`, including `PIRP_CONTEXT`, `CdCleanupIrpContext`, `CdLockUserBuffer`, `CdTeardownStructures`, `CdReleaseFcb`, `CdCompleteRequest`, and `CdFspDispatch`. It also uses Windows kernel IRP, work queue, spin lock, and cache-safe pending APIs.

## Edge cases and notes

- MDL reads/writes skip user-buffer locking because no user buffer is present.
- Query-directory requests lock the query output buffer for write access.
- Failed oplock completion does not repost; it completes immediately.
- Requests with no associated file object bypass per-volume throttling and are queued directly to the system work queue.
- The file suppresses PREfast/obsolete warnings around legacy `ExInitializeWorkItem` and `ExQueueWorkItem`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/workque.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/write.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/write.c

## Purpose

Implements CDFS common write handling. Since CDFS is read-only for normal file data, this path only accepts volume/DASD writes through `UserVolumeOpen` and rejects all other open types.

## Key routine

- `CdCommonWrite`: common entry point for `NtWriteFile` handling in CDFS.

## Behavior

`CdCommonWrite` returns success immediately for zero-length writes. It decodes the file object and requires `TypeOfOpen == UserVolumeOpen`; otherwise it completes with `STATUS_INVALID_DEVICE_REQUEST`.

For volume writes, it acquires the FCB shared and verifies the FCB unless the handle is dismounting the volume. Unless extended DASD I/O is allowed, writes starting beyond file size return `STATUS_END_OF_FILE`, and writes extending beyond file size are truncated to the volume file size.

The routine then block-aligns the requested byte count. If the transfer is unaligned by sector offset or aligned size would exceed the original user buffer, it requires a wait-capable context; otherwise it raises `STATUS_CANT_WAIT` so the request can be posted. In the unaligned-buffer case it avoids writing past the caller buffer by reducing `WriteByteCount` back to `ByteCount`.

## I/O context and completion

The routine initializes `IrpContext->IoContext`, using stack storage for synchronous/wait-capable work and allocating a context for asynchronous work. It sets `Irp->IoStatus.Information` to the intended write byte count and marks the file object `FO_FILE_MODIFIED`.

The actual I/O is delegated to `CdVolumeDasdWrite`. If it returns `STATUS_PENDING`, the IRP is left incomplete and the file resource is not released by this function. Otherwise, errors are normalized through `FsRtlNormalizeNtstatus`, user-induced errors are raised, and partial alignment padding in the caller buffer is zeroed with the local `SafeZeroMemory` wrapper. Synchronous file position is advanced to the computed byte range on success.

## Dependencies

Uses CDFS helpers from `CdProcs.h`: `CdDecodeFileObject`, `CdAcquireFileShared`, `CdReleaseFile`, `CdVerifyFcbOperation`, `CdVolumeDasdWrite`, `CdMapUserBuffer`, `CdFsdPostRequest`, `CdCompleteRequest`, and status raising helpers. It relies on Windows IRP stack write parameters, file object flags, and exception handling.

## Edge cases and notes

- The only supported write surface is a volume open, not a user file open.
- `SafeZeroMemory` catches faults while zeroing user-buffer tail bytes and raises `STATUS_INVALID_USER_BUFFER`.
- `STATUS_CANT_WAIT` is converted into posting through `CdFsdPostRequest`.
- `ReleaseFile` is cleared when lower-level DASD write returns pending, transferring completion/resource responsibility to asynchronous I/O completion.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/acchksup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/acchksup.c

## Purpose

Provides FastFAT access-check support for FAT directory attributes, manage-volume privilege checks, explicit device ACL checks, and construction of a token that disables the Everyone SID.

## Key routines

- `FatCheckFileAccess`: filters requested file access against FAT dirent attributes.
- `FatCheckManageVolumeAccess`: checks whether the subject has `SE_MANAGE_VOLUME_PRIVILEGE`.
- `FatExplicitDeviceAccessGranted`: determines whether access was explicitly granted to the device object rather than only via Everyone.
- `FatCreateRestrictEveryoneToken`: creates a restricted token where `SeWorldSid` is disabled / deny-only.

## Access semantics

`FatCheckFileAccess` rejects volume ID and device dirents outright. It also rejects desired access masks containing rights outside the supported FAT set. For read-only dirents, it permits metadata/security-style access plus read-oriented access. For read-only directories, it additionally permits directory add and delete-child rights, matching FAT directory semantics.

`FatCheckManageVolumeAccess` builds a one-entry `PRIVILEGE_SET` for `SE_MANAGE_VOLUME_PRIVILEGE` and calls `SePrivilegeCheck`.

`FatExplicitDeviceAccessGranted` first accepts cases where specific access beyond traverse was already granted, and also accepts manage-volume privilege. Otherwise, it locks the subject context, selects the effective token, creates a restricted token without Everyone access, temporarily swaps that token into the subject context, and reruns `SeAccessCheck` against the device security descriptor. It restores the original token and dereferences the restricted token before returning.

## Dependencies

Uses FAT support declarations from `FatProcs.h`, FAT dirent attribute constants, Windows security token APIs (`SePrivilegeCheck`, `SeFilterToken`, `SeAccessCheck`, `SeLockSubjectContext`, `SeUnlockSubjectContext`), and object dereference APIs.

## Edge cases and notes

- The explicit-device check intentionally strips Everyone to distinguish broad public access from user/group-specific grants.
- `FatCreateRestrictEveryoneToken` returns a referenced token object that callers must release with `ObDereferenceObject`.
- `IrpContext` is unused in some routines except for interface consistency and tracing.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/acchksup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/allocsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/allocsup.c

## Purpose

Implements FastFAT allocation support: FAT scanning, free-cluster bitmap/window setup, file allocation lookup and growth, truncation, cluster allocation/deallocation, MCB split/merge, FAT entry encoding/decoding for FAT12/16/32, and bad-cluster discovery.

## Major data model

The file maintains allocation state in the VCB:

- `AllocationSupport`: root directory offsets/sizes, file-area LBO, number of clusters, FAT entry bit size, log sector/cluster sizes, total free clusters.
- `FreeClusterBitMap`: bitmap for the current allocation window, where set bits represent allocated clusters and clear bits represent free clusters.
- `Windows`: FAT32 window descriptors used when the volume has more clusters than `MAX_CLUSTER_BITMAP_SIZE`.
- `CurrentWindow`: active FAT window whose free bitmap is loaded.
- `ClusterHint`: window-relative allocation hint.
- `DirtyFatMcb`: tracks FAT sectors dirtied by allocation changes.
- `BadBlockMcb`: records bad clusters discovered while scanning.

## Key routines

- `FatSetupAllocationSupport`: computes allocation geometry, initializes/extends the virtual volume file cache, allocates FAT windows, scans FAT entries, chooses an initial window, builds the current free bitmap, and sets the first allocation hint.
- `FatTearDownAllocationSupport`: frees windows and bitmap storage and clears the dirty FAT MCB.
- `FatLookupFileAllocation`: maps a file VBO to LBO using the FCB/DCB MCB, extending the MCB by walking the FAT chain if needed.
- `FatAddFileAllocation`: appends clusters to a file/directory, updates first-cluster dirent fields when allocating an empty file, informs cache manager if needed, and merges new runs.
- `FatTruncateFileAllocation`: trims allocation to a cluster boundary, updates first-cluster fields for truncation to zero, splits allocation, and deallocates removed clusters.
- `FatLookupFileAllocationSize`: forces discovery of true chain allocation size using the special `MAXULONG - 1` lookup path.
- `FatAllocateDiskSpace`: reserves free clusters from the current/free windows, builds an MCB for newly allocated space, writes FAT chains, supports exact-match requests, and handles FAT32 window switching.
- `FatDeallocateDiskSpace`: optionally zeroes data before freeing, marks FAT entries available, clears bitmap bits in the active window, updates window and global free counts, and attempts FAT-chain restoration on failure.
- `FatSplitAllocation` / `FatMergeAllocation`: split and join MCB-described chains by rewriting the terminal or splice FAT entry.
- `FatInterpretClusterType`: classifies FAT entries as available, next, reserved, bad, or last, with FAT12/16 normalization and FAT32 masking.
- `FatLookupFatEntry`: reads a FAT entry using cached/pinned FAT pages, with special handling for FAT12 whole-FAT pinning.
- `FatSetFatEntry`: writes one FAT entry, including the special DOS-style FAT dirty/clean entry path.
- `FatSetFatRun`: writes a contiguous run of FAT entries, linking clusters or freeing them.
- `FatLogOf`: computes log2 for power-of-two values and bugchecks on invalid input.
- `FatExamineFatEntries`: scans FAT ranges to build free bitmaps, initialize FAT32 windows, serve volume bitmap data, and populate bad-cluster state.

## Allocation algorithm

Allocation starts by rounding requested bytes to clusters, with special handling for the maximal 4 GiB minus 1 case. `FatAllocateDiskSpace` first subtracts the requested cluster count from the global free count while holding `ChangeBitMapResource` and `FreeClusterBitMapMutex`, ensuring another thread cannot take the space.

It then searches for a contiguous free run from either an absolute hint or `Vcb->ClusterHint`. If a sufficient run exists and exact-match constraints are met, it reserves bitmap bits, updates window free count, adds the run to the output MCB, and writes the FAT chain.

If no single run satisfies the request, it upgrades to exclusive bitmap-resource access, repeatedly chooses runs from the current or selected FAT32 windows, reserves them, writes FAT entries, links disjoint runs through the prior last cluster, and advances until the requested cluster count is satisfied. FAT32 can switch windows to maintain locality or select a better window by `FatSelectBestWindow`.

## Deallocation and zeroing

`FatDeallocateDiskSpace` first optionally zeroes every run via synchronous write IRPs using zero MDLs capped at `MAX_ZERO_MDL_SIZE` (1 MiB). Zeroing failures are recorded but do not prevent freeing, to avoid leaking volume space.

The actual free operation has two phases: write `FAT_CLUSTER_AVAILABLE` into affected FAT entries, then update in-memory bitmap/window/free counts. This ordering prevents another allocator from taking clusters that would need to be restored if FAT updates fail. On abnormal termination, the routine walks already-processed MCB entries and attempts to rebuild the FAT chain.

## FAT12/16/32 handling

- FAT12 lookup pins the whole FAT because entries can cross byte/page boundaries.
- FAT16 lookup pins one FAT page at a time and reads `USHORT` entries.
- FAT32 lookup pins one FAT page at a time, reads `ULONG` entries, and masks with `FAT32_ENTRY_MASK`.
- FAT32 write paths preserve reserved high bits for normal entries and chunk large `FatSetFatRun` operations with unwind logic because pinning all touched FAT pages may be impractical.

## Failure and unwind behavior

This file is heavily exception-oriented. Growth, truncation, split, merge, allocation, deallocation, and FAT write routines use `try/finally` blocks to reverse partial state:

- `FatAddFileAllocation` rolls back allocation size, cache-manager size changes, first-cluster dirent updates, and newly allocated disk space.
- `FatTruncateFileAllocation` restores in-memory allocation fields when possible, but comments acknowledge cluster leaks may remain after some deallocation failures.
- `FatSplitAllocation` merges MCB runs back on failure.
- `FatMergeAllocation` removes appended MCB runs on failure.
- `FatSetFatRun` has FAT32-specific unwind to restore previously changed entries.

## Dependencies

Depends on FastFAT types/helpers in `FatProcs.h`, cache helpers from `cachesup.c`, MCB wrappers (`FatAddMcbEntry`, `FatLookupMcbEntry`, `FatRemoveMcbEntry`, etc.), FAT geometry macros, Windows cache manager APIs, RTL bitmap APIs, resource/fast mutex synchronization, MDL and IRP I/O APIs, and security/error propagation helpers.

## Edge cases and notes

- FAT32 volumes larger than `MAX_CLUSTER_BITMAP_SIZE` use bucket/window scanning to avoid maintaining a huge bitmap at once.
- `FatExamineFatEntries` handles three distinct roles: setup scan, window switch, and arbitrary bitmap fill.
- `FatLookupFileAllocation` detects corrupt chains that hit available/reserved/bad clusters where a continuation is expected.
- Bad clusters are recorded in `BadBlockMcb` during setup or single-window scans.
- The code contains explicit maximal-file overflow handling where byte counts can wrap to zero or use `0xffffffff`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/allocsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/cachesup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/cachesup.c

## Purpose

Implements FastFAT cache-manager integration for volume FAT data, directory stream files, EA stream files, dirty/repinned BCB handling, MDL completion, synchronous cache-map teardown, mapped-data pinning, zeroing, and Win8+ page prefetch.

## Key routines

- `FatInitializeCacheMap`: wrapper for `CcInitializeCacheMap`; enables disk I/O accounting on Win8+ when configured.
- `FatReadVolumeFile`: maps FAT volume-file ranges through `CcMapData`.
- `FatPrepareWriteVolumeFile`: pins FAT volume-file ranges with `CcPinRead`, optionally zeroes them, and marks dirty through `FatSetDirtyBcb`.
- `FatReadDirectoryFile`: opens/initializes a directory stream file if needed and maps or pins directory data.
- `FatPrepareWriteDirectoryFile`: extends directory allocation when needed, pins pages or VACB-sized ranges, zeroes new allocation, and marks data dirty.
- `FatOpenDirectoryFile`: creates and initializes the internal stream file object for a directory.
- `FatOpenEaFile` / `FatCloseEaFile`: create and tear down the EA stream file and cache map.
- `FatSetDirtyBcb`: optionally repins a BCB, marks it dirty, and manages delayed volume-clean/dirty state.
- `FatRepinBcb`: stores unique BCB references in the IRP context for later controlled unpin.
- `FatUnpinRepinnedBcbs`: write-through unpins repinned BCBs, purges cache sections on selected removable-media failures, and raises failed flush status unless disabled.
- `FatZeroData`: sector-aligns and delegates zeroing to `CcZeroData`.
- `FatCompleteMdl`: completes MDL read/write requests through cache-manager MDL completion APIs.
- `FatSyncUninitializeCacheMap`: synchronously waits for `CcUninitializeCacheMap` completion.
- `FatPinMappedData`: pins already mapped directory data.
- `FatPrefetchPages`: Win8+ helper that builds an `MM_PREFETCH` read list and calls `MmPrefetchPages`.

## Directory cache flow

Directory reads and writes call `FatOpenDirectoryFile` to ensure a stream file object and cache map exist. If allocation size is unknown, the code resolves it through `FatLookupFileAllocationSize`, sets directory file size from allocation size, and checks the free-dirent bitmap.

`FatPrepareWriteDirectoryFile` grows directory allocation with `FatAddFileAllocation` if the write extends beyond current allocation. FAT12/16 root directories cannot grow and return disk full. After growth, it updates cache-manager file sizes and zeroes newly allocated clusters. It pins in page-sized chunks within the original request to avoid OBCBs, then uses `VACB_MAPPING_GRANULARITY` after crossing the original request boundary for efficiency. On abnormal termination after allocation growth, it truncates back to the original allocation and updates cache sizes.

## Dirty and repinned BCB handling

`FatSetDirtyBcb` calls `CcSetDirtyPinnedData`, and when allowed marks the volume dirty for non-FAT12 volumes. It throttles physical dirty marking/timer updates to roughly once per second, sets a clean-volume timer, and disables eject for removable media when transitioning dirty.

`FatRepinBcb` records each BCB once in a linked list of `REPINNED_BCBS` arrays stored from the IRP context. `FatUnpinRepinnedBcbs` later unpins all of them, optionally write-through for write-through or deferred-flush media. On failures for removable/deferred-flush media, it can unpin other BCBs from the same file, purge the file cache section, force verify, and propagate normalized status.

## Internal stream files

`FatOpenDirectoryFile` creates an internal stream file object with `IoCreateStreamFileObject`, associates it with the DCB, increments internal/residual open counts, assigns section object pointers, grants access flags, and initializes a cache map using no-op callbacks.

`FatOpenEaFile` performs analogous setup for the EA file, but uses `FatData.CacheManagerCallbacks` and calls `CcSetAdditionalCacheAttributes` to disable read-ahead/write-behind-style behavior for EA handling. `FatCloseEaFile` flushes optionally, clears `Vcb->VirtualEaFile`, clears the EA MCB, synchronously uninitializes the cache map, and dereferences the stream file object.

## Synchronization and debug checks

In debug builds, `FatIsCurrentOperationSynchedForDcbTeardown` validates that a directory open operation is protected against DCB teardown by mount state, VCB ownership, parent-by-child context, or an operation file object rooted under the DCB. `FatOpenDirectoryFile` asserts this before adding an internal open.

Directory stream creation uses a directory-file mutex and double-checks `Dcb->Specific.Dcb.DirectoryFile` under that mutex.

## Dependencies

Depends on `FatProcs.h`, allocation support (`FatAddFileAllocation`, `FatTruncateFileAllocation`, `FatLookupFileAllocationSize`), directory bitmap support, close-context preallocation, FastFAT file-object tagging, cache manager APIs, memory manager prefetch APIs for Win8+, and kernel synchronization/timer/DPC primitives.

## Edge cases and notes

- `FatReadVolumeFile` asserts reads stay within the boot/reserved/FAT region, with a mount-time exception for offset zero.
- `FatPrepareWriteVolumeFile` ensures pinned data is unpinned on abnormal termination.
- `FatZeroData` returns success for sector-fragment-only zero requests because `CcZeroData` cannot handle non-sector-aligned ranges in this temporary helper.
- `FatCompleteMdl` only accepts read and write major functions; any other major function bugchecks.
- `FatPrefetchPages` treats zero-page prefetch as success and frees its read list on all exit paths.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/cachesup.c -->