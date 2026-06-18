<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSExtern.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSExtern.h

## Purpose
`AFSExtern.h` declares the global objects, function pointers, configuration strings, control flags, cache mapping values, and security helper pointers shared by the OpenAFS Windows redirector kernel library. It is the external-state companion to `AFSCommon.h`.

## Important APIs, Types, And Globals
The header declares global driver/device objects (`AFSLibraryDriverObject`, `AFSLibraryDeviceObject`, `AFSControlDeviceObject`, `AFSRDRDeviceObject`), `AFSFastIoDispatch`, registry and name strings, debug flags and logging callbacks, the cache-manager callback table, system-process handle, global-root volume and special directory entries, the service request function pointer `AFSProcessRequest`, provider connection hook `AFSAddConnectionEx`, pool allocation/free function pointers, auth-group retrieval callback, library control/cache mapping state, security descriptor helper function pointers, `AFSDefaultSD`, `SeWorldSidAuthority`, and `AFSRtlSysVersion`.

## Control Flow And Integration
There is no executable flow, but these globals are dereferenced throughout the library after initialization. `AFSWorker.cpp` relies on control/RDR/library device objects, allocation callbacks, global root, and debug functions. `AFSWrite.cpp` relies on RDR device state, cache-manager callbacks, service request hooks, cache flags, system process identity, and OS version. Generic, create, name, volume, and provider code use the global strings, special share entries, security descriptor state, and pool callbacks.

## State And Persistence
The declarations refer to process/kernel-resident singleton state. Some values mirror persistent configuration, such as registry path, mount root, server/global-root names, library cache base/length, and default security descriptor. Others are runtime-only, including device object pointers, function pointers supplied during library initialization, debug flags, and the current global-root object tree.

## Dependencies And Integration Points
The header is wrapped in `extern "C"` for C linkage from C++ source files. It depends on types defined by Windows kernel headers and OpenAFS local headers, including `AFSVolumeCB`, `AFSDirectoryCB`, service callback typedefs, `FAST_IO_DISPATCH`, `CACHE_MANAGER_CALLBACKS`, and security descriptor/SID types. It is normally pulled in via `AFSCommon.h` unless `NO_EXTERN` is defined.

## Risks And Edge Cases
Global state initialization order is critical. Most implementation files assume these pointers are valid once dispatch paths run; null or stale callback pointers would fail in kernel mode. Function-pointer ABI drift between the library and the hosting redirector/control code is high impact. Because debug/logging/allocation hooks are globals, tests that replace them must restore them carefully. `AFSSysProcess` is compared against process IDs in write paths, so type and lifetime assumptions matter.

## Test Signals
Useful signals include initialization tests proving all required globals and callbacks are populated, negative tests for missing service/allocation/debug callbacks where possible, teardown tests clearing or invalidating globals only after workers stop, link checks with `NO_EXTERN` defining translation units, and runtime smoke tests for writes, workers, security descriptor creation, provider connection calls, and cache-manager callbacks after library initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSExtern.h -->
