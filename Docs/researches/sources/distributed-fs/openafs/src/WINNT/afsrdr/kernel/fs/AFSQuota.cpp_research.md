# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSQuota.cpp

## Purpose
`AFSQuota.cpp` contains quota IRP handlers, but quota operations are not supported by this redirector shim. `IRP_MJ_QUERY_QUOTA` and `IRP_MJ_SET_QUOTA` are commented out in `DriverEntry`, and both handlers return `STATUS_NOT_SUPPORTED` if called.

## Important APIs, Control Flow, And State
`AFSQueryQuota` and `AFSSetQuota` retrieve the current IRP stack, log the file object at error level under `AFS_SUBSYSTEM_FILE_PROCESSING`, complete the IRP with `STATUS_NOT_SUPPORTED`, and return. Neither checks library state nor forwards to the library device. No quota state is kept in this file.

## Dependencies And Integration Points
The handlers are declared in `AFSCommon.h` and could be installed in the dispatch table, but current initialization leaves quota dispatch disabled. They depend only on `AFSCompleteRequest`, tracing, exception filtering, and dump support.

## Risks And Test Signals
The disabled dispatch table means these functions may be unreachable in normal operation, but direct invocation should still complete cleanly. Tests should verify quota IRPs receive unsupported behavior if enabled, do not alter library in-flight counts, and do not leak or double-complete under exception conditions.
