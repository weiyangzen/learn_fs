# Group Research: group_1714_reactos_sources_windows_reactos_ntoskrnl_io_iomgr_iofunc_c_sources__21bc8f593fb4

Scope: `Docs/research_subset_a.md`  
Source tree: `sources/windows/reactos`  
Files read completely: 6 files, 7,157 total lines

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iofunc.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iofunc.c

## Purpose

Implements the ReactOS kernel I/O manager’s generic file, volume, directory, device-control, paging, lock, read, and write entry points. This file is the main syscall-facing IRP construction layer for `Nt*File`, `Io*Information`, paging I/O, and device/filesystem control operations.

## Main Responsibilities

- Converts native APIs such as `NtReadFile`, `NtWriteFile`, `NtQueryInformationFile`, `NtSetInformationFile`, `NtDeviceIoControlFile`, `NtFsControlFile`, and volume information calls into initialized IRPs.
- Handles synchronous file object locking, file object events, caller events, APC/completion-port conflicts, pending waits, and interruption abort paths.
- Chooses buffered I/O, direct I/O with MDLs, or neither I/O based on device flags and IOCTL transfer method.
- Uses Fast I/O opportunistically for device controls, byte-range locks, basic/standard file information, reads, writes, and unlocks.
- Provides special kernel-handled answers for selected metadata such as file position, access/mode/alignment information, `FileFsDeviceInformation`, and `FileFsDriverPathInformation`.
- Implements paging read/write helpers `IoPageRead` and `IoSynchronousPageWrite`, including reserve IRP fallback for paging-file reads.

## Important Internal Helpers

- `IopCleanupAfterException` releases partially built IRPs, system buffers, MDLs, synchronous file locks, events, local events, and file object references after SEH failures.
- `IopFinalizeAsynchronousIo` waits on locally allocated events for async handles, aborts interrupted IRPs, copies the kernel IOSB back to the caller, and frees the event.
- `IopPerformSynchronousRequest` centralizes IRP queuing, operation-count accounting, `IoCallDriver`, deferred completion, synchronous waits, abort-on-alert/APC, and file-object unlock.
- `IopDeviceFsIoControl` is the common implementation behind `NtDeviceIoControlFile` and `NtFsControlFile`.
- `IopQueryDeviceInformation`, `IopGetFileInformation`, and `IopGetBasicInformationFile` provide kernel-mode query helpers.
- `IopOpenLinkOrRenameTarget` opens and validates rename/link target parent directories, checks overwrite rules, and enforces same-device targets.
- `IopGetFileMode`, `IopGetMountFlag`, `IopVerifyDriverObjectOnStack`, and `IopGetDriverPathInformation` synthesize selected query results without dispatching to the FSD.

## Public and Native APIs Covered

Implemented or substantially implemented:

- Paging and kernel helpers: `IoSynchronousPageWrite`, `IoPageRead`, `IoQueryFileInformation`, `IoQueryVolumeInformation`, `IoSetInformation`.
- Control: `NtDeviceIoControlFile`, `NtFsControlFile`.
- Flush and notification: `NtFlushBuffersFile`, `NtNotifyChangeDirectoryFile`.
- Locking: `NtLockFile`, `NtUnlockFile`.
- Directory query: `NtQueryDirectoryFile`.
- File information: `NtQueryInformationFile`, `NtSetInformationFile`.
- Read/write: `NtReadFile`, `NtWriteFile`.
- Volume information: `NtQueryVolumeInformationFile`, `NtSetVolumeInformationFile`.

Explicitly unimplemented stubs:

- `NtQueryEaFile`
- `NtQueryQuotaInformationFile`
- `NtReadFileScatter`
- `NtSetEaFile`
- `NtSetQuotaInformationFile`
- `NtWriteFileGather`
- `NtCancelDeviceWakeupRequest`
- `NtRequestDeviceWakeup`

## Behavior Notes

- User-mode callers are guarded with SEH probing for IOSBs, buffers, strings, offsets, keys, and information structures.
- Noncached read/write paths validate sector-size alignment, buffer alignment, and byte-offset alignment.
- Async file handles require explicit offsets for normal files; named pipes and mailslots are exceptions.
- `FO_SYNCHRONOUS_IO` paths use file-object locking and may use `FileObject->CurrentByteOffset` when caller passes `FILE_USE_FILE_POINTER_POSITION` or no byte offset.
- Completion ports and user APC routines are rejected together on the same request.
- Buffered I/O allocates `AssociatedIrp.SystemBuffer` and sets `IRP_BUFFERED_IO`, `IRP_DEALLOCATE_BUFFER`, and input/output flags as needed.
- Direct I/O allocates MDLs and probes/locks pages with `IoReadAccess` or `IoWriteAccess`.
- `IRP_DEFER_IO_COMPLETION` is used for several file/directory/query paths so this layer can complete immediately returned IRPs itself.
- `FSCTL_DISMOUNT_VOLUME` increments `SharedUserData->DismountCount`.

## Filesystem Relevance

This is the syscall-to-filesystem-driver boundary for ReactOS. Most filesystem-visible IRPs for read/write, metadata query/set, directory enumeration, notifications, byte-range locks, flushes, filesystem controls, and volume controls originate here. It is central for understanding how ReactOS presents Windows-compatible I/O manager behavior to local filesystems and filesystem filters.

## Dependencies and Coupling

Heavy dependencies include object manager handle referencing, file object flags, device stack lookup, Fast I/O dispatch tables, MDL allocation, memory probing/locking, completion ports, shared user data, cache manager counters, VPB mount state, and I/O completion internals.

## Research Notes

- The file is mostly implemented but still has notable syscall gaps around EAs, quota APIs, scatter/gather file I/O, and device wake requests.
- Error cleanup is spread through common helpers plus local SEH blocks; this file is a key place to audit for leak, double-unlock, and stale-event bugs.
- Fast I/O acceptance is conservative for read/write: only direct success-like statuses are accepted before falling back to IRPs.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iofunc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iomdl.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iomdl.c

## Purpose

Implements I/O manager wrappers for MDL allocation, partial MDL construction, and MDL freeing.

## Main APIs

- `IoAllocateMdl`
- `IoBuildPartialMdl`
- `IoFreeMdl`

## Behavior

`IoAllocateMdl` validates nonzero length, rejects allocations with the high bit set, calculates the page span, and either uses a fixed-size MDL lookaside entry for small MDLs up to 23 pages or allocates a variable-size MDL from nonpaged pool. It initializes the MDL with `MmInitializeMdl`, marks fixed-size MDLs with `MDL_ALLOCATED_FIXED_SIZE`, and optionally attaches the MDL to an IRP as primary or secondary buffer.

`IoBuildPartialMdl` derives a target MDL from a source MDL, copies selected source flags, marks the target as `MDL_PARTIAL`, computes `MappedSystemVa`, and copies the relevant PFN array subset.

`IoFreeMdl` prepares the MDL for reuse, then returns fixed-size MDLs to the I/O manager lookaside list or frees pool-backed MDLs with `TAG_MDL`.

## Filesystem Relevance

This file supports direct I/O paths used by filesystem and storage IRPs. In this group, `iofunc.c` calls `IoAllocateMdl` for direct device controls, directory queries, reads, writes, and related user buffer pinning.

## Dependencies and Coupling

Depends on memory manager MDL primitives, I/O manager lookaside list helpers, PFN layout immediately after `MDL`, and pool tag `TAG_MDL`.

## Research Notes

- Small MDLs are optimized through a fixed-size lookaside allocation path.
- Secondary-buffer insertion assumes an existing IRP MDL chain is present before walking `Irp->MdlAddress`.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iomdl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iomgr.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iomgr.c

## Purpose

Initializes the ReactOS I/O manager and defines global I/O manager state, object types, lookaside lists, root object directories, boot partition marking, and top-level I/O subsystem startup sequencing.

## Main Responsibilities

- Defines global I/O manager objects and counters: file/device object types, operation and transfer counters, statistics lock, triage dump storage, and file generic mapping.
- Initializes IRP, MDL, and I/O completion packet lookaside lists globally and per processor.
- Creates object manager types for Adapter, Controller, Device, Driver, IoCompletion, and File objects.
- Creates permanent object directories `\Driver`, `\FileSystem`, and `\FileSystem\Filters`.
- Marks the boot partition device object and stores the boot device for error logging.
- Implements `IoInitSystem`, the high-level boot-time I/O manager initialization sequence.
- Contains an unimplemented `IoInitializeCrashDump` stub.

## Key Functions

- `IopInitLookasideLists` calculates large IRP, small IRP, and MDL sizes; initializes system lookaside lists; configures per-CPU lookaside pointers and IRP float credit.
- `IopCreateObjectTypes` wires object type behavior, including parse/delete/security/query-name callbacks for device, driver, file, and completion objects.
- `IopCreateRootDirectories` creates permanent I/O namespace directories.
- `IopMarkBootPartition` opens the ARC boot device, marks its device object with `DO_SYSTEM_BOOT_PARTITION`, and stores it in `IopErrorLogObject`.
- `IoInitSystem` initializes resources, lists, spin locks, PnP notifications, reserve IRP support, I/O timers, object types, directories, PnP services, WMI, HAL PnP, boot/system drivers, ramdisk boot handling, ARC names, system root, drive letters, and system DLL location.

## Filesystem Relevance

This is the bootstrapping layer that makes the file object type, device object type, filesystem directories, I/O timers, reserve IRPs, and boot volume infrastructure available. Filesystem drivers depend on this setup before they can be loaded, named, attached, and called.

## Dependencies and Coupling

Couples the I/O manager to object manager, executive resources, PnP manager, WMI, HAL, boot loader metadata, ARC name creation, driver loading, ramdisk startup, drive-letter assignment, and process manager system DLL loading.

## Research Notes

- Initialization order is important: object types and directories are created before later driver and filesystem activity.
- Reserve IRP initialization is part of system startup and is later used by paging paths such as `IoPageRead`.
- `IoInitializeCrashDump` is not implemented.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iomgr.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iorsrce.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iorsrce.c

## Purpose

Implements hardware resource and configuration-query support for the ReactOS I/O manager, including legacy hardware registry traversal, configuration information reporting, system partition persistence, legacy resource assignment, and HAL resource map registration.

## Main Responsibilities

- Maintains global `CONFIGURATION_INFORMATION` returned by `IoGetConfigurationInformation`.
- Maps ARC `CONFIGURATION_TYPE` and `IO_QUERY_DEVICE_DATA_FORMAT` values to registry value/key names.
- Traverses `\REGISTRY\MACHINE\HARDWARE\DESCRIPTION\SYSTEM` to implement `IoQueryDeviceDescription`.
- Fetches enabled device interfaces for configuration checks.
- Stores system partition and OS loader path data in `HKLM\SYSTEM\Setup`.
- Handles legacy resource reporting and assignment with conflict detection.
- Writes HAL raw and translated resources into `\Registry\Machine\HARDWARE\RESOURCEMAP`.

## Key Functions

- `IopQueryDeviceDescription` walks controller and peripheral registry keys, collects identifier/configuration/component values, and invokes the caller’s query callback.
- `IopQueryBusDescription` recursively enumerates root and sub-bus keys, matches requested interface type and bus number, then either calls the query callback directly or descends into controller/peripheral lookup.
- `IopFetchConfigurationInformation` calls `IoGetDeviceInterfaces`, counts returned symbolic links, and compares against an expected interface count.
- `IopStoreSystemPartitionInformation` resolves the system partition symbolic link target and writes `SystemPartition` and normalized `OsLoaderPath` registry values.
- `IoGetConfigurationInformation` returns the static global configuration structure.
- `IoReportResourceUsage` is half-implemented: validates resource input, detects conflicts, respects `OverrideConflict`, but does not claim resources in the registry.
- `IopLegacyResourceAllocation` is half-implemented: fixes resource lists against requirements, detects conflicts, but does not persist claims; null requirements return `STATUS_NOT_IMPLEMENTED`.
- `IoAssignResources` rejects inappropriate use by non-legacy PnP device nodes and delegates to legacy allocation.
- `IoQueryDeviceDescription` initializes root registry traversal and query context.
- `IoReportHalResourceUsage` creates volatile resource-map keys and writes `.Raw` and `.Translated` resource-list values.

## Filesystem Relevance

This file is not filesystem-specific, but it is part of the same I/O manager substrate that storage, disk, bus, and filesystem stacks rely on during boot and legacy driver initialization. Resource assignment and hardware description queries affect device discovery paths below filesystems.

## Dependencies and Coupling

Depends on registry syscalls, Unicode string construction, pool allocation, PnP device nodes, resource conflict detection/fixup helpers, device interface enumeration, object symbolic links, and HAL resource descriptors.

## Research Notes

- Resource reporting/assignment is explicitly incomplete where registry claiming should happen.
- `IoQueryDeviceDescription` only proceeds when `BusType` is supplied; missing bus type returns `STATUS_NOT_IMPLEMENTED`.
- The recursive registry traversal allocates and frees many `KEY_*_INFORMATION` buffers; cleanup paths are central to correctness.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iorsrce.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iotimer.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iotimer.c

## Purpose

Implements I/O manager timer support for device objects, wrapping executive timers and dispatching registered per-device timer routines.

## Main State

- `IopTimerLock`
- `IopTimerQueueHead`
- `IopTimerDpc`
- `IopTimer`
- `IopTimerCount`

## Key Functions

- `IopTimerDispatch` runs from the timer DPC, locks the timer list, walks enabled timers, and invokes each timer routine with its device object and context.
- `IopRemoveTimerFromTimerList` removes an I/O timer from the global list and decrements the enabled timer count when needed.
- `IoInitializeTimer` allocates or reuses a device’s `IO_TIMER`, sets routine/context, and inserts it into the global timer queue.
- `IoStartTimer` enables a device timer unless the device extension indicates unload/delete/remove is pending or processed.
- `IoStopTimer` disables an enabled timer and decrements the global count.

## Filesystem Relevance

This is shared I/O infrastructure. Filesystem or storage device objects can register timer callbacks through these APIs for periodic device-level work.

## Dependencies and Coupling

Depends on device object timer fields, device extension lifecycle flags, global I/O timer initialization in `IoInitSystem`, spin locks, DPC timer dispatch, and executive list operations.

## Research Notes

- Timer callbacks are invoked while `IopTimerLock` is held, so callback behavior must be constrained and nonblocking.
- `IoInitializeTimer` inserts into the global timer list each time it is called; callers should avoid repeated initialization patterns that duplicate list entries.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iotimer.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iowork.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iowork.c

## Purpose

Implements I/O manager wrappers around executive work items for device-associated deferred work.

## Key Functions

- `IoAllocateWorkItem` allocates an `IO_WORKITEM`, stores the target device object, and initializes the embedded executive work item to call `IopWorkItemCallback`.
- `IoQueueWorkItem` references the device object, records the caller’s worker routine and context, and queues the work item to the requested work queue.
- `IopWorkItemCallback` invokes the stored worker routine and dereferences the device object after the callback returns.
- `IoFreeWorkItem` frees the work item with pool tag `TAG_IOWI`.

## Filesystem Relevance

Provides the standard deferred execution mechanism for I/O components, including filesystems, filters, and storage drivers that need to run work outside the original call path.

## Dependencies and Coupling

Depends on executive work queues, object referencing for device lifetime protection, nonpaged pool allocation, and `IO_WORKITEM` layout.

## Research Notes

- Device lifetime is protected across queued work by reference/dereference around the queued callback.
- The work item itself is not freed after callback; ownership remains with the caller, which must call `IoFreeWorkItem`.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iowork.c -->