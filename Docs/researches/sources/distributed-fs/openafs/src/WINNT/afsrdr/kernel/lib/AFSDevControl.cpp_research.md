# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSDevControl.cpp

## Purpose

`AFSDevControl.cpp` implements the library dispatch handler for `IRP_MJ_DEVICE_CONTROL`. It validates IOCTL buffer sizes and caller mode, invokes initialization and management routines, updates cache/network/volume state, answers status queries, and completes the IRP. This file is the kernel-library side of the control channel used by the file-system/framework component and network provider support code.

## Important APIs, types, and functions

- `AFSDevControl(PDEVICE_OBJECT, PIRP)` is the only function. It reads `Parameters.DeviceIoControl.IoControlCode`, switches on the IOCTL, validates `SystemBuffer` lengths, calls the appropriate AFS helper, sets `Irp->IoStatus.Information` where needed, catches exceptions, and completes the IRP.
- Initialization IOCTL: `IOCTL_AFS_INITIALIZE_LIBRARY_DEVICE` accepts `AFSLibraryInitCB`, requires `KernelMode`, and runs `AFSInitializeLibrary`, `AFSInitializeWorkerPool`, `AFSInitializeGlobalDirectoryEntries`, and `AFSInitializeSpecialShareNameList`.
- Connection IOCTLs: `IOCTL_AFS_ADD_CONNECTION`, `IOCTL_AFS_CANCEL_CONNECTION`, `IOCTL_AFS_GET_CONNECTION`, `IOCTL_AFS_LIST_CONNECTIONS`, and `IOCTL_AFS_GET_CONNECTION_INFORMATION` use `AFSNetworkProviderConnectionCB` and related result buffers.
- Extent/cache IOCTLs: `IOCTL_AFS_SET_FILE_EXTENTS`, `IOCTL_AFS_RELEASE_FILE_EXTENTS`, `IOCTL_AFS_SET_FILE_EXTENT_FAILURE`, and `IOCTL_AFS_INVALIDATE_CACHE`.
- State/status IOCTLs: `IOCTL_AFS_NETWORK_STATUS`, `IOCTL_AFS_VOLUME_STATUS`, `IOCTL_AFS_STATUS_REQUEST`, and `IOCTL_AFS_GET_OBJECT_INFORMATION`.
- Trace configuration: `IOCTL_AFS_CONFIG_LIBRARY_TRACE` accepts `AFSDebugTraceConfigCB` and updates `AFSDebugTraceFnc`.
- The internal Windows remote redirector IOCTL `0x140390` (`IOCTL_LMR_DISABLE_LOCAL_BUFFERING`) is recognized and explicitly returns `STATUS_NOT_SUPPORTED`.

## Control flow

The dispatch handler obtains the stack location and IOCTL code, then processes one switch arm. Most arms perform simple structural validation before forwarding to the corresponding implementation. Variable-length input is checked with `FIELD_OFFSET` arithmetic, notably remote-name lengths for add-connection and extent-array length for set-extents. Some operations write results into the same `AssociatedIrp.SystemBuffer` used for input, consistent with buffered IOCTLs.

Initialization is special. It is accepted only from kernel mode, checks for an `AFSLibraryInitCB`, and then performs four ordered initialization stages. A failure in any stage breaks out and completes the IOCTL with that failure. The default arm returns `STATUS_NOT_IMPLEMENTED` and notes that security checks elsewhere mean new IOCTLs must also be added in the framework communication support file.

After the switch, exception handling maps unexpected faults to `STATUS_UNSUCCESSFUL`, emits trace/dump output, writes `Irp->IoStatus.Status`, completes the request through `AFSCompleteRequest`, and returns the final status.

## State and persistence behavior

This file mutates global library state indirectly. Initialization populates device/library globals, worker threads, synthetic directory entries, and special-share lists. Connection IOCTLs update network-provider mappings. Extent IOCTLs update cached file extent state. Invalidate-cache, network-status, and volume-status IOCTLs alter runtime cache/reachability state. Trace configuration changes the global debug trace callback pointer.

The handler itself stores no persistent local state. `Irp->IoStatus.Information` is part of the public contract for result sizes; several setter operations explicitly reset it to zero.

## Dependencies and integration points

`AFSDevControl` depends on WDK buffered IOCTL conventions (`Irp->AssociatedIrp.SystemBuffer`, `InputBufferLength`, `OutputBufferLength`, `RequestorMode`) and redirector helper routines declared through `AFSCommon.h`. It integrates with `AFSData.cpp` by initializing and updating global symbols, with worker-pool/cache/extent code through the extent and cache IOCTLs, with network-provider support through connection IOCTLs, and with object/status code through status query routines. The default-arm comment identifies `..\\fs\\AFSCommSupport.cpp` as the framework-side companion for IOCTL exposure and security checks.

## Risks and edge cases

- IOCTLs share the same system buffer for input and output. Length validation must remain exact for every structure, especially variable-length connection names and extent arrays.
- `IOCTL_AFS_SET_FILE_EXTENTS` reads `pExtents->ExtentCount` only after ensuring the buffer contains that field, then validates the full array. This pattern must be preserved for any variable-length additions.
- Initialization is ordered but partial failure cleanup is not visible in this file. Callers must handle retry/unload safety in the underlying initialization routines.
- `IOCTL_AFS_CONFIG_LIBRARY_TRACE` uses `InterlockedCompareExchangePointer` with identical exchange/comparand values from the incoming config, which effectively only updates when the old value already equals the new value. That may be intentional as a guarded compare, or it may be a suspicious no-op pattern worth reviewing against intended trace reconfiguration behavior.
- Unknown IOCTL behavior is tied to security checks in a companion framework file. Adding a new IOCTL in only one side can make it unreachable or unsafe.

## Test signals

Tests should cover kernel-mode versus user-mode initialization access, undersized buffers for every IOCTL, variable-length add-connection and set-extents boundary cases, status/output length reporting, initialization-stage failures, unsupported `0x140390`, trace-callback configuration behavior, exception-path completion, and cross-checking that every accepted IOCTL is also allowed and marshalled by the framework communication layer.
