# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSInit.cpp

## Purpose

`AFSInit.cpp` contains the Windows kernel driver's library entry and unload paths. `DriverEntry` establishes global driver state, creates the library control device, initializes library-specific resources, and installs dispatch handlers for the Windows I/O major-function table. `AFSUnload` reverses the library lifetime by invalidating the global root volume, tearing down worker pools and library devices, releasing global memory, and closing library state.

## Important APIs, types, and functions

`DriverEntry(PDRIVER_OBJECT, PUNICODE_STRING)` is called by the I/O manager at load time. `AFSUnload(PDRIVER_OBJECT)` is registered as the unload callback. Important state includes `AFSLibraryDriverObject`, `AFSRegistryPath`, `AFSRtlSysVersion`, `AFSRtlSetGroupSecurityDescriptor`, `AFSLibraryDeviceObject`, `AFSSysProcess`, `AFSGlobalRoot`, and `AFSDefaultSD`. The file depends on `AFSCreateDefaultSecurityDescriptor`, `AFSInitializeLibraryDevice`, `AFSRemoveLibraryDevice`, `AFSCloseLibrary`, worker-pool teardown, and volume invalidation helpers.

## Control flow

`DriverEntry` runs inside an exception filter, prints build metadata, stores the driver object globally, copies the registry path into paged pool, captures the OS version, and dynamically resolves `RtlSetGroupSecurityDescriptor`. It attempts default security descriptor creation, but logs and continues if that fails. It then creates `AFS_LIBRARY_CONTROL_DEVICE_NAME` with `IoCreateDevice`, initializes the library device, zeros library worker counters, fills all major functions with `AFSDefaultDispatch`, overrides implemented IRP handlers, registers `AFSUnload`, and records the current process id. Failure cleanup frees the registry path and removes/deletes the library device.

`AFSUnload` invalidates `AFSGlobalRoot`, clears the active-global-root flag, shuts down the volume worker, removes the worker pool, frees the registry path and default security descriptor, closes the library, removes the library device, and deletes the device object.

## State and persistence behavior

This file owns process-lifetime kernel state rather than durable state. The copied registry path, OS version, optional routine pointer, control device object, dispatch table, and worker-count fields persist for the loaded driver lifetime. Unload reverses these allocations and invalidates active volume state.

## Dependencies and integration points

The file integrates with the Windows I/O manager through `IoCreateDevice`, `IoDeleteDevice`, the major-function dispatch table, and `DriverUnload`. It wires in the rest of the redirector/library surface, including create/close, read/write, volume information, directory control, FS/device/internal device control, shutdown, lock control, cleanup, security, and system control.

## Risks and test signals

Security descriptor creation failure is intentionally downgraded to success, which can affect later security behavior. The registry path allocation uses `Length`, not `MaximumLength`, so later code must not assume spare terminator space. The exception handler in `DriverEntry` logs but may leave `ntStatus` unchanged if a fault happens before explicit failure assignment. Tests should cover load/unload, allocation and device-creation failure injection, dispatch-table wiring, unavailable `RtlSetGroupSecurityDescriptor`, and leak-free worker/device cleanup.
