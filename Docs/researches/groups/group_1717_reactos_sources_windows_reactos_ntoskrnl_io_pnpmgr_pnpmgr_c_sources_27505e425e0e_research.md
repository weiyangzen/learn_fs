# Group Research: group_1717_reactos_sources_windows_reactos_ntoskrnl_io_pnpmgr_pnpmgr_c_sources_27505e425e0e

Scope confirmed against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpmgr.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpmgr.c

Read status: complete file, 1857 lines.

This file provides central PnP manager support routines: device-instance registry helpers, critical-device database matching, bus-type GUID indexing, synchronous PnP IRP construction, device property lookup, resource-list sizing, and exported PnP-facing kernel APIs.

Key entry points:
- `IopInstallCriticalDevice()` reads a device instance's `HardwareID` and optional `CompatibleIDs`, normalizes backslashes to `#`, scans `CriticalDeviceDatabase`, and copies matching `ClassGUID` and optional `Service` values into the Enum instance key.
- `IopGetBusTypeGuidIndex()` maintains the global `PnpBusTypeGuidList`, growing it in blocks of eight GUIDs under a fast mutex.
- `IopInitiatePnpIrp()` builds a temporary `IRP_MJ_PNP` stack location and delegates to `IopSynchronousCall()`.
- `IopCreateDeviceKeyPath()` creates nested device instance registry keys under `Enum`, while `IopCreateRegistryKeyEx()` is a more generic nested key creator.
- `IopSetDeviceInstanceData()` creates `LogConf`, `Control`, and ACPI `Device Parameters` registry data, writing boot resources, resource requirements, default `ConfigFlags`, and `FirmwareIdentified`.
- `IopGetParentIdPrefix()` retrieves or generates a parent ID prefix from the parent's instance path and CRC32, then stores it in the parent Enum key.
- `PnpBusTypeGuidGet()`, `PnpDeviceObjectToDeviceInstance()`, `PnpDetermineResourceListSize()`, `PiGetDeviceRegistryProperty()`, `IoGetDeviceProperty()`, `IoOpenDeviceRegistryKey()`, `IoInvalidateDeviceRelations()`, `IoSynchronousInvalidateDeviceRelations()`, `IoTranslateBusAddress()`, and `IoInvalidateDeviceState()` expose the implemented property, registry, relation, and translation surface.
- `PiInitPhase0()` initializes `PpRegistryDeviceResource` and the device-reference AVL table; `PpInitSystem()` dispatches PnP manager initialization by kernel phase.

Important dependencies:
- Registry APIs: `ZwOpenKey`, `ZwCreateKey`, `ZwQueryValueKey`, `ZwSetValueKey`, `ZwEnumerateKey`, `RtlQueryRegistryValues`.
- Device-node state: `IopGetDeviceNode`, `IopIsValidPhysicalDeviceObject`, `IopRootDeviceNode`, `PopSystemPowerDeviceNode`, `IopDeviceTreeLock`.
- PnP action queue: `PiQueueDeviceAction`, `PiPerformSyncDeviceAction`.
- Resource support: `PnpDetermineResourceListSize`, `PnpBusTypeGuidList`, HAL address translation.

Notable behavior and risks:
- The device-reference AVL table is initialized with compare/allocate/free callbacks that assert false and return dummy values, so it is a placeholder rather than usable storage.
- `IopInstallCriticalDevice()` has several early-continue paths after opening or allocating nested critical-device data that do not consistently close/free all intermediate objects.
- `IoGetDeviceProperty()` implements common bus, identifier, name, removal-policy, and registry-backed properties, but resource requirements, allocated resources, and container ID are explicitly unimplemented.
- `IoOpenDeviceRegistryKey()` requires a valid PDO, builds either driver class-key or Enum device-key paths, and creates the `Device Parameters` subkey for device keys.
- Device-relation invalidation only acts on `BusRelations`; synchronous invalidation returns `STATUS_NOT_IMPLEMENTED` for `PowerRelations` and success/no-op for `TargetDeviceRelation`.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpnotify.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpnotify.c

Read status: complete file, 519 lines.

This file implements Plug and Play notification registration, delivery, and unregistration for device-interface changes, hardware-profile changes, and target-device changes.

Key entry points:
- `PiInitializeNotifications()` initializes guarded mutexes and list heads for notification categories.
- `PiNotifyDeviceInterfaceChange()` allocates a `DEVICE_INTERFACE_CHANGE_NOTIFICATION`, filters registrations by interface class GUID, and invokes matching callbacks.
- `PiNotifyHardwareProfileChange()` broadcasts a `HWPROFILE_CHANGE_NOTIFICATION` to all hardware-profile listeners.
- `PiNotifyTargetDeviceChange()` broadcasts target-device removal/custom notifications through the target device node's per-device notification list and fills the registered `FileObject` before each callback.
- `IoRegisterPlugPlayNotification()` allocates a `PNP_NOTIFY_ENTRY`, references the driver object, installs it on the relevant list, and optionally sends arrival notifications for existing interfaces.
- `IoUnregisterPlugPlayNotification()` marks an entry deleted and dereferences it under the category lock.
- `IoPnPDeliverServicePowerNotification()` is present but unimplemented.

Important dependencies:
- Global lists guarded by `PiNotifyDeviceInterfaceLock`, `PiNotifyHwProfileLock`, and `PiNotifyTargetDeviceLock`.
- Device-node target notification list: `deviceNode->TargetDeviceNotify`.
- Interface enumeration through `IoGetDeviceInterfaces()`.
- Target resolution through `IopGetRelatedTargetDevice()`.

Notable behavior and risks:
- Notification callbacks are invoked after temporarily releasing the guarded mutex. Entries are reference-counted first so unregister-during-callback remains survivable.
- `PiCallNotifyProc()` debug-checks that callbacks preserve IRQL and APC-disable state, but ignores callback return values.
- `PNP_NOTIFY_ENTRY.RefCount` is an 8-bit field, so extreme recursive/reentrant callback paths could overflow it.
- `PiNotifyTargetDeviceChange()` references the target `DeviceObject` before allocation, but the allocation-failure path returns without dereferencing it.
- Device-interface registrations with `PNPNOTIFY_DEVICE_INTERFACE_INCLUDE_EXISTING_INTERFACES` call the callback directly for existing links, outside the registered-entry refcount path.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpreport.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpreport.c

Read status: complete file, 551 lines.

This file handles APIs used by drivers to report detected legacy/root-enumerated devices, resource detection/conflict checks, and custom target-device change notifications.

Key entry points:
- `IopGetInterfaceTypeString()` maps `INTERFACE_TYPE` values to registry-friendly strings used in generated compatible IDs.
- `IoReportDetectedDevice()` creates or accepts a PDO, allocates a device node, creates the Enum instance key, writes `Service`, `Legacy`, `DeviceReported`, compatible IDs, device text, and resource data, optionally assigns resources, inserts the node under the root, and queues enumeration.
- `IoReportResourceForDetection()` validates supplied resource lists and calls `IopDetectResourceConflict()`.
- `PpSetCustomTargetEvent()` sends a custom target-device notification through `PiNotifyTargetDeviceChange()` and optionally completes a caller event/status pair.
- `IoReportTargetDeviceChange()` validates a PDO and custom notification, rejects system remove events, sends the notification synchronously, and waits for completion.
- `IoReportTargetDeviceChangeAsynchronous()` copies the caller's custom notification into a nonpaged work item and queues delayed work.
- `IopReportTargetDeviceChangeAsyncWorker()` sends the queued custom notification and releases the referenced PDO.

Important dependencies:
- Root enumerator helpers: `PnpRootCreateDevice`, `PnpRootRegisterDevice`.
- Device-node creation and insertion: `PipAllocateDeviceNode`, `PiInsertDevNode`, `PiSetDevNodeState`.
- Registry setup: `IopCreateDeviceKeyPath`, `IopSetDeviceInstanceData`, `PiSetDevNodeText`.
- Resource assignment/conflict detection: `IopAssignDeviceResources`, `IopDetectResourceConflict`.
- Notification delivery: `PiNotifyTargetDeviceChange`.

Notable behavior and risks:
- Built-in drivers using `IoCreateDriver()` have `ServiceKeyName` shortened to the last path component before root-device IDs are generated.
- Newly reported devices get `DNF_MADEUP | DNF_ENUMERATED`, then are placed in `DeviceNodeStartPostWork` and re-enumerated.
- `ResourceAssigned == FALSE` causes immediate resource assignment; otherwise the supplied resources are recorded without assignment in this path.
- `PpSetCustomTargetEvent()` accepts asynchronous callback/context parameters but never invokes the completion callback, so asynchronous callers get `STATUS_PENDING` without callback completion from this file.
- The synchronous path sets the event before writing `SyncStatus = STATUS_SUCCESS`, which is a small ordering risk on multiprocessor systems.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpreport.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpres.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpres.c

Read status: complete file, 1498 lines.

This file implements PnP resource allocation, requirement filtering, resource-list translation, resource-map persistence, and conflict detection against the registry-backed hardware resource map.

Key entry points:
- `IopFindBusNumberResource()`, `IopFindMemoryResource()`, `IopFindPortResource()`, `IopFindDmaResource()`, and `IopFindInterruptResource()` search for available descriptors satisfying individual `IO_RESOURCE_DESCRIPTOR` requirements.
- `IopFixupResourceListWithRequirements()` merges existing boot/assigned resources with one acceptable alternative list from an `IO_RESOURCE_REQUIREMENTS_LIST`, adding missing descriptors and handling alternates.
- `IopFilterResourceRequirements()` sends `IRP_MN_FILTER_RESOURCE_REQUIREMENTS` to the device stack and adopts a returned requirements list if one is supplied.
- `IopTranslateDeviceResources()` copies raw resources and translates ports, interrupts, and memory through HAL routines.
- `IopAssignDeviceResources()` is the high-level assignment flow: filter requirements, copy boot resources, detect conflicts, call `HalAdjustResourceList()`, fix up missing resources, translate, update `HARDWARE\\RESOURCEMAP`, update Enum `Control\\AllocConfig`, and set `DeviceNodeResourcesAssigned`.
- `IopDetectResourceConflict()` walks `\\Registry\\Machine\\HARDWARE\\RESOURCEMAP`, skips `.Translated` values, and compares raw resource lists.
- `IopUpdateResourceMap()` and `IopUpdateControlKeyWithResources()` persist raw/translated resources in global and per-device registry locations.

Important dependencies:
- Resource-list sizing from `PnpDetermineResourceListSize()`.
- Registry resource map layout under `HARDWARE\\RESOURCEMAP`.
- HAL translation/adjustment: `HalTranslateBusAddress`, `HalGetInterruptVector`, `HalAdjustResourceList`.
- Device properties for PDO names through `IoGetDeviceProperty(DevicePropertyPhysicalDeviceObjectName)`.
- PnP IRP helper `IopInitiatePnpIrp()`.

Notable behavior and risks:
- `IopCheckResourceDescriptor()` detects overlap for memory, port, interrupt, bus-number, and DMA descriptors, but returns `FALSE` for non-silent checks due to a local hack; this suppresses real conflict failures in some user-visible paths.
- When a conflict is found and a conflicting descriptor is requested, the code copies the incoming descriptor rather than the already-owned conflicting descriptor, weakening range-skip logic in resource search.
- Memory and port allocation mutate zero alignment to one as a workaround.
- Resource-list walking comments acknowledge variable-sized `CmResourceTypeDeviceSpecific` descriptors, but several loops still index `PartialDescriptors[ii]` directly.
- `IopTranslateDeviceResources()` has a missing `break` after memory translation, intentionally or accidentally falling through to no-op descriptor cases.
- On translation cleanup, the translated-list free path assigns `DeviceNode->ResourceList = NULL` twice and does not clear `ResourceListTranslated`.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnpres.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnproot.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnproot.c

Read status: complete file, 1529 lines.

This file implements the root PnP bus driver and root-enumerated PDO handling. It keeps an in-memory list of root devices, creates PDOs for registry-backed and legacy-reported devices, answers PnP IRPs for those PDOs, and exposes the root driver's dispatch entry points.

Key entry points:
- `PnpRootInitializeDevExtension()` initializes the static root FDO extension list and lock.
- `PnpRootCreateDeviceObject()` creates unnamed root-child PDOs with `PNPROOT_PDO_DEVICE_EXTENSION`.
- `PnpRootCreateDevice()` creates a new `Root\\<service>\\NNNN` legacy/root device, updates the registry `NextInstance`, creates the instance key, creates a PDO, and links it into the root list.
- `PnpRootRegisterDevice()` registers an externally supplied PDO by splitting its instance path into device ID and instance ID, then links it into the root list.
- `EnumerateDevices()` walks `HKLM\\System\\CurrentControlSet\\Enum\\Root`, skips `LEGACY_` keys, filters unreported devices, and calls `CreateDeviceFromRegistry()` for each accepted instance.
- `PnpRootQueryDeviceRelations()` enumerates devices, creates missing PDOs, references them, merges any incoming relations, and returns a `DEVICE_RELATIONS` list.
- `PnpRootFdoPnpControl()` handles root FDO `IRP_MN_QUERY_DEVICE_RELATIONS`.
- `PnpRootPdoPnpControl()` handles child PDO PnP minors including start, target relation, capabilities, resources, resource requirements, text, IDs, bus information, and remove.
- `PnpRootPowerControl()` trivially succeeds query/set power IRPs.
- `PnpRootDriverEntry()` records `IopRootDriverObject`, installs PnP/power dispatch routines, and optionally creates a PFN dump device when tracing is enabled.

Important dependencies:
- Registry helpers: `IopOpenRegistryKeyEx`, `RtlQueryRegistryValues`, `ZwEnumerateKey`, `ZwCreateKey`.
- PnP manager device-node ownership: `IopGetDeviceNode`, `IopRootDeviceNode`.
- Device object lifecycle: `IoCreateDevice`, `IoDeleteDevice`, `ObReferenceObject`.
- Root enum constants: `REGSTR_PATH_SYSTEMENUM`, `REGSTR_KEY_ROOTENUM`.

Notable behavior and risks:
- Root device state is global/static (`PnpRootDOExtension`) rather than attached to a normal FDO device extension.
- `IopShouldProcessDevice()` only asserts `DeviceReported == 1`; it does not reject other DWORD values after reading them.
- `PnpRootCreateDevice()` allocates `FullInstancePath->MaximumLength` without explicit room for a terminating null, matching `UNICODE_STRING` length use but risky for callers treating it as null-terminated.
- PDO remove frees strings and resource buffers, unlinks the device, frees `DeviceInfo`, and deletes the PDO.
- `PdoQueryCapabilities()` only sets `UniqueID = TRUE`; most capability fields remain caller-initialized.
- Hardware and compatible ID queries are optional no-ops for root PDOs, while device ID and instance ID are duplicated from `PNPROOT_DEVICE`.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnproot.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnputil.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnputil.c

Read status: complete file, 195 lines.

This file contains small PnP utility routines for converting registry strings into kernel string objects and freeing those converted lists.

Key entry points:
- `PnpFreeUnicodeStringList()` frees each allocated string buffer in an array and then frees the array.
- `PnpRegMultiSzToUnicodeStrings()` validates a `REG_MULTI_SZ`, counts component strings, allocates a `UNICODE_STRING` array, copies each string into its own null-terminated buffer, and returns the count.
- `PnpRegSzToString()` scans a `REG_SZ` byte range for the first null terminator and optionally returns the string length in bytes.

Important dependencies:
- Registry value layout through `KEY_VALUE_FULL_INFORMATION`.
- Pool allocation tags `'sUpP'` and general pool freeing.

Notable behavior and risks:
- `PnpRegMultiSzToUnicodeStrings()` handles both double-null-terminated and length-bounded final strings.
- The allocated `UNICODE_STRING` array is not zero-initialized before individual buffers are filled. Error cleanup passes the number of completed entries, which avoids freeing uninitialized later entries.
- `PnpRegSzToString()` always returns `TRUE`; it reports a bounded length even if the input lacks a terminator.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnputil.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/arm/init.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/arm/init.c

Read status: complete file, 72 lines.

This ARM-specific ARM3 memory-manager initialization file mostly declares global memory layout and accounting variables expected by the broader ARM3 memory manager, with machine-dependent initialization still stubbed.

Key contents:
- Global nonpaged/paged/session/system view layout variables such as `MmNonPagedSystemStart`, `MmNonPagedPoolStart`, `MmPagedPoolEnd`, `MmSessionBase`, and `MiSystemViewStart`.
- PFN and physical-memory globals including `MmSystemPageDirectory`, `MmSystemPagePtes`, `MiPfnBitMap`, `MmPhysicalMemoryBlock`, `MmNumberOfPhysicalPages`, and `MmHighestPhysicalPage`.
- User/kernel range globals such as `MmUserProbeAddress`, `MmHighestUserAddress`, `MmSystemRangeStart`, `MmSystemCacheStart`, and `MmHyperSpaceEnd`.
- `MiInitMachineDependent()` is the only function and calls `UNIMPLEMENTED_FATAL()` before returning success.

Important dependencies:
- Shared ARM3 internals from `mm/ARM3/miarm.h`.
- Loader-provided memory descriptors through `PLOADER_PARAMETER_BLOCK`, though not yet consumed here.

Notable behavior:
- This file is a declaration/porting placeholder for ARM memory-manager state.
- `MiInitMachineDependent()` is not functionally implemented; it fatal-logs unimplemented initialization.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/arm/init.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/contmem.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/contmem.c

Read status: complete file, 676 lines.

This file implements ARM3 contiguous physical memory allocation and freeing, backing the public `MmAllocateContiguousMemory*` and `MmFreeContiguousMemory*` APIs.

Key entry points:
- `MiFindContiguousPages()` scans `MmPhysicalMemoryBlock` runs for free PFNs within caller bounds and optional boundary constraints, then revalidates under the PFN lock, unlinks pages from free/zeroed lists, marks PFN state, and tags allocation start/end PFNs.
- `MiCheckForContiguousMemory()` verifies whether an existing virtual range maps a physically contiguous PFN sequence satisfying low/high/boundary constraints.
- `MiFindContiguousMemory()` calls `MiFindContiguousPages()`, maps the selected physical range through `MmMapIoSpace()`, and fixes PFN `PteAddress`/`PteFrame` metadata to match the mapping.
- `MiAllocateContiguousMemory()` first tries cached nonpaged-pool allocation and validates physical contiguity, then falls back to PFN-run search if IRQL permits.
- `MiFreeContiguousMemory()` frees pool-backed contiguous allocations directly, otherwise validates the start PFN marker, marks PFNs deleted, unmaps the I/O-space mapping, and decrements share counts under the PFN lock.
- Public wrappers `MmAllocateContiguousMemorySpecifyCache()`, `MmAllocateContiguousMemory()`, `MmFreeContiguousMemory()`, and `MmFreeContiguousMemorySpecifyCache()` convert address bounds and delegate to internal helpers.

Important dependencies:
- PFN database helpers/macros: `MI_PFN_ELEMENT`, `MiGetPfnEntry`, `MiIsPfnInUse`, `MiUnlinkFreeOrZeroedPage`, `MiAcquirePfnLock`, `MiReleasePfnLock`, `MiDecrementShareCount`.
- Address/PTE helpers: `MiAddressToPte`, `MiPteToAddress`, `PFN_FROM_PTE`.
- Pool and I/O mapping APIs: `ExAllocatePoolWithTag`, `ExFreePoolWithTag`, `MmMapIoSpace`, `MmUnmapIoSpace`.
- Global layout bounds: `MmNonPagedPoolStart`, `MmNonPagedPoolExpansionStart`, `MmNonPagedPoolEnd`, `MmHighestPhysicalPage`.

Notable behavior and risks:
- Boundary handling converts `BoundaryPfn` to `~(BoundaryPfn - 1)`; zero boundary is accepted only because guarded checks skip use when `BoundaryPfn` is zero.
- Cached allocations prefer nonpaged pool because initial nonpaged pool is expected to be contiguous, but expansion allocations may fail the explicit PFN-contiguity check.
- The allocator refuses the PFN-search fallback above APC_LEVEL.
- Freeing a non-pool allocation from the middle of an allocation triggers `BAD_POOL_CALLER` with code `0x60`.
- Public `MmFreeContiguousMemorySpecifyCache()` ignores size and cache type during free, intentionally delegating to the generic free path.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/contmem.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/drvmgmt.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/drvmgmt.c

Read status: complete file, 254 lines.

This file contains ARM3 driver-management and driver-verifier support routines, with pageable-image locking/trimming mostly stubbed and verifier thunk registration partially implemented.

Key entry points:
- `MmUnlockPageableImageSection()`, `MmLockPageableSectionByHandle()`, `MmLockPageableDataSection()`, and `MmTrimAllSystemPageableMemory()` are unimplemented or warning stubs.
- `MmAddVerifierThunks()` validates a driver-supplied thunk-pair table, allocates a private copy, locates the owning loader entry, rejects kernel/HAL thunks, verifies pristine routines are inside the owning image, and links the thunk table into `MiVerifierDriverAddedThunkListHead`.
- `MmIsDriverVerifying()` checks the driver's loader entry for `LDRP_IMAGE_VERIFYING`.
- `MmIsVerifierEnabled()` reports `MmVerifierData.Level` when verifier thunk infrastructure has been initialized, otherwise returns `STATUS_NOT_SUPPORTED`.

Important dependencies:
- Verifier globals: `MmVerifierData`, `MiVerifierDriverAddedThunkListHead`, `MiActiveVerifierThunks`.
- Loader state: `MiLookupDataTableEntry()`, `PLDR_DATA_TABLE_ENTRY`, `MmSystemLoadLock`, `MmBootImageSize`.
- Driver object loader section (`DriverObject->DriverSection`).

Notable behavior and risks:
- `MmAddVerifierThunks()` checks each thunk's `PristineRoutine`, but the loop uses `ThunkTable->PristineRoutine` instead of `ThunkTable[i].PristineRoutine`, so only the first entry is effectively validated repeatedly.
- Verifier availability is inferred from `MiVerifierDriverAddedThunkListHead.Flink` being initialized/non-null.
- Pageable image section lock/unlock behavior is not implemented, so callers get no real memory residency management here.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/drvmgmt.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/dynamic.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/dynamic.c

Read status: complete file, 126 lines.

This file provides the ARM3 dynamic physical-memory API surface. Hot-add, hot-remove, and bad/good marking APIs are stubs; physical memory range enumeration is implemented.

Key entry points:
- `MmAddPhysicalMemory()`, `MmMarkPhysicalMemoryAsBad()`, `MmMarkPhysicalMemoryAsGood()`, and `MmRemovePhysicalMemory()` are unimplemented and return `STATUS_NOT_IMPLEMENTED`.
- `MmGetPhysicalMemoryRanges()` allocates a nonpaged copy of `MmPhysicalMemoryBlock` runs as byte-based `PHYSICAL_MEMORY_RANGE` entries, appends a zero terminator, and returns it to the caller.

Important dependencies:
- `MmPhysicalMemoryBlock` run metadata.
- PFN lock routines `MiAcquirePfnLock()` and `MiReleasePfnLock()`.
- Nonpaged pool tag `'hPmM'`.

Notable behavior:
- `MmGetPhysicalMemoryRanges()` asserts PASSIVE_LEVEL, sizes the buffer from `NumberOfRuns + 1`, and asserts the run count did not change after acquiring the PFN lock.
- Returned ranges convert pages to bytes with `<< PAGE_SHIFT` and require caller-side pool freeing.
- Dynamic physical memory mutation is not supported by this implementation.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/ARM3/dynamic.c -->