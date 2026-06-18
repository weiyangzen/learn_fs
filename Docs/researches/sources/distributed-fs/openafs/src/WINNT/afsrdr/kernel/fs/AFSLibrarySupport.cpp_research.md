# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLibrarySupport.cpp

## Purpose
`AFSLibrarySupport.cpp` manages the loadable OpenAFS redirector library driver that performs most filesystem work. The fs shim owns library lifecycle, request queuing while the library is unavailable, in-flight request accounting while unloading, resubmission of queued IRPs, initial callback negotiation, and trace callback reconfiguration.

## Important APIs, Control Flow, And State
`AFSLoadLibrary` serializes on `LoadLibraryEvent`, stores the service registry path, calls `ZwLoadDriver`, opens `AFS_LIBRARY_CONTROL_DEVICE_NAME`, saves `LibraryFileObject` and `LibraryDeviceObject`, sets `AFS_LIBRARY_LOADED`, clears `AFS_LIBRARY_QUEUE_CANCELLED`, then drains queued IRPs with `AFSProcessQueuedResults(FALSE)`. On error it unloads/frees the stored service path.

`AFSUnloadLibrary` clears `AFS_LIBRARY_LOADED`, optionally marks `AFS_LIBRARY_QUEUE_CANCELLED`, waits until `InflightLibraryRequests` reaches zero using `InflightLibraryEvent`, cancels queued IRPs, dereferences the library file object, clears the library device object, unloads the driver, and frees `LibraryServicePath`.

`AFSCheckLibraryState` is the gate every pass-through dispatch uses. It rejects redirector shutdown, queues the IRP when the library is not loaded, or increments `InflightLibraryRequests` and clears the in-flight event when loaded. `AFSClearLibraryRequest` decrements that count and signals when zero. `AFSQueueLibraryRequest` appends an `AFSLibraryQueueRequestCB` and marks the IRP pending. `AFSProcessQueuedResults` either completes queued IRPs as cancelled or calls `AFSSubmitLibraryRequest`, whose switch dispatches the original IRP major function back into the correct fs handler.

`AFSInitializeLibrary` sends `IOCTL_AFS_INITIALIZE_LIBRARY_DEVICE` with device objects, server/mount names, debug flags, cache information, cache callbacks, and function pointers (`AFSProcessRequest`, `AFSDbgLogMsg`, `AFSAddConnectionEx`, pool wrappers, dump tracing, auth lookup). `AFSConfigLibraryDebug` pushes the current trace function pointer through `IOCTL_AFS_CONFIG_LIBRARY_TRACE`.

## Dependencies And Integration Points
This file is central to integration between the lightweight filesystem dispatch layer and the loadable library device. It depends on control-device extension state, event/resource synchronization, `ZwLoadDriver/ZwUnloadDriver`, `IoGetDeviceObjectPointer`, IRP completion/resubmission helpers, all major IRP handlers, the communication layer, network-provider list updates, cache manager callback state, and global trace settings.

## Risks And Test Signals
The in-flight count is safety-critical: every successful `AFSCheckLibraryState` must be balanced by `AFSClearLibraryRequest`, with `AFSWrite` taking two references because completion can outlive the caller. Queue cancellation races with redirector shutdown and library reload must not leak IRPs. `AFSProcessQueuedResults` resubmits through top-level handlers, so recursion and double-completion behavior need coverage. Test signals include library load failure, queued requests before load, unload while reads/writes are pending, queue cancellation, trace reconfiguration with/without a loaded library, and exact in-flight event behavior under concurrent dispatch.
