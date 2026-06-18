# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/Include/AFSExtern.h

## Purpose
`AFSExtern.h` declares the fs-layer global variables defined elsewhere, primarily in `AFSData.cpp`. It lets all modules share driver/device objects, configuration, tracing state, server names, auth-group identifiers, callback pointers, and dump buffers.

## Important APIs, Control Flow, And State
The globals include `AFSDriverObject`, `AFSDeviceObject`, `AFSRDRDeviceObject`, `AFSFastIoDispatch`, `AFSRegistryPath`, debug/trace flags, max I/O/dirty settings, `AFSSysProcess`, `AFSMUPHandle`, server/mount/global-root names, `AFSDbgLogLock`, debug ring pointers/length/counter/flags, dump-file location/name/event/buffer, cache-manager callbacks, auth-group flags and GUIDs, `AFSSetInformationToken`, and `AFSDebugTraceFnc`.

## Dependencies And Integration Points
Every implementation in this subset reads or writes some of these globals. `DriverEntry` initializes many of them, `AFSLogSupport.cpp` owns debug/dump state, `AFSRDRSupport.cpp` owns RDR device/cache-related use, `AFSLibrarySupport.cpp` passes callbacks and names to the library, and `AFSProcessSupport.cpp` consumes auth/process globals.

## Risks And Test Signals
Global state makes initialization order and teardown order critical. Many pointers are nullable during early failure or shutdown; callers must guard accordingly. Tests should exercise partial initialization failure, repeated load/unload, trace reconfiguration, redirector close, and static analysis for globals accessed without locks where concurrency matters.
