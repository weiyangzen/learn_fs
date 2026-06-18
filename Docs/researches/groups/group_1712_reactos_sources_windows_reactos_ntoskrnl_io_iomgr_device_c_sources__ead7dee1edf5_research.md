# Group Research: group_1712_reactos_sources_windows_reactos_ntoskrnl_io_iomgr_device_c_sources__ead7dee1edf5

Scope checked against `Docs/research_subset_a.md`: `sources/windows/reactos` is included. All four listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/device.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/device.c

This file implements ReactOS I/O manager device-object management: creating, deleting, attaching, detaching, enumerating, and resolving device objects, plus shutdown notification lists and legacy StartIo queue handling.

Key behavior:
- `IoCreateDevice` builds a `DEVICE_OBJECT` plus caller extension and `EXTENDED_DEVOBJ_EXTENSION`, assigns default security, initializes power-manager state, creates VPBs for disk/tape/CD-like devices, initializes device queues, inserts the object, references the owning driver, and links it into `DriverObject->DeviceObject`.
- `IoDeleteDevice`, `IopDereferenceDeviceObject`, and `IopUnloadDevice` coordinate delete-pending state, shutdown deregistration, timer removal, security descriptor release, device-list unlinking, driver unload callbacks, and temporary object conversion.
- `IopAttachDeviceToDeviceStackSafe` attaches a source device above the current top of a target stack under `LockQueueIoDatabaseLock`, rejecting targets that are initializing, unloading, deleting, or being removed. Public attach APIs delegate to it.
- Stack queries include `IoGetAttachedDevice`, `IoGetAttachedDeviceReference`, `IoGetDeviceAttachmentBaseRef`, `IoGetLowerDeviceObject`, `IoGetRelatedDeviceObject`, `IoGetBaseFileSystemDeviceObject`, and target-device relation lookup through a synchronous PnP query.
- Shutdown support keeps first-chance and last-chance shutdown notification lists and sends `IRP_MJ_SHUTDOWN` in `IoShutdownSystem`; phase 1 also shuts down disk, CD-ROM, and tape filesystem queues.
- StartIo support manages keyed and non-keyed device queues, cancel routines, `CurrentIrp`, and deferred StartIo serialization through `StartIoCount`, `StartIoFlags`, and `StartIoKey`.
- Default device security uses predefined public/system DACLs, with special handling for filesystem devices, storage devices, floppy characteristics, admins, and CD-ROM world-read access.

Integration points:
- Depends on object manager APIs (`ObCreateObject`, `ObInsertObject`, references, temporary objects), power manager (`PoInitializeDeviceObject`, `PoVolumeDevice`, `PoRemoveVolumeDevice`), VPB helpers, PnP device-node helpers, and global I/O database locking.
- Driver initialization in `driver.c` calls `IopReadyDeviceObjects` to clear `DO_DEVICE_INITIALIZING` after `DriverEntry`.
- Filesystem shutdown queues are external globals handled by base filesystem shutdown code.

Research notes:
- `IoEnumerateDeviceObjectList` assumes `DriverObject->DeviceObject` is non-NULL; the initial count and first dereference would be unsafe for a driver with no devices.
- `IopDereferenceDeviceObject` accepts `ForceUnload` but asserts it is false, so forced unload is not implemented through that parameter.
- Attach and stack verification take the I/O database lock; `IoDetachDevice` directly modifies attachment fields in this file, so callers must provide any required synchronization.
- Shutdown notification registration uses a single `DO_SHUTDOWN_REGISTERED` flag even though entries can be first-chance or last-chance and removal scans both lists.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/device.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/deviface.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/deviface.c

This file implements Plug and Play device-interface registration, lookup, aliasing, enumeration, registry-key access, and interface enable/disable notifications.

Key behavior:
- Device interface symbolic links use either kernel `\??\` or user `\\?\` prefixes and encode device instance paths by replacing backslashes with `#`, followed by the interface class GUID and optional reference string.
- `IopBuildSymbolicLink` constructs symbolic links from a device instance string, GUID string, optional reference string, and prefix mode.
- `IopSeparateSymbolicLink` parses a link into prefix, munged device string, GUID string, optional reference string, and optional GUID value.
- Registry state is stored below `HKLM\System\CurrentControlSet\Control\DeviceClasses\{GUID}` using munged symbolic-link device keys and reference-string instance subkeys.
- `IoRegisterDeviceInterface` validates the PDO and reference string, creates the class/device/reference registry keys, writes `DeviceInstance` and `SymbolicLink`, creates the kernel symbolic link to the PDO object name, and returns the interface symbolic link.
- `IoGetDeviceInterfaces` enumerates class keys, optionally filters by a specific PDO `InstancePath`, skips `Control`, optionally filters inactive interfaces via `Control\Linked`, reads `SymbolicLink`, normalizes its prefix to `\??\`, and returns a double-null-terminated list.
- `IoOpenDeviceInterfaceRegistryKey` opens or creates the per-interface `Device Parameters` key.
- `IoGetDeviceInterfaceAlias` uses the existing interface’s `DeviceInstance` and reference string with another class GUID, then verifies the alias instance key exists.
- `IoSetDeviceInterfaceState` writes volatile `Control\Linked`, reconstructs the device instance from the symbolic link, resolves the PDO, and sends arrival/removal notifications through `PiNotifyDeviceInterfaceChange` and `IopQueueDeviceChangeEvent`.

Integration points:
- Shares `IopGetDeviceObjectFromDeviceInstance` with driver-loading code.
- Uses registry helper APIs such as `IopOpenRegistryKeyEx`, `IopCreateRegistryKeyEx`, `IopGetRegistryValue`, and PnP registry string conversion.
- Emits PnP/device-change events consumed by the wider kernel PnP notification path.
- Creates symbolic links through `IoCreateSymbolicLink` and updates existing links on collision.

Research notes:
- Several paths manually duplicate symbolic-link parsing and munging instead of always using the helper, so format changes would need careful synchronization.
- `IopBuildSymbolicLink` duplicates the munged device string but does not free it in the visible success or failure paths after allocation.
- `IopOpenOrCreateSymbolicLinkSubKeys` can call `ZwDeleteKey(DeviceKeyHandle)` on failure when `Create` is true before confirming the handle is non-NULL.
- `IoGetDeviceInterfaces` has cleanup-sensitive `continue` paths while filtering by PDO that can skip closing/freeing the current device-key state.
- `IoRegisterDeviceInterface` contains multiple early-return error paths after allocations or key opens; the visible code does not consistently free the GUID string from `RtlStringFromGUID` or close/free all intermediate resources.
- Enabling/disabling an interface changes registry state and sends notifications; the symbolic link itself is created during registration and is not deleted on disable in this file.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/deviface.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/driver.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/driver.c

This file implements driver-object lifecycle management, boot/system driver initialization, dynamic driver load/unload, reinitialization callbacks, and driver object extensions.

Key behavior:
- `IopGetDriverNames` derives the kernel driver object name from the service key, using `ObjectName` when present or constructing `\Driver\<ServiceName>` / `\FileSystem\<ServiceName>` from the service `Type`.
- `IopNormalizeImagePath` normalizes empty or relative image paths to `\SystemRoot\System32\drivers\<service>.sys` or `\SystemRoot\<relative>`.
- `IopInitializeDriverModule` creates a permanent driver object for a loaded image, initializes dispatch entries to `IopInvalidDeviceRequest`, copies service/driver names, calls `DriverEntry`, fixes illegal NULL major functions, frees init pages, marks devices ready, and optionally runs reinitialization.
- Boot-driver support resolves imports for loader-provided modules, derives service names from module filenames, opens service keys, initializes built-in boot drivers in group/tag order, processes service `Enum` entries, queues AddDevice work for matching PDOs, and triggers root/device-tree enumeration.
- `IopInitializeSystemDrivers` performs a synchronous device-tree enumeration, loads registry-selected system drivers with `ZwLoadDriver`, and queues another tree enumeration.
- `IopUnloadDriver` enforces `SeLoadDriverPrivilege`, resolves the driver object, validates the service image path, marks devices unload-pending, checks for references or attached devices, calls `DriverUnload` through the system-process worker path, and makes the driver object temporary.
- `IoCreateDriver` creates built-in driver objects with optional generated names, initializes default dispatchers, calls the supplied initialization function, and fixes NULL dispatch entries.
- Reinitialization APIs enqueue boot and normal reinit callbacks; `IopReinitializeDrivers` and `IopReinitializeBootDrivers` drain those queues, increment the driver extension count, clear registration flags, and call the callbacks.
- Driver object extension APIs allocate and find client extensions keyed by caller-provided identification address.
- `NtLoadDriver` and `NtUnloadDriver` are the public system calls; actual load/unload work is marshaled to `PsInitialSystemProcess` when needed by `IopDoLoadUnloadDriver`.

Integration points:
- Uses memory manager image loading/unloading (`MmLoadSystemImage`, `MmUnloadSystemImage`, `MmFreeDriverInitialization`) and import resolution.
- Coordinates closely with PnP globals/actions (`PnpSystemInit`, `PnPBootDriversLoaded`, `PiQueueDeviceAction`, `PiPerformSyncDeviceAction`, `PiEnumerationFinished`).
- Calls `IopReadyDeviceObjects` from `device.c` after successful image-driver initialization.
- Uses registry service configuration for names, type, image path, group order, tag order, and enumerated device instances.

Research notes:
- `IopUnloadDriver` sets `DOE_UNLOAD_PENDING` on each device before proving unload is safe; if references or attached devices prevent unload, it returns success without visibly clearing those flags.
- `IopLoadDriver` calls `IopNormalizeImagePath(&ImagePath, NULL)`; if a registry `ImagePath` value is an empty string, the empty-path branch expects a non-NULL service name.
- `IoAllocateDriverObjectExtension` and `IoGetDriverObjectExtension` raise IRQL to DPC level but do not take a visible interprocessor lock around the linked list, so concurrent extension operations may need external serialization.
- `IoCreateDriver` does not visibly call `IopReadyDeviceObjects` after successful initialization, unlike `IopInitializeDriverModule`.
- Boot initialization includes setup-loader hacks and assumes certain registry/loader invariants; several failure paths return early after partial setup.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/driver.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/error.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/error.c

This file implements I/O error-log packet allocation, queuing, delivery to the Event Log LPC port, and hard-error mode stubs.

Key behavior:
- Error log entries are capped by `IOP_MAXIMUM_LOG_SIZE` and tracked through `IopTotalLogSize`, `IopErrorLogListHead`, and `IopLogListLock`.
- `IoAllocateErrorLogEntry` accepts either a device object or driver object, validates packet size, references the associated device/driver objects, allocates a nonpaged `ERROR_LOG_ENTRY`, and returns the embedded `IO_ERROR_LOG_PACKET`.
- `IoWriteErrorLogEntry` timestamps the entry, inserts it into the global list, and starts `IopLogWorker` if no worker is running.
- `IopLogWorker` connects to the Event Log port, removes queued entries, builds `ELF_API_MSG` / `IO_ERROR_LOG_MESSAGE` payloads, adds driver and device names plus caller strings, sends them with `ZwRequestPort`, and frees entries on success.
- If port connection or send fails, the worker schedules a delayed retry through a timer/DPC path and requeues the current entry on send failure.
- `IoFreeErrorLogEntry` releases the referenced objects and subtracts the entry size from the global total.
- `IoRaiseHardError` queues a kernel APC to the requesting thread unless hard errors are disabled; the APC target `IopRaiseHardError` is currently unimplemented and completes the IRP with `STATUS_NOT_IMPLEMENTED`.
- `IoRaiseInformationalHardError` is unimplemented and returns `FALSE`.
- `IoSetThreadHardErrorMode` toggles `PsGetCurrentThread()->HardErrorsAreDisabled` and returns the previous enabled state.

Integration points:
- Sends error log messages to the event-log subsystem port named by `ELF_PORT_NAME`.
- Uses object-manager names for driver and device display strings.
- IRP hard-error handling interacts with thread APC state, `VPB`, real device object, and request completion.

Research notes:
- The log-size admission check in `IoAllocateErrorLogEntry` is noted by the code as concurrency-sensitive; it checks `IopTotalLogSize + LogEntrySize` before the interlocked add.
- The queue uses `InsertHeadList` and `RemoveHeadList`, so delivery order is newest-first rather than FIFO.
- Hard-error behavior is mostly placeholder: the queued APC completes with `STATUS_NOT_IMPLEMENTED`, and informational hard errors always fail.
- Driver/device name packing carefully truncates to the fixed LPC message buffer, but that makes long object names lossy in event-log messages.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/error.c -->