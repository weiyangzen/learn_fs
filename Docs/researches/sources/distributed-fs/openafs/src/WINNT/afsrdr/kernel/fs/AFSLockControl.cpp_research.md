# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSLockControl.cpp

## Purpose
`AFSLockControl.cpp` implements the `IRP_MJ_LOCK_CONTROL` dispatch shim. Lock and unlock IRPs for redirector file objects are forwarded to the loaded library driver; control-device requests are rejected.

## Important APIs, Control Flow, And State
`AFSLockControl` rejects `AFSDeviceObject` with `STATUS_INVALID_DEVICE_REQUEST`, then calls `AFSCheckLibraryState`. If the library is absent, the IRP may be queued and returned as `STATUS_PENDING`; if the gate fails, the IRP is completed with the error. On success it calls `IoSkipCurrentIrpStackLocation`, forwards to `LibraryDeviceObject` with `IoCallDriver`, and immediately calls `AFSClearLibraryRequest` to release the unload guard for the caller's library submission.

## Dependencies And Integration Points
The implementation depends on `AFSLibrarySupport.cpp` for queueing and in-flight accounting, `AFSCompleteRequest` for local completion, and exception/dump tracing. The real byte-range lock semantics live in the library driver; this layer is a state gate and pass-through.

## Risks And Test Signals
The shim assumes the library owns completion after `IoCallDriver`; completing locally after forwarding would be wrong. Exception handling completes with the exception status, but only after dumping trace state. Tests should cover control-device rejection, absent-library queuing, normal pass-through to library, unload while lock IRPs are in flight, and lock/unlock failures propagated from the library.
