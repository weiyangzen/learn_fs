# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSInternalDevControl.cpp

## Purpose

`AFSInternalDevControl.cpp` implements the `IRP_MJ_INTERNAL_DEVICE_CONTROL` dispatch hook for the library device. In this source it is a deliberate stub: all internal device-control requests are completed with `STATUS_NOT_IMPLEMENTED`.

## Important APIs, types, and functions

`AFSInternalDevControl(PDEVICE_OBJECT, PIRP)` is installed by `DriverEntry`. It calls `IoGetCurrentIrpStackLocation`, though the resulting stack pointer is not inspected. Completion and diagnostics use `AFSCompleteRequest`, `AFSExceptionFilter`, `AFSDbgTrace`, and `AFSDumpTraceFilesFnc`.

## Control flow

The function ignores `LibDeviceObject`, initializes `ntStatus` to `STATUS_NOT_IMPLEMENTED`, obtains the current IRP stack location, enters an exception-guarded block, completes the IRP with that status, and returns it. If completion or surrounding code raises, the exception path logs and dumps trace files, then returns the initialized status.

## State and persistence behavior

There is no persistent state and no mutation of driver structures. The only side effect is completing the IRP. All IOCTL codes, buffer methods, and caller contexts receive identical behavior because the IRP stack is not inspected.

## Dependencies and integration points

The dispatch is wired in `AFSInit.cpp` for `IRP_MJ_INTERNAL_DEVICE_CONTROL`. It depends only on common OpenAFS completion and exception-tracing helpers, not on file, cache, service, or redirector state.

## Risks and test signals

Any future filter-stack or private internal IOCTL expectation will fail until this stub grows real switch logic. The unused stack-location variable is a useful signal that functionality may have been reserved but never implemented. Tests should verify single completion with `STATUS_NOT_IMPLEMENTED`, no pending IRP leak, no information payload, and stable behavior under malformed internal device-control requests.
