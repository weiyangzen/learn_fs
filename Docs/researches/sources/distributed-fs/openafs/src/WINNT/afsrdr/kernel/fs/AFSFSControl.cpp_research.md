# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFSControl.cpp

Purpose: handles filesystem-control IRPs (`IRP_MJ_FILE_SYSTEM_CONTROL`) for the redirector by rejecting the control device and forwarding valid redirector requests to the library.

Important APIs/types/functions: `AFSFSControl()` checks for `AFSDeviceObject`, returns `STATUS_INVALID_DEVICE_REQUEST` for control requests, gates on `AFSCheckLibraryState()`, forwards via `IoCallDriver()`, and clears the library request marker.

Control flow: this is a standard dispatch wrapper. It completes local failures and transfers ownership to the library on success.

State/persistence: no local persistent state. Filesystem-control operations may affect mount/volume state in the library.

Dependencies/integration: uses `AFSDeviceObject`, the control extension's `LibraryDeviceObject`, `AFSCompleteRequest()`, and exception tracing.

Risks: FSCTLs are broad and security-sensitive; detailed validation is delegated. The wrapper must not complete IRPs after library ownership transfer or while pending in `AFSCheckLibraryState()`.

Test signals: control-device FSCTL rejection, forwarding of mount/volume FSCTLs, library-state pending/failure behavior, and completion status propagation.
