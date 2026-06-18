# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFileInfo.cpp

Purpose: handles file information query and set IRPs by rejecting control/root opens and forwarding regular redirector file-object operations to the library.

Important APIs/types/functions: `AFSQueryFileInfo()` handles query information. `AFSSetFileInfo()` handles set information. Both validate `DeviceObject`, extract `AFSFcb` from `FileObject->FsContext`, reject null or `AFS_REDIRECTOR_FCB` root opens, call `AFSCheckLibraryState()`, and forward to `LibraryDeviceObject`.

Control flow: control-device and root-open requests complete with `STATUS_INVALID_DEVICE_REQUEST`. Regular file-object requests use the standard library-forwarding sequence and clear the library request marker after calling the lower device.

State/persistence: no direct local metadata persistence; all file info reads/updates are delegated. Status and completion are local only for invalid requests.

Dependencies/integration: depends on FCB node typing, global control extension, library-device forwarding, common completion, and exception tracing.

Risks: misclassified root FCBs can prevent legitimate metadata operations or forward invalid ones. Set-information operations can include rename, allocation, disposition, and timestamps, so delegated validation must be comprehensive. Pending library-state behavior must not double-complete.

Test signals: query/set on control device, root redirector open rejection, regular file query/set forwarding, library unavailable/pending, and exception status conversion to `STATUS_UNSUCCESSFUL`.
