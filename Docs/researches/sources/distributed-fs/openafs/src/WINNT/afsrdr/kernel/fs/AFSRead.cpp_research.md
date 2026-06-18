# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSRead.cpp

## Purpose
`AFSRead.cpp` implements the `IRP_MJ_READ` dispatch shim. It validates that reads target the redirector device, gates them on library availability, and forwards accepted IRPs to the loaded library driver.

## Important APIs, Control Flow, And State
`AFSRead` rejects control-device reads with `STATUS_INVALID_DEVICE_REQUEST`. It then calls `AFSCheckLibraryState`; failure completes locally, `STATUS_PENDING` means the request has been queued, and success increments the library in-flight count. The routine skips the current stack location, calls `IoCallDriver` on `LibraryDeviceObject`, and balances the in-flight count with `AFSClearLibraryRequest`. Exception handling dumps traces and returns `STATUS_INSUFFICIENT_RESOURCES` without local completion in that exceptional path.

## Dependencies And Integration Points
The real read path is in the library driver; this shim depends on `AFSLibrarySupport.cpp` for gating and unload safety, the control device extension for `LibraryDeviceObject`, and common completion/exception/dump utilities.

## Risks And Test Signals
Read IRPs can be queued while the library is loading, so callers must handle `STATUS_PENDING`. Since no completion routine is installed, the unload guard only protects submission, not asynchronous completion; this is intentional for normal reads but differs from writes. Tests should cover control-device rejection, library absent queued reads, pass-through success/failure propagation, unload racing with read submission, and exception behavior.
