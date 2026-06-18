# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSClose.cpp

Purpose: handles `IRP_MJ_CLOSE`. Control-device closes complete immediately; redirector file closes are forwarded to the user-mode/library device when appropriate.

Important APIs/types/functions: `AFSClose()` dispatches by device object. `AFSCommonClose()` extracts the FCB, rejects root/redirector FCB closes as local success, calls `AFSCheckLibraryState()`, forwards to `LibraryDeviceObject`, and clears the library request marker.

Control flow: if `DeviceObject == AFSDeviceObject`, the IRP is completed as success. Otherwise the close path checks the FCB from `FileObject->FsContext`; root opens complete locally, regular objects are gated on library state, and non-pending success is transferred with `IoSkipCurrentIrpStackLocation()`/`IoCallDriver()`.

State/persistence: no file state is modified here beyond completion/forwarding. The library path owns any actual close-side teardown of cached file state.

Dependencies/integration: depends on `AFSCommon.h`, `AFSDeviceObject`, `AFSCheckLibraryState()`, `AFSClearLibraryRequest()`, and the library device object in the control extension.

Risks: double completion if library-state pending handling is changed incorrectly. Root/redirector FCB identification depends on valid `NodeTypeCode`. The local `pDeviceExt` assignment is unused except for retrieving the extension and can hide stale assumptions.

Test signals: control close, root close, regular close with library unavailable, pending library queue, successful library forwarding, and exception-path status behavior.
