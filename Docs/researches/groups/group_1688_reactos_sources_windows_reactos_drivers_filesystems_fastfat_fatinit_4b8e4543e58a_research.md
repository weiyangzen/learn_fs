# Group Research: group_1688_reactos_sources_windows_reactos_drivers_filesystems_fastfat_fatinit_4b8e4543e58a

Scope: `Docs/research_subset_a.md` includes `sources/windows/reactos`, so all files in this group are in scope.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatinit.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatinit.c

## Purpose

`fatinit.c` implements FastFAT driver initialization and unload support. It creates the filesystem device objects, wires the IRP and Fast I/O dispatch tables, initializes global driver state, reads compatibility registry options, registers filter callbacks, and registers FAT as a disk and CD-ROM filesystem with the I/O manager.

## Main Entry Points

- `DriverEntry`
  - Creates `\Fat` as `FILE_DEVICE_DISK_FILE_SYSTEM`.
  - Creates `\FatCdrom` as `FILE_DEVICE_CD_ROM_FILE_SYSTEM`.
  - Assigns every FastFAT `IRP_MJ_*` dispatch routine into `DriverObject->MajorFunction`.
  - Initializes `FatFastIoDispatch` with Fast I/O read/write/query/lock/MDL callbacks.
  - Registers `FatFilterCallbackAcquireForCreateSection` with `FsRtlRegisterFileSystemFilterCallbacks`.
  - Zeroes and initializes global `FatData`.
  - Initializes close queues, work item, zero page, spin lock, resources, lookaside lists, cache manager callbacks, processor count, and global process pointer.
  - Reads registry values controlling Chicago compatibility mode and code-page invariance.
  - Registers both filesystem device objects with `IoRegisterFileSystem`.
  - Detects Fujitsu FMR hardware.
  - On Windows 8+ caches global disk accounting state via `PsIsDiskCountersEnabled`.

- `FatUnload`
  - Deletes nonpaged lookaside lists.
  - Deletes `FatData.Resource`.
  - Frees the close work item.
  - Dereferences the disk and CD-ROM filesystem device objects.
  - Notably does not delete all objects or free every allocation initialized in `DriverEntry`; this mirrors a filesystem driver unload path that depends on broader lifetime assumptions.

- `FatGetCompatibilityModeValue`
  - Opens `\Registry\Machine\System\CurrentControlSet\Control\FileSystem`.
  - Queries a DWORD-like value by name.
  - Uses a fixed stack buffer first, then grows a paged-pool buffer on `STATUS_BUFFER_OVERFLOW`.
  - Returns the registry value through `Value` only on success with nonzero data length.

- `FatIsFujitsuFMR`
  - Opens `\Registry\Machine\Hardware\DESCRIPTION\System`.
  - Reads the `Identifier` value.
  - Returns true when the value begins with `FUJITSU FMR-`.

## Important Constants

- `COMPATIBILITY_MODE_KEY_NAME`: filesystem control registry key.
- `COMPATIBILITY_MODE_VALUE_NAME`: `Win31FileSystem`; inverted into `FatData.ChicagoMode`.
- `CODE_PAGE_INVARIANCE_VALUE_NAME`: `FatDisableCodePageInvariance`; inverted into `FatData.CodePageInvariant`.
- `KEY_WORK_AREA`: initial registry query buffer size.
- `REGISTRY_HARDWARE_DESCRIPTION_W`, `REGISTRY_MACHINE_IDENTIFIER_W`, `FUJITSU_FMR_NAME_W`: hardware detection inputs.

## Initialization Flow

1. Create named filesystem device objects.
2. Set dispatch and Fast I/O tables.
3. Register FS filter callback for section synchronization.
4. Initialize `FatData` and global queues.
5. Allocate close work item and zero page.
6. Tune close/list lookaside depth from `MmQuerySystemSize`.
7. Initialize cache manager callbacks.
8. Read registry behavior toggles.
9. Initialize resources and lookaside lists.
10. Register with the I/O manager.
11. Record hardware/platform features.
12. Return `STATUS_SUCCESS`.

## Error Handling

- Device creation failure returns immediately.
- If CD-ROM filesystem device creation fails, the disk filesystem device is deleted.
- Filter callback registration failure deletes both device objects.
- Work item and zero-page allocation failures return `STATUS_INSUFFICIENT_RESOURCES`.
- Registry lookup failures are tolerated; defaults are used.

## Dependencies

This file depends heavily on declarations from `fatprocs.h`, especially:

- Global variables: `FatData`, `FatDiskFileSystemDeviceObject`, `FatCdromFileSystemDeviceObject`, `FatFastIoDispatch`, lookaside lists, close queues.
- Dispatch routines: `FatFsdCreate`, `FatFsdRead`, `FatFsdWrite`, etc.
- Fast I/O callbacks: `FatFastIoCheckIfPossible`, `FatFastQueryBasicInfo`, `FatFastLock`, etc.
- Cache callbacks: `FatAcquireFcbForLazyWrite`, `FatReleaseFcbFromReadAhead`, etc.
- Filter callback: `FatFilterCallbackAcquireForCreateSection`.

## Research Notes

`fatinit.c` is the root bootstrap for the ReactOS FastFAT driver. Most functional behavior is delegated elsewhere; this file defines how the driver becomes visible to NT I/O, cache, and filesystem-filter infrastructure. The registry reads establish compatibility defaults that influence name handling and long filename behavior throughout the driver.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatinit.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatprocs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatprocs.h

## Purpose

`fatprocs.h` is the central internal procedure header for the FastFAT filesystem. It includes NT kernel headers, FAT structure headers, ReactOS compatibility shims, shared helper macros, and prototypes for the driver’s major subsystems.

It is the main internal ABI between FastFAT modules.

## Included Dependencies

- NT filesystem/device headers: `ntifs.h`, `ntddscsi.h`, `scsi.h`, `ntddcdrm.h`, `ntdddisk.h`, `ntddstor.h`, `ntintsafe.h`.
- ReactOS-specific headers under `__REACTOS__`: `pseh/pseh2.h`, `dbgbitmap.h`.
- Local headers:
  - `nodetype.h`
  - `fat.h`
  - `lfn.h`
  - `fatstruc.h`
  - `fatdata.h`

## ReactOS Compatibility Adjustments

Under `__REACTOS__`, this header downgrades unsupported NT 6.2+ memory/security features:

- `MdlMappingNoExecute` becomes `0`.
- `NonPagedPoolNx` maps to `NonPagedPool`.
- `NonPagedPoolNxCacheAligned` maps to `NonPagedPoolCacheAligned`.
- `POOL_NX_ALLOCATION` becomes `0`.

It also defines `TYPE_OF_OPEN` before `fatstruc.h`, because `fatstruc.h` needs it.

## Major Type and Macro Definitions

- `FINISHED`: Boolean result convention for operations that may fail only because waiting/blocking was not allowed.
- `FAT_CREATE_INITIAL_NAME_BUF_SIZE`: stack buffer size for create/rename name components.
- `FAT_ENUMERATION_CONTEXT`: tracks a pinned FAT page during FAT entry enumeration.
- `TYPE_OF_OPEN`: identifies file object interpretation:
  - `UnopenedFileObject`
  - `UserFileOpen`
  - `UserDirectoryOpen`
  - `UserVolumeOpen`
  - `VirtualVolumeFile`
  - `DirectoryFile`
  - `EaFile`
- `FAT_FLUSH_TYPE`: flush/purge modes.
- `COMPARISON`: name comparison result.
- `FAT_VOLUME_STATE`: clean/dirty volume marking modes.
- Alignment and pointer helpers: `Add2Ptr`, `PtrOffset`, `WordAlign`, `LongAlign`, `QuadAlign`, `BlockAlign`, `BlockAlignTruncate`.
- Unaligned field copy helpers: `CopyUchar1`, `CopyUchar2`, `CopyUchar4`, `CopyU4char`.

## Functional Areas Declared

### String and MCB Helpers

Declares string buffer management and MCB mapping helpers:

- `FatFreeStringBuffer`
- `FatExtendString`
- `FatEnsureStringBufferEnough`
- `FatAddMcbEntry`
- `FatLookupMcbEntry`
- `FatLookupLastMcbEntry`
- `FatGetNextMcbEntry`
- `FatRemoveMcbEntry`

### Access Checks

Declares access validation helpers:

- `FatCheckFileAccess`
- `FatCheckManageVolumeAccess`
- `FatExplicitDeviceAccessGranted`

### Allocation Support

Declares FAT cluster/allocation operations:

- `FatLookupFatEntry`
- `FatSetupAllocationSupport`
- `FatTearDownAllocationSupport`
- `FatLookupFileAllocation`
- `FatAddFileAllocation`
- `FatTruncateFileAllocation`
- `FatLookupFileAllocationSize`
- `FatAllocateDiskSpace`
- `FatDeallocateDiskSpace`
- `FatSplitAllocation`
- `FatMergeAllocation`
- `FatSetFatEntry`
- `FatLogOf`

The inline `FatIsIoRangeValid` enforces FAT’s 32-bit file-size addressability limit.

### Cache and Buffer Support

Declares volume/directory cache access, cache-map setup, BCB pinning/dirtying, MDL completion, prefetching, and zeroing:

- `FatReadVolumeFile`
- `FatPrepareWriteVolumeFile`
- `FatReadDirectoryFile`
- `FatPrepareWriteDirectoryFile`
- `FatOpenDirectoryFile`
- `FatSetDirtyBcb`
- `FatRepinBcb`
- `FatUnpinRepinnedBcbs`
- `FatZeroData`
- `FatInitializeCacheMap`
- `FatSyncUninitializeCacheMap`

`FatUnpinBcb` is a macro; debug builds decrement `IrpContext->PinCount`.

### Device I/O

Declares noncached and paging I/O helpers:

- `FatPagingFileIo`
- `FatNonCachedIo`
- `FatNonCachedNonAlignedRead`
- `FatMultipleAsync`
- `FatSingleAsync`
- `FatWaitSync`
- `FatLockUserBuffer`
- `FatBufferUserBuffer`
- `FatMapUserBuffer`
- `FatToggleMediaEjectDisable`
- `FatPerformDevIoCtrl`
- `FatBuildZeroMdl`

### Directory Entry Support

Declares dirent creation, lookup, deletion, construction, and synchronization with FCB state:

- `FatCreateNewDirent`
- `FatInitializeDirectoryDirent`
- `FatDeleteDirent`
- `FatLocateDirent`
- `FatLocateSimpleOemDirent`
- `FatLfnDirentExists`
- `FatLocateVolumeLabel`
- `FatGetDirentFromFcbOrDcb`
- `FatIsDirectoryEmpty`
- `FatDeleteFile`
- `FatConstructDirent`
- `FatConstructLabelDirent`
- `FatSetFileSizeInDirent`
- `FatUpdateDirentFromFcb`

`FatDirectoryKey` derives a 64-bit directory key from creation time and first cluster.

### Extended Attributes

Declares EA file and packed-EA manipulation:

- `FatGetEaLength`
- `FatGetNeedEaCount`
- `FatCreateEa`
- `FatDeleteEa`
- `FatGetEaFile`
- `FatReadEaSet`
- `FatDeleteEaSet`
- `FatAddEaSet`
- `FatDeletePackedEa`
- `FatAppendPackedEa`
- `FatLocateNextEa`
- `FatLocateEaByName`
- `FatIsEaNameValid`
- `FatPinEaRange`
- `FatMarkEaRangeDirty`
- `FatUnpinEaRange`

### File Object Support

Declares mapping between NT file objects and FastFAT objects:

- `FatSetFileObject`
- `FatDecodeFileObject`
- `FatPurgeReferencedFileObjects`
- `FatForceCacheMiss`

### Filesystem Control

Declares volume flush, boot-sector validation, and lock/unlock helpers:

- `FatFlushAndCleanVolume`
- `FatIsBootSectorFat`
- `FatLockVolumeInternal`
- `FatUnlockVolumeInternal`

### Name Support

Declares short/long name validation, 8.3 conversion, Unicode/OEM conversion, LFN selection, and case restoration:

- `FatIsNameInExpression`
- `FatStringTo8dot3`
- `Fat8dot3ToString`
- `FatGetUnicodeNameFromFcb`
- `FatSetFullFileNameInFcb`
- `FatSetFullNameInFcb`
- `FatUnicodeToUpcaseOem`
- `FatSelectNames`
- `FatEvaluateNameCase`
- `FatSpaceInName`
- `FatUnicodeRestoreShortNameCase`

Inline/macro helpers include:

- `FatAreNamesEqual`
- `FatIsNameShortOemValid`
- `FatIsNameLongOemValid`
- `FatIsNameLongUnicodeValid`

### Resource and Locking Model

Defines the core locking protocol:

- Global resource: `FatData.Resource`
- Volume resource: `Vcb->Resource`
- File resource: `Fcb->Header.Resource`

Macros and routines include:

- `FatAcquireExclusiveGlobal`
- `FatAcquireSharedGlobal`
- `FatAcquireExclusiveVolume`
- `FatReleaseVolume`
- `FatAcquireExclusiveVcb`
- `FatAcquireSharedVcb`
- `FatAcquireExclusiveFcb`
- `FatAcquireSharedFcb`
- `FatAcquireSharedFcbWaitForEx`
- `FatConvertToSharedFcb`
- `FatReleaseGlobal`
- `FatReleaseVcb`
- `FatReleaseFcb`

The comments document a clear acquisition hierarchy: global first, then VCB or FCB, with mount/dismount taking the global resource exclusive.

### Cache Manager and Filter Callbacks

Declares cache callback routines:

- `FatAcquireVolumeForClose`
- `FatReleaseVolumeFromClose`
- `FatAcquireFcbForLazyWrite`
- `FatReleaseFcbFromLazyWrite`
- `FatAcquireFcbForReadAhead`
- `FatReleaseFcbFromReadAhead`
- `FatAcquireForCcFlush`
- `FatReleaseForCcFlush`
- `FatNoOpAcquire`
- `FatNoOpRelease`
- `FatFilterCallbackAcquireForCreateSection`

### Structure Lifecycle

Declares constructors/destructors and traversal helpers:

- `FatInitializeVcb`
- `FatTearDownVcb`
- `FatDeleteVcb`
- `FatCreateRootDcb`
- `FatCreateFcb`
- `FatCreateDcb`
- `FatDeleteFcb`
- `FatCreateCcb`
- `FatDeleteCcb`
- `FatCreateIrpContext`
- `FatDeleteIrpContext_Real`
- `FatGetNextFcbTopDown`
- `FatGetNextFcbBottomUp`
- `FatCheckForDismount`

### Splay Tree Name Indexes

Declares open-FCB name index operations:

- `FatInsertName`
- `FatRemoveNames`
- `FatFindFcb`
- `FatIsHandleCountZero`
- `FatCompareNames`

`CompareNames` optimizes comparison by first byte before full compare.

### Time Conversion

Declares FAT/NT timestamp conversions:

- `FatNtTimeToFatTime`
- `FatFatTimeToNtTime`
- `FatFatDateToNtTime`
- `FatGetCurrentFatTime`

### Verification and Dirty State

Declares media/volume verification and dirty marking:

- `FatMarkFcbCondition`
- `FatVerifyVcb`
- `FatVerifyFcb`
- `FatCleanVolumeDpc`
- `FatMarkVolume`
- `FatFspMarkVolumeDirtyWithRecover`
- `FatCheckDirtyBit`
- `FatQuickVerifyVcb`
- `FatVerifyOperationIsLegal`
- `FatPerformVerify`

### Work Queue

Declares posting and worker dispatch support:

- `FatOplockComplete`
- `FatPrePostIrp`
- `FatAddToWorkque`
- `FatFsdPostRequest`
- `FatFspDispatch`

### Dispatch Surface

Declares all FSD dispatch routines registered in `fatinit.c`:

- `FatFsdCleanup`
- `FatFsdClose`
- `FatFsdCreate`
- `FatFsdDeviceControl`
- `FatFsdDirectoryControl`
- `FatFsdQueryEa`
- `FatFsdSetEa`
- `FatFsdQueryInformation`
- `FatFsdSetInformation`
- `FatFsdFlushBuffers`
- `FatFsdFileSystemControl`
- `FatFsdLockControl`
- `FatFsdPnp`
- `FatFsdRead`
- `FatFsdShutdown`
- `FatFsdQueryVolumeInformation`
- `FatFsdSetVolumeInformation`
- `FatFsdWrite`

Also declares corresponding `FatCommon*` routines used by FSD/FSP paths.

### Fast I/O

Declares fast I/O callbacks:

- `FatFastIoCheckIfPossible`
- `FatFastQueryBasicInfo`
- `FatFastQueryStdInfo`
- `FatFastQueryNetworkOpenInfo`
- `FatFastLock`
- `FatFastUnlockSingle`
- `FatFastUnlockAll`
- `FatFastUnlockAllByKey`

`FatIsFastIoPossible` derives Fast I/O eligibility from FCB condition, node type, oplock state, byte-range locks, async writes, and write protection.

### Exception Handling

Declares and defines the driver’s structured exception convention:

- `FatExceptionFilter`
- `FatBugCheckExceptionFilter`
- `FatProcessException`
- `FatRaiseStatus`
- `FatResetExceptionState`
- `FatNormalizeAndRaiseStatus`
- `try_return`
- `try_leave`

`FatRaiseStatus` records expected errors in `IrpContext->ExceptionStatus` before raising.

### FAT-Specific Helpers

- `FatInterpretClusterType`
- `FatGenerateFileIdFromDirentOffset`
- `FatGenerateFileIdFromFcb`
- `FatGenerateFileIdFromDirentAndOffset`
- `FatDeviceIsFatFsdo`
- `IsDirectory`
- `IsFileDeleted`
- `IsFileWriteThrough`
- `IsFileObjectReadOnly`

## Research Notes

This header is the coordination point for the entire FastFAT implementation. It exposes module boundaries through comment headings, so it doubles as an architecture map: allocation, cache, device I/O, directory, EA, file-object, filesystem-control, name, resource, structure, splay, time, verification, work queue, FSD/FSP dispatch, Fast I/O, and exception-handling concerns are all declared here.

The most important design point is the explicit resource hierarchy and the distinction between FSD synchronous dispatch, FSP worker-thread processing, and Fast I/O shortcuts.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatprocs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatprocssrc.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatprocssrc.c

## Purpose

`fatprocssrc.c` contains only:

```c
#include "fatprocs.h"
```

It is a tiny source translation unit that includes the central FastFAT procedure header.

## Behavior

There are no functions, globals, macros, or executable logic defined directly in this file. Its only effect is to force compilation of a translation unit that sees `fatprocs.h`.

## Dependencies

- `fatprocs.h`, which in turn includes NT kernel headers and FastFAT internal structure/data headers.

## Research Notes

This file is likely present for build-system, precompiled-header, dependency-generation, or source-layout compatibility reasons. It does not add runtime behavior by itself.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatprocssrc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatstruc.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatstruc.h

## Purpose

`fatstruc.h` defines FastFAT’s core in-memory data structures. These are the objects manipulated by the routines declared in `fatprocs.h`: global driver data, mounted volumes, file/directory control blocks, per-handle context, IRP context, noncached I/O context, and EA helper ranges.

## Core Object Model

### `FAT_DATA`

Global FastFAT driver state, allocated from nonpaged pool.

Important fields:

- Node identity: `NodeTypeCode`, `NodeByteSize`.
- Mounted volume list: `VcbQueue`.
- Driver and filesystem device objects: `DriverObject`, `DiskFileSystemDeviceObject`, `CdromFileSystemDeviceObject`.
- Global synchronization: `Resource`, `GeneralSpinLock`.
- Cache integration: `OurProcess`, `CacheManagerCallbacks`, `CacheManagerNoOpCallbacks`.
- Runtime flags:
  - `ChicagoMode`
  - `FujitsuFMR`
  - `AsyncCloseActive`
  - `ShutdownStarted`
  - `CodePageInvariant`
  - `HighAsync`
  - `HighDelayed`
- Deferred close queues:
  - `AsyncCloseList`
  - `DelayedCloseList`
  - `FatCloseItem`
- Shared zero page: `ZeroPage`.

### `FAT_WINDOW`

Represents a window into the FAT free-cluster bitmap when the FAT is too large to keep one full bitmap resident.

Fields:

- `FirstCluster`
- `LastCluster`
- `ClustersFree`

### `CLOSE_CONTEXT`

Carries state for asynchronous or delayed close processing.

Fields:

- Global and per-VCB list links.
- `Vcb`
- `Fcb`
- `TypeOfOpen`
- `Free`

This structure can be embedded/overlaid in a `CCB`.

### `VCB`

Volume Control Block for each mounted FAT volume.

Major categories:

- Common volume file header: `VolumeFileHeader`.
- Global mount linkage: `VcbLinks`.
- Device linkage: `TargetDeviceObject`, `Vpb`, `CurrentDevice`, optional `VolumeGuid`, `VolumeGuidPath`.
- State: `VcbState`, `VcbCondition`.
- Root object: `RootDcb`.
- Allocation metadata:
  - `NumberOfWindows`
  - `Windows`
  - `CurrentWindow`
  - `Bpb`
  - `First0x24BytesOfBootSector`
  - `AllocationSupport`
  - `DirtyFatMcb`
  - `BadBlockMcb`
  - `FreeClusterBitMap`
  - `FreeClusterBitMapMutex`
  - `ChangeBitMapResource`
  - `ClusterHint`
- Open counts:
  - `DirectAccessOpenCount`
  - `OpenFileCount`
  - `ReadOnlyCount`
  - `InternalOpenCount`
  - `ResidualOpenCount`
- Synchronization:
  - `Resource`
  - `DirectoryFileCreationMutex`
  - `AdvancedFcbHeaderMutex`
- Cache/stream objects:
  - `VirtualVolumeFile`
  - `SectionObjectPointers`
  - `VirtualEaFile`
  - `EaFcb`
- Volume locking and notifications:
  - `FileObjectWithVcbLocked`
  - `DirNotifyList`
  - `NotifySync`
- Verification and dirty-clean timers:
  - `VerifyThread`
  - `CleanVolumeDpc`
  - `CleanVolumeTimer`
  - `LastFatMarkVolumeDirtyCall`
- Statistics and tunneling:
  - `Statistics`
  - `Tunnel`
- Media/device details:
  - `ChangeCount`
  - `DeviceNumber`
  - `SwapVpb`
- Per-volume close queues:
  - `AsyncCloseList`
  - `DelayedCloseList`

### `VCB_STATE_*`

Defines volume state flags such as:

- locked
- removable media
- volume dirty
- mounted dirty
- shutdown
- close in progress
- deleted FCB
- create in progress
- boot/paging file
- deferred flush
- async close active
- write protected
- removal prevented
- volume dismounted
- VPB lifecycle flags
- dismount in progress
- bad blocks populated
- hotpluggable
- mount in progress

`VCB_STATE_FLAG_VOLUME_DISMOUNTED` is explicitly documented as FSCTL dismount state, not a replacement for `VcbCondition`.

### `FILE_SYSTEM_STATISTICS`

Combines `FILESYSTEM_STATISTICS` and `FAT_STATISTICS`, padded to a 64-byte multiple to avoid cache-line tearing. `Vcb->Statistics` points to one per processor.

### `VOLUME_DEVICE_OBJECT`

An NT `DEVICE_OBJECT` with FastFAT volume state appended.

Fields:

- Base `DEVICE_OBJECT`.
- Work overflow accounting:
  - `PostedRequestCount`
  - `OverflowQueueCount`
  - `OverflowQueue`
  - `OverflowQueueSpinLock`
- `VolumeFileHeader`
- Embedded `VCB`.

### `FILE_NAME_NODE`

Name index entry used in per-directory splay trees.

Fields:

- Back-pointer to `Fcb`.
- Name union: OEM or Unicode.
- `FileNameDos` marker.
- `RTL_SPLAY_LINKS`.

### `NON_PAGED_FCB`

Nonpaged per-FCB state required by cache/MM and async writes.

Fields:

- `SectionObjectPointers`
- `OutstandingAsyncWrites`
- `OutstandingAsyncEvent`
- `AdvancedFcbHeaderMutex`

### `FCB` / `DCB`

The File Control Block and Directory Control Block share the same structure. `DCB` is typedef’d to `FCB` except when building FSKD extensions.

Major fields:

- `FSRTL_ADVANCED_FCB_HEADER Header`
- `NonPaged`
- `FirstClusterOfFile`
- Parent/volume relationship:
  - `ParentDcbLinks`
  - `ParentDcb`
  - `Vcb`
- State:
  - `FcbState`
  - `FcbCondition`
  - `ShareAccess`
- Open/accounting counters:
  - `UncleanCount`
  - `OpenCount`
  - `NonCachedUncleanCount`
  - `PurgeFailureModeEnableCount`
- On-disk location:
  - `DirentOffsetWithinDirectory`
  - `LfnOffsetWithinDirectory`
- Cached timestamps:
  - `CreationTime`
  - `LastAccessTime`
  - `LastWriteTime`
- Allocation/cache:
  - `ValidDataToDisk`
  - `Mcb`
- Directory-specific union member:
  - `ParentDcbQueue`
  - `DirectoryFileOpenCount`
  - `DirectoryFile`
  - `UnusedDirentVbo`
  - `DeletedDirentHint`
  - `RootOemNode`
  - `RootUnicodeNode`
  - `FreeDirentBitmap`
  - `FreeDirentBitmapBuffer`
- File-specific union member:
  - `FileLock`
  - pre-Win8 `Oplock`
  - `LazyWriteThread`
- Name and attribute state:
  - `EaModificationCount`
  - `ShortName`
  - `FullFileName`
  - `FinalNameLength`
  - `DirentFatFlags`
  - `ExactCaseLongName`
  - `LongName` union for OEM or Unicode LFN tree node
- Move/defrag synchronization:
  - `MoveFileEvent`

The comments explain why FastFAT keeps both OEM and Unicode splay trees: FAT has both OEM short names and Unicode long names on disk, and a single Unicode tree would not reliably preserve the current prefix-lookup assumptions without further duplicate-FCB handling.

### `FCB_STATE_*`

Defines per-file/per-directory state flags:

- delete on close
- truncate on close
- paging file
- force cache miss in progress
- flush FAT
- temporary
- system file
- names in splay tree
- OEM long name present
- Unicode long name present
- delay close
- short-name case flags
- deny defrag
- zero on deallocation

`FCB_LOOKUP_ALLOCATIONSIZE_HINT` is `-1`, meaning allocation size must be discovered from disk.

### `CCB`

Context Control Block allocated per file object/handle.

Important fields:

- Node identity.
- `Flags` plus `ContainsWildCards`.
- Optional encryption-on-close context.
- Union containing either:
  - Directory/query/EA state:
    - `OffsetToStartSearchFrom`
    - OEM query template as wildcard string or constant 8.3 name
    - Unicode query template
    - `EaModificationCount`
    - `OffsetOfNextEaToReturn`
  - `CloseContext` overlay for close processing.

### `CCB_FLAG_*`

Defines handle state such as:

- match all
- skip short-name compare
- free query template buffers
- user-set timestamp fields
- read-only handle
- DASD flush/purge state
- delete on close
- opened by short name
- mixed-case query template
- extended DASD I/O allowed
- match volume ID
- close-context overlay active
- complete dismount
- manage-volume access restriction
- format-unit sent
- deny defrag
- first write seen

### `REPINNED_BCBS`

Tracks BCBs that must remain pinned until IRP completion during abnormal unwinding.

- Fixed array size: `REPINNED_BCBS_ARRAY_SIZE` = 4.
- Chains through `Next` when more BCBs are needed.

### `IRP_CONTEXT`

Per-originating-IRP context used by FSD/FSP paths.

Fields:

- Node identity.
- Work queue item.
- Originating IRP.
- Real device.
- VCB for exception handling.
- Major/minor function.
- `PinCount`.
- Flags controlling wait/write-through/recursive/FSP/user I/O behavior.
- `ExceptionStatus`.
- Noncached I/O context pointer.
- Embedded `REPINNED_BCBS`.

### `IRP_CONTEXT_FLAG_*`

Defines request behavior flags:

- disable dirty
- wait allowed
- write through
- disable write through
- recursive call
- disable popups
- deferred write
- verify read
- stack I/O context
- in FSP
- user I/O
- disable raise
- override verify
- cleanup breaking oplock
- swapped stack on newer NT targets
- parent by child

### `FAT_IO_CONTEXT`

Context for noncached I/O.

Fields:

- Saved IRP context flags.
- Async multi-run IRP count and master IRP.
- Zero MDL for partial-sector zeroing.
- Union:
  - Async state with held resources, request byte count, file object, nonpaged FCB.
  - Sync event.

### Other Helper Structures

- `IO_RUN`: describes one LBO/VBO/offset/byte-count run for multi-run I/O.
- `DELETE_CONTEXT`: stores file size and first cluster for delete/undelete support.
- `DEFERRED_FLUSH_CONTEXT`: timer/DPC/work item for delayed flush.
- `CLEAN_AND_DIRTY_VOLUME_PACKET`: worker packet for clean/dirty volume marking.
- `PAGING_FILE_OVERFLOW_PACKET`: carries paging-file IRP and FCB when stack is low.
- `EA_RANGE`: pins and describes a range of EA data using an inline BCB array with fallback chain.
- `CLUSTER_TYPE`: classification of FAT cluster entries:
  - available
  - reserved
  - bad
  - last
  - next
- `FAT_CALLOUT_PARAMETERS`: Windows Threshold stack-swapping callout parameters for create handling.

## Research Notes

`fatstruc.h` is the structural backbone of FastFAT. It captures the driver’s object hierarchy:

`FAT_DATA` -> mounted `VCB`s -> tree of `FCB`/`DCB` objects -> per-handle `CCB`s -> per-request `IRP_CONTEXT`s.

The file also documents key architectural constraints: FAT’s 32-bit allocation model, mixed OEM/Unicode name lookup, cache/MM section-object requirements, close deferral, volume dirty tracking, and the split between paged object state and nonpaged state required for kernel callbacks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/fatstruc.h -->