# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSSystemControl.cpp

## Purpose
`AFSSystemControl.cpp` implements `IRP_MJ_SYSTEM_CONTROL` as an unsupported/stub WMI system-control handler. It logs and completes requests locally with `STATUS_NOT_IMPLEMENTED`.

## Important APIs, Control Flow, And State
`AFSSystemControl` ignores the device object, obtains the IRP stack, traces the file object at warning level, completes via `AFSCompleteRequest`, and returns `STATUS_NOT_IMPLEMENTED`. No library forwarding, persistent state updates, or in-flight accounting occur.

## Dependencies And Integration Points
The handler is installed in `DriverEntry` and can also be selected by `AFSSubmitLibraryRequest` for queued system-control IRPs. It depends on the shared trace, completion, exception-filter, and dump helpers.

## Risks And Test Signals
Any WMI/system-control integration is unavailable through this driver. Test by issuing system-control IRPs and confirming local completion, no call into the library, stable logging, and no double completion under exception handling.
