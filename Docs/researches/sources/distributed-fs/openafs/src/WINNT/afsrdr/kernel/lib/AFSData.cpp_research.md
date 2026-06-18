# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSData.cpp

## Purpose

`AFSData.cpp` is the single definition unit for the redirector library's global variables. It defines device objects, shared names, cache configuration, debug/control flags, callback entry points supplied by the framework, security globals, global directory entries, and OS-version state. The file has no active control flow beyond initialization through static zero/default values, but it is foundational because most other library files use these symbols as shared process-wide kernel state.

## Important APIs, types, and functions

- `#define NO_EXTERN` before including `AFSCommon.h` selects definitions instead of declarations for the shared globals.
- Device/global handles: `AFSLibraryDriverObject`, `AFSLibraryDeviceObject`, `AFSControlDeviceObject`, `AFSRDRDeviceObject`, and `AFSSysProcess`.
- Name globals: `AFSRegistryPath`, `AFSServerName`, `AFSMountRootName`, `AFSPIOCtlName`, and `AFSGlobalRootName`.
- Root and directory globals: `AFSGlobalRoot`, `AFSSpecialShareNames`, `AFSGlobalDotDirEntry`, and `AFSGlobalDotDotDirEntry`.
- Debug/cache/control state: `AFSDebugFlags`, `AFSLibCacheManagerCallbacks`, `AFSLibControlFlags`, `AFSLibCacheBaseAddress`, `AFSLibCacheLength`, `AFSDebugTraceFnc`, and `AFSDbgLogMsg`.
- Framework callbacks: `AFSProcessRequest`, `AFSAddConnectionEx`, `AFSExAllocatePoolWithTag`, `AFSExFreePoolWithTag`, `AFSDumpTraceFilesFnc`, and `AFSRetrieveAuthGroupFnc`.
- Security globals: `AFSRtlSetSaclSecurityDescriptor`, `AFSDefaultSD`, `AFSRtlSetGroupSecurityDescriptor`, and `SeWorldSidAuthority`.
- System state: `AFSRtlSysVersion`.

## Control flow

There are no functions in this file. Load-time behavior is controlled by C/C++ global initialization. Most pointer globals start as `NULL`, integral flags as `0`, `AFSDbgLogMsg` defaults to `AFSDefaultLogMsg`, and `AFSDumpTraceFilesFnc` defaults to `AFSDumpTraceFiles_Default`. Later initialization paths, especially `AFSInitializeLibrary` reached from `AFSDevControl.cpp`, are expected to populate the framework callbacks and global device/name/security/cache state before dispatch handlers use them.

## State and persistence behavior

The state is process-wide for the loaded kernel library. It persists for the lifetime of the driver/library load and is shared by create, directory, cache, service, connection, and debug paths. Because callback pointers and device-object pointers begin as null, dispatch paths guard some use sites, such as `AFSCreate` rejecting file-system opens until `AFSRDRDeviceObject` and `AFSGlobalRoot` are ready. Other use sites assume initialization has already succeeded.

The global directory entries for `"."`, `".."`, special share names, and the PIOCtl name shape enumeration and open behavior across all CCBs. The cache-manager globals hold shared callbacks/base/length used by cache and extent code. The debug callback pointers control whether tracing routes to defaults or framework-supplied logging.

## Dependencies and integration points

Every file that includes `AFSCommon.h` depends on these definitions. `AFSCreate.cpp` uses `AFSRDRDeviceObject`, `AFSGlobalRoot`, `AFSPIOCtlName`, `AFSSpecialShareNames`, framework allocation/free callbacks, debug callbacks, and auth/service callbacks. `AFSDirControl.cpp` uses `AFSControlDeviceObject`, `AFSGlobalDotDirEntry`, `AFSGlobalDotDotDirEntry`, `AFSPIOCtlName`, and allocation/free callbacks. `AFSDevControl.cpp` initializes many of these globals indirectly through library initialization and can replace `AFSDebugTraceFnc` through `IOCTL_AFS_CONFIG_LIBRARY_TRACE`.

## Risks and edge cases

- These globals are mutable shared kernel state. Initialization ordering is critical; null callbacks or device objects can crash callers that do not explicitly guard them.
- Callback pointer replacement and use require concurrency discipline outside this file. The debug trace callback is updated with an interlocked operation in `AFSDevControl.cpp`, but most other initialization is expected to occur before concurrent file-system traffic.
- `extern "C"` exposes unmangled names, which is important for C/driver integration but also means duplicate definitions would be linker-visible if `NO_EXTERN` is misused elsewhere.
- Default debug and dump callbacks reduce startup fragility, but allocation, auth retrieval, service requests, and connection callbacks have no safe default here.

## Test signals

Initialization tests should verify that `AFSInitializeLibrary` fills all required callbacks and globals before file-system dispatch begins, that create/open paths return readiness failures while root/device globals are unset, that debug tracing works before and after `IOCTL_AFS_CONFIG_LIBRARY_TRACE`, and that unload/reinitialize paths reset or replace global state without stale callback/device-object use.
