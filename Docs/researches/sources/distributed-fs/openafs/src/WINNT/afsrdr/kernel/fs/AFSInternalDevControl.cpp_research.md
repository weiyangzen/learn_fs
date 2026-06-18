# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSInternalDevControl.cpp

## Purpose
`AFSInternalDevControl.cpp` implements the `IRP_MJ_INTERNAL_DEVICE_CONTROL` dispatch entry. In this filesystem redirector layer it is a stub: internal device controls are not implemented and every request is completed locally with `STATUS_NOT_IMPLEMENTED`.

## Important APIs, Control Flow, And State
`AFSInternalDevControl` retrieves the current stack location but does not inspect any control code. Inside structured exception handling, it calls `AFSCompleteRequest(Irp, STATUS_NOT_IMPLEMENTED)` and returns that status. The `DeviceObject` is explicitly unused. No persistent state is read or written except tracing/dump activity on exception.

## Dependencies And Integration Points
The handler is installed by `DriverEntry` and may also be resubmitted by `AFSSubmitLibraryRequest` if an IRP was queued while the library was unavailable. It depends on `AFSCompleteRequest`, `AFSExceptionFilter`, `AFSDbgTrace`, and `AFSDumpTraceFilesFnc` from the shared support layer.

## Risks And Test Signals
Because it always completes, callers expecting pass-through internal IOCTL behavior will fail at this shim. The unused `pIrpSp` assignment is harmless but signals that no control-code filtering exists. Test with an internal-device-control IRP against both control and redirector devices and verify completion status, no library in-flight accounting, and exception dump behavior if stack access faults.
