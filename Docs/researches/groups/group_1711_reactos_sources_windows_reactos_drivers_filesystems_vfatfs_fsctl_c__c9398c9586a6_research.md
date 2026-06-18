# Group Research: group_1711_reactos_sources_windows_reactos_drivers_filesystems_vfatfs_fsctl_c__c9398c9586a6

Scope confirmed against `Docs/research_subset_a.md`. All 15 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/fsctl.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/fsctl.c

## Purpose

`fsctl.c` implements VFAT file-system-control handling: volume recognition, mount, verify, dirty-state queries/updates, lock/unlock, dismount, retrieval pointers, and filesystem statistics. It is the mount-time bridge between raw block devices, parsed FAT/FATX layout metadata, cache-manager stream setup, and the live VCB/VPB state used by the rest of `vfatfs`.

## Main Runtime Flow

- `VfatHasFileSystem()` probes a target block device with `IOCTL_DISK_GET_DRIVE_GEOMETRY` and, for fixed/removable media, `IOCTL_DISK_GET_PARTITION_INFO`; it then reads sector zero and validates FAT12/FAT16/FAT32 boot-sector fields or, if ordinary FAT recognition fails on a valid partition, FATX16/FATX32 Xbox boot-sector fields.
- FAT recognition computes `FATINFO`: FAT start/count/length, root/data starts, bytes and sectors per cluster, cluster count, FAT type, root cluster, volume ID/label, media kind, total sectors, and FAT32 FSInfo sector.
- `ReadVolumeLabel()` scans root-directory entries either through the root FCB/cache path after mount or by direct disk reads during verify. It supports both FAT volume-label entries and FATX volume-label entries.
- `VfatMount()` validates that the mount request targets the global file system device, recognizes the media, creates the per-volume filesystem device, allocates a hash table sized by FAT type, initializes VCB state/resources/statistics, binds the VPB, sets FAT-specific callback functions, creates stream FCBs for the FAT and volume, initializes the FAT cache map, counts free clusters, reads label/serial, marks clean volumes dirty, initializes notifications, and emits `FSRTL_VOLUME_MOUNT`.
- `VfatVerify()` rechecks media change state and compares the newly parsed `FATINFO` and label against the mounted VPB. It returns `STATUS_WRONG_VOLUME` when the disk no longer matches.
- `VfatFileSystemControl()` dispatches `IRP_MN_MOUNT_VOLUME`, `IRP_MN_VERIFY_VOLUME`, and user/kernel FSCTLs.

## FSCTL Support

- Implemented: `FSCTL_GET_RETRIEVAL_POINTERS`, `FSCTL_IS_VOLUME_DIRTY`, `FSCTL_MARK_VOLUME_DIRTY`, `FSCTL_LOCK_VOLUME`, `FSCTL_UNLOCK_VOLUME`, `FSCTL_DISMOUNT_VOLUME`, and `FSCTL_FILESYSTEM_GET_STATISTICS`.
- Stubbed as invalid requests: `FSCTL_GET_VOLUME_BITMAP` and `FSCTL_MOVE_FILE`.

## Important Details

- FAT12/16 root directories are treated specially because they are fixed regions rather than normal cluster chains.
- FATX detection is attempted only after ordinary FAT detection fails and partition information is considered valid.
- Dirty-bit handling marks a clean mounted volume dirty immediately and records `VCB_CLEAR_DIRTY` so clean lock/dismount/shutdown paths can clear the bit later.
- Volume locking normally requires `OpenHandleCount == 1`, but there is a narrow boot-volume hack allowing autochk-era locking when only a small number of directory handles are open.
- Mount failure cleanup tears down cache maps, stream file objects, FCBs, statistics, spare VPB, and the partially created device.

## Research Notes

This file is central to the VFAT lifecycle. When studying correctness, focus on recognition field validation, VPB ownership transitions, dirty-bit ordering, and the lock/dismount relationship with `misc.c` dismount cleanup and `shutdown.c` clean shutdown.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/fsctl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/iface.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/iface.c

## Purpose

`iface.c` contains `DriverEntry()` for the ReactOS VFAT/FATX filesystem driver. It creates the global filesystem device, initializes `VfatGlobalData`, installs dispatch vectors, cache-manager callbacks, fast I/O support, lookaside lists, close/dismount global state, and registers the filesystem with the I/O manager.

## Main Contents

- Creates the global device named `\FatX` with `FILE_DEVICE_DISK_FILE_SYSTEM`.
- Stores global driver/device pointers, processor count, and optional corruption-break flag.
- Initializes delayed close support, `DO_DIRECT_IO`, major-function dispatch, cache-manager callbacks, fast I/O, lookaside lists, and mounted-volume tracking.
- Registers the filesystem with `IoRegisterFileSystem()`.
- Under `KDBG`, registers `vfatKdbgHandler()`.

## Integration

This file is the entry point for all later files in the VFAT driver. `misc.c` owns the common request builder/dispatcher that most major functions enter through, while `fsctl.c`, `rw.c`, `volume.c`, `pnp.c`, and others implement the actual per-major-function behavior.

## Research Notes

Unload is explicitly disabled (`DriverUnload = NULL`). Failure handling is narrow: if close work-item allocation fails, the global device is deleted and initialization aborts.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/iface.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/kdbg.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/kdbg.c

## Purpose

`kdbg.c` implements optional KDBG command support for inspecting VFAT state at runtime. The whole command handler is compiled only under `KDBG`.

## Commands

- `?fat.vols`: walks `VfatGlobalData->VolumeListHead` and prints each mounted volume device pointer and VCB pointer.
- `?fat.files <volume-or-vcb-pointer>`: matches a volume device or VCB pointer and prints each FCB's reference count, open count, cleanup/close/delayed-close flags, file object, and path.
- `?fat.setdbgfile [path]`: clears or sets the global Unicode `DebugFile` from an ANSI debugger argument.

## Important Details

The handler only claims commands beginning with `?fat.` and uses `DPRINT1` for debugger-visible output. It does not acquire the global volume-list resource or per-volume FCB-list locks while walking state, so it is diagnostic rather than synchronized production logic.

## Research Notes

This file is useful when tracing FCB lifetime bugs because the printed flags line up with KDBG-only FCB flags declared in `vfat.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/kdbg.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/misc.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/misc.c

## Purpose

`misc.c` provides the VFAT common IRP dispatch framework, request queuing, user-buffer locking, pass-through device control, byte-range lock control, and final dismount cleanup. It is the central control plane between `DriverEntry()` and the per-operation modules.

## Dispatch Path

- `VfatBuildRequest()` allocates a `VFAT_IRP_CONTEXT` from the global lookaside list and passes it to `VfatDispatchRequest()`.
- `VfatAllocateIrpContext()` captures device, VCB, stack location, major/minor functions, file object, completion flags, event, reference count, and priority boost.
- `VfatDispatchRequest()` enters the filesystem, switches by major function, calls the appropriate module routine, then completes, queues, or frees the context.
- Major-function targets include close/create/read/write/fsctl/query/set info/directory/query/set volume/lock/device control/cleanup/flush/PnP.

## Queuing and Deferred Execution

- `VfatQueueRequest()` marks IRPs pending, sets `IRPCONTEXT_CANWAIT`, and queues work to `CriticalWorkQueue`.
- It limits posted requests per volume and stores excess work on a per-volume overflow queue guarded by `OverflowQueueSpinLock`.
- `VfatDoRequest()` runs queued work and drains overflow items in the same worker.
- `VfatHandleDeferredWrite()` is the callback used by cache-manager deferred writes.

## Buffer and Control Helpers

- `VfatLockControl()` rejects the global device and directories, then delegates file-lock IRPs to `FsRtlProcessFileLock()`.
- `VfatDeviceControl()` forwards the IRP to the storage device without completing it in VFAT.
- `VfatGetUserBuffer()` maps an MDL if present, otherwise returns `Irp->UserBuffer`.
- `VfatLockUserBuffer()` allocates an MDL and probes/locks pages, with SEH cleanup on probe failure.

## Dismount Cleanup

`VfatCheckForDismount()` decides whether a VCB can be deleted using VPB reference count and open-handle count. Full deletion uninitializes internal root/volume/FAT stream objects, asserts no overflow work remains, removes the volume from the global list, uninitializes notifications, frees stats/resources/VPB state, dereferences the storage device, and deletes the volume device.

## Research Notes

This file controls request lifetime and is critical for deadlock and use-after-free analysis. The queue overflow mechanism exists specifically to keep cache-manager interactions from consuming too many worker threads for one volume.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/pnp.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/pnp.c

## Purpose

`pnp.c` contains the VFAT PnP major-function handler.

## Behavior

`VfatPnp()` returns `STATUS_NOT_IMPLEMENTED` for query remove, surprise removal, remove, and cancel remove. For all other PnP minor functions, it skips the current IRP stack location, clears `IRPCONTEXT_COMPLETE`, and forwards the IRP to the lower storage device.

## Research Notes

Removal handling is effectively incomplete. For non-removal PnP requests, VFAT behaves as a pass-through layer and relies on the lower device stack for completion.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/pnp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/rw.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/rw.c

## Purpose

`rw.c` implements VFAT read/write handling, including cluster-chain translation, cached I/O through the cache manager, noncached/raw disk I/O, page-file forwarding, byte-range lock checks, stack-overflow read posting, file extension, write metadata updates, and I/O statistics.

## Cluster Helpers

- `NextCluster()` returns the next logical cluster. FAT12/16 root-directory sentinel cluster `1` advances by sectors-per-cluster; other chains call either normal or extending FAT callbacks.
- `OffsetToCluster()` converts a file offset to a cluster number by walking from the first cluster. It also handles FAT12/16 root-directory cluster `1` by mapping directly into the root directory's fixed sector range.

## Low-Level Read/Write Data Paths

- `VfatReadFileData()` handles FAT stream reads, volume reads, FAT12/16 root-directory reads, and normal file reads grouped by contiguous clusters.
- `VfatWriteFileData()` handles volume writes, writes FAT stream data to every FAT copy, handles FAT12/16 root-directory writes, and groups contiguous clusters for normal file writes.

## Read Dispatch

`VfatRead()` rejects reads on the global filesystem device and non-paging directory reads. Page-file reads are converted to storage-device offsets and forwarded directly down the stack. Noncached, paging, and volume reads must be sector aligned. Normal cached reads go through `CcCopyRead()`; noncached reads lock the user buffer and call `VfatReadFileData()`.

## Write Dispatch

`VfatWrite()` rejects the global filesystem device and non-paging directory writes. Page-file writes are offset-adjusted and forwarded directly to storage. FAT stream, volume stream, and FAT12/16 root-directory writes cannot extend beyond current file size. Cached writes use `CcCanIWrite()`, `CcDeferWrite()`, `CcZeroData()`, and `CcCopyWrite()`; noncached writes lock the user buffer and call `VfatWriteFileData()`.

## Important Details

- The last-cluster cache is protected by `Fcb->LastMutex` and accelerates sequential I/O.
- Optional `DEBUG_VERIFY_OFFSET_CACHING` recomputes cluster positions and bugchecks on cache mismatch.
- Noncached I/O rounds read limits to sector-rounded file sizes.
- Successful non-paging file writes update DOS timestamps, mark the FCB dirty, and report notifications.

## Research Notes

This file is the main place to study data-path correctness. Important edge cases include FAT copy writes, EOF/sector rounding, file-extension ordering, cached/noncached coherence, and the direct page-file bypass.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/rw.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/shutdown.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/shutdown.c

## Purpose

`shutdown.c` handles `IRP_MJ_SHUTDOWN` for the VFAT filesystem. It flushes all mounted volumes, clears dirty bits for clean shutdown where appropriate, passes shutdown to the lower storage device, and optionally checks for dismount.

## Main Flow

- `VfatDiskShutDown()` builds a synchronous `IRP_MJ_SHUTDOWN` request for the lower storage device, calls the driver, waits if pending, and returns the final status.
- `VfatShutdown()` accepts shutdown only on the global filesystem device object, marks shutdown started, walks the mounted-volume list, flushes each volume, clears dirty state when eligible, sends shutdown to storage, optionally checks for dismount under `ENABLE_SWAPOUT`, and completes the original IRP.

## Important Details

There is a FIXME noting that new mount requests should be blocked during shutdown. Global resource cleanup is also marked FIXME.

## Research Notes

This file ties into dirty-bit semantics established during mount and lock/dismount. Clean shutdown depends on the volume having been marked with `VCB_CLEAR_DIRTY` during mount or lock-time cleanup.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/string.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/string.c

## Purpose

`string.c` provides small VFAT pathname/name validation helpers.

## Contents

- `long_illegals` lists characters invalid in long filenames: `"*\\<>/?:|`.
- `vfatIsLongIllegal(WCHAR c)` returns whether a character appears in that invalid-character set.
- `IsDotOrDotDot(PCUNICODE_STRING Name)` returns true for the single-component names `.` and `..`.

## Research Notes

Despite its `PURPOSE` comment saying "Volume routines", this file is a name-helper module. The prototype for `vfatSplitPathName()` is in `vfat.h`, but that function is not implemented in this file.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/string.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/vfat.h -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/vfat.h

## Purpose

`vfat.h` is the shared private header for the ReactOS VFAT/FATX filesystem driver. It defines on-disk FAT/FATX structures, core in-memory VCB/FCB/CCB/IRP-context structures, dispatch callback tables, flags, pool tags, inline helpers, and prototypes for the driver modules.

## On-Disk Structures and Constants

It defines packed boot-sector structures for FAT12/FAT16, FAT32, FATX, and FAT32 FSInfo; FAT/FATX dirent layouts; long filename slots; EA-related structures; `DIR_ENTRY`; FAT type constants; and macros for deleted/end/volume/long directory-entry tests.

## Core In-Memory State

- `FATINFO` stores parsed volume layout: sector/cluster sizes, FAT location/count/length, root/data starts, root cluster, cluster count, type, total sectors, volume ID/label, media kind, and FSInfo sector.
- `DEVICE_EXTENSION`/`VCB` stores volume resources, FCB list/hash table, volume/storage devices, FAT stream, FATINFO, free-cluster state, stream FCBs, statistics, overflow queue, FAT callbacks, FATX/date mode, notify state, VPBs, and directory-entry dispatch callbacks.
- `VFAT_GLOBAL_DATA` stores global driver/device pointers, volume list, lookaside lists, fast I/O table, cache-manager callbacks, delayed-close state, close worker, and shutdown flag.
- `VFATFCB` stores common FCB header, resources, on-disk dirent, names, ref/open counts, parent/list/hash state, share access, file locks, last-cluster cache, and delayed close context.
- `VFATCCB` stores current offset, flags, directory enumeration index, and search pattern.
- `VFAT_IRP_CONTEXT` stores the active IRP, device/VCB, flags, work item, stack location, major/minor function, file object, refcount, event, and priority boost.

## Inline Helpers and Flags

The header defines VCB, FCB, and IRP-context flags; wrappers for FAT/FATX directory dispatch; `VfatMarkIrpContextForQueue()`; helpers for directory/read-only/FATX checks; change notification; and per-processor statistic updates.

## API Surface

The header declares cross-module functions for block I/O, cleanup/close/create, directory enumeration and date conversion, dirent access, directory writes and moves, EA setting, fast I/O callbacks, FAT cluster operations and dirty-bit operations, FCB lifecycle/table lookup, file information, flush, fsctl, driver entry, dispatch helpers, PnP, read/write, shutdown, string helpers, and volume query/set.

## Research Notes

`vfat.h` is the best map of module boundaries. It also reveals architectural constraints that appear throughout the C files: FATX behavior is selected through callbacks and flags, FAT12/16 root directories are special, volume lifecycle depends on VPB swapping, and most request deferral is carried by `VFAT_IRP_CONTEXT`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/vfat.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/volume.c -->
# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/volume.c

## Purpose

`volume.c` implements `IRP_MJ_QUERY_VOLUME_INFORMATION` and `IRP_MJ_SET_VOLUME_INFORMATION` for VFAT. It reports volume label/serial/creation time, filesystem attributes, allocation size/free space, device characteristics, and supports setting the volume label.

## Query Helpers

- `FsdGetFsVolumeInformation()` fills `FILE_FS_VOLUME_INFORMATION` from the VPB serial/label and volume FCB creation time.
- `FsdGetFsAttributeInformation()` reports the filesystem name as `FAT`, `FAT32`, or `FATX`; sets `FILE_CASE_PRESERVED_NAMES | FILE_UNICODE_ON_DISK`; and reports maximum component length 255.
- `FsdGetFsSizeInformation()` and `FsdGetFsFullSizeInformation()` call `CountAvailableClusters()` and report allocation-unit geometry and free space.
- `FsdGetFsDeviceInformation()` reports `FILE_DEVICE_DISK` and device characteristics.

## Label Setting

`FsdSetFsLabelInformation()` validates label length, converts the Unicode label to OEM bytes, builds a FAT or FATX volume-label dirent, opens the root FCB cache, scans for an existing volume-label entry, updates it or creates a new entry, marks pinned cache data dirty, and updates the VPB label in memory.

## Dispatch Behavior

`VfatQueryVolumeInformation()` acquires `DirResource` shared and dispatches by `FS_INFORMATION_CLASS`. `VfatSetVolumeInformation()` acquires `DirResource` exclusive and currently supports only `FileFsLabelInformation`.

## Research Notes

Label mutation edits the root directory directly through the cache manager. Query paths rely on VPB state populated during mount, while size/free-space queries force cluster counting through FAT-layer support.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/vfatfs/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/debug.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/debug.c

## Purpose

`io/debug.c` provides diagnostic dump helpers for ReactOS I/O and PnP manager state. It prints CM resource lists, I/O resource requirements, device node state names, and recursive device-node trees.

## Resource Dumping

- `PipDumpCmResourceDescriptor()` prints one `CM_PARTIAL_RESOURCE_DESCRIPTOR`.
- `PipGetNextCmPartialDescriptor()` advances over fixed-size descriptors and variable-length device-specific descriptors.
- `PipDumpCmResourceList()` walks a `CM_RESOURCE_LIST`.
- `PipDumpIoResourceDescriptor()` prints one `IO_RESOURCE_DESCRIPTOR`.
- `PipDumpResourceRequirementsList()` walks all alternative resource lists in an `IO_RESOURCE_REQUIREMENTS_LIST`.

## Device-Node Dumping

- `PipGetDeviceNodeStateName()` maps `PNP_DEVNODE_STATE` values to readable strings.
- `PipDumpArbiters()` is present but unimplemented.
- `PipDumpDeviceNode()` prints device-node identity and optional allocated, boot, required, translated, and recursive child information.
- `PipDumpDeviceNodes()` starts from a caller-provided node or `IopRootDeviceNode`.

## Important Details

Most routines honor `DebugLevel`: level `0` always dumps, while nonzero levels compile out under `NDEBUG`. The code is diagnostic and does not modify I/O manager state.

## Research Notes

This file is not filesystem code, but it is relevant for storage and PnP investigation because it exposes resource allocation and device-tree inspection tools used around device discovery and boot storage debugging.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/adapter.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/adapter.c

## Purpose

`adapter.c` contains I/O manager wrapper state for HAL adapter APIs and implements `IoAllocateAdapterChannel()`.

## Contents

It defines `IoAdapterObjectType`, `IoDeviceHandlerObjectType`, and `IoDeviceHandlerObjectSize`. `IoAllocateAdapterChannel()` fills the device object's embedded wait context block with the device object, caller context, and current IRP, then delegates to `HalAllocateAdapterChannel()`.

## Research Notes

This is a thin compatibility wrapper around HAL DMA adapter channel allocation. The important state transfer is from `DeviceObject->CurrentIrp` and caller context into `DeviceObject->Queue.Wcb` before delegating to HAL.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/adapter.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/arcname.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/arcname.c

## Purpose

`arcname.c` initializes ARC namespace symbolic links during boot. It maps loader ARC names such as disk, partition, and CD-ROM paths to NT device names, records system partition information, and reassigns `\SystemRoot`.

## Global State

- `IoArcHalDeviceName`: Unicode `\ArcName\...` for the firmware system/HAL partition.
- `IoArcBootDeviceName`: Unicode `\ArcName\...` for the OS boot partition.
- `IoLoaderArcBootDeviceName`: paged copy of the loader boot ARC name.

## ARC Name Creation

- `IopCreateArcNames()` builds global HAL and boot ARC Unicode names, handles remote boot, then creates disk ARC names first and CD ARC names if the boot device is not found.
- `IopCreateArcNamesCd()` enumerates CD-ROMs through device-interface links or `\Device\CdRomN`, reads 2048 bytes at offset `0x8000`, computes a checksum, and maps the matching boot ARC name to the CD-ROM device.
- `IopCreateArcNamesDisk()` enumerates disks through device-interface links or `\Device\HarddiskN\Partition0`, queries geometry and layout, handles EZ-Drive MBR adjustment, reads the first sector checksum, matches MBR signatures or GPT GUIDs, and creates ARC symlinks for whole disks and partitions.

## SystemRoot and Signature Helpers

- `IopReassignSystemRoot()` resolves the boot ARC symlink and replaces `\SystemRoot` with a permanent symlink to the resolved NT target plus loader boot path.
- `IopVerifyDiskSignature()` compares loader MBR signatures or GPT disk GUIDs against `DRIVE_LAYOUT_INFORMATION_EX`.

## Important Details

The code accommodates both MountMgr-style enabled devices and fallback legacy device names. It warns on duplicate-signature-like conditions where signature matches but checksum differs. Most functions are `INIT` code except `IopVerifyDiskSignature()`.

## Research Notes

This file is boot-storage glue. For filesystem research, it explains how early boot partition names become stable NT object-manager symbolic links that later filesystem mounts can consume.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/arcname.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/bootlog.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/bootlog.c

## Purpose

`bootlog.c` implements ReactOS boot driver logging. It records load success/failure entries under the registry during boot and can later write them to `\SystemRoot\rosboot.log`.

## State

It tracks whether to create a boot log, whether registry logging is enabled, whether file logging completed, the numeric entry count, and an `ERESOURCE` for serialization.

## Main Functions

- `IopInitBootLog()` initializes the resource and optionally starts logging.
- `IopStartBootLog()` enables logging and requests later file creation.
- `IopStopBootLog()` disables accepting new entries.
- `IopBootLog()` writes "Loaded driver" or "Did not load driver" entries under `CurrentControlSet\BootLog`.
- `IopWriteLogFile()` appends optional UTF-16 text plus CRLF to `\SystemRoot\rosboot.log`.
- `IopCreateLogFile()` supersedes `rosboot.log` and writes a UTF-16 BOM.
- `IopSaveBootLogToFile()` creates the file, reads numeric registry values from `BootLog`, appends each value to the file, deletes each registry value, and enables the log-file flag.

## Important Details

Registry and file paths are kernel object-manager paths. File content is UTF-16. There is a locking issue in the current implementation: `IopSaveBootLogToFile()` acquires `IopBootLogResource` and calls `IopCreateLogFile()`, which also acquires the same resource without releasing it in that function.

## Research Notes

This file is not a filesystem implementation, but it exercises kernel file creation/writes during boot and depends on the storage/filesystem stack becoming available enough for `\SystemRoot\rosboot.log`.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/bootlog.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/controller.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/controller.c

## Purpose

`controller.c` implements I/O manager controller object wrappers over kernel device queues.

## Main Functions

- `IoAllocateController()` requires `DISPATCH_LEVEL`, stores caller context and execution routine in the device object's WCB, queues it, and immediately calls the execution routine if the controller queue was idle.
- `IoCreateController()` creates a kernel controller object with optional extension space, inserts it into the object manager, initializes type/size/extension/queue state, and returns it.
- `IoDeleteController()` dereferences the controller object.
- `IoFreeController()` removes the next queued device, invokes its stored execution routine, and recursively frees again if requested.

## Important Details

The controller extension is placed immediately after the `CONTROLLER_OBJECT`. Queue entries are recovered back to `DEVICE_OBJECT` through `DEVICE_OBJECT.Queue.Wcb.WaitQueueEntry`.

## Research Notes

This is legacy controller-serialization infrastructure. It is relevant to storage-driver scheduling concepts but independent from the VFAT driver code in this batch.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/controller.c -->