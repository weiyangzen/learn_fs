# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCleanup.cpp

Purpose: handles `IRP_MJ_CLEANUP` for both the control device and redirector device path. It tears down service/redirector instances opened on the control device and forwards real file cleanup requests to the library device.

Important APIs/types/functions: `AFSCleanup()` is the top-level dispatch handler. It detects `AFS_CONTROL_INSTANCE` to call `AFSCleanupIrpPool()` and `AFSDeregisterService()`, detects `AFS_REDIRECTOR_INSTANCE` to call `AFSCloseRedirector()`, and otherwise delegates to `AFSCommonCleanup()`. `AFSCommonCleanup()` validates the FCB and library state, forwards the IRP to `LibraryDeviceObject`, and marks `FO_CLEANUP_COMPLETE` if completing locally.

Control flow: control-device cleanup is completed immediately after instance-specific cleanup. Redirector file cleanup skips root opens and redirector FCBs, then calls `AFSCheckLibraryState()`. If the library returns pending, the IRP remains owned by the library path. Otherwise the stack is skipped, the request is called into the library, and `AFSClearLibraryRequest()` is invoked.

State/persistence: may shut down the communication IRP pool and service registration, close redirector state, and set `FO_CLEANUP_COMPLETE` on local completion. No durable persistence.

Dependencies/integration: uses control flags stored in `FileObject->FsContext`, global `AFSDeviceObject`, `AFSDeviceExt`, library-device forwarding, `AFSCommSupport.cpp` pool cleanup, and exception/trace helpers.

Risks: correctness depends on `FsContext` being either a flag-bearing control instance or an `AFSFcb` depending on device object. Pending library-state handling must avoid double completion. Cleanup closes service resources, so stale control handles can affect all queued service requests.

Test signals: control-device handle cleanup after initialization, redirector instance cleanup, root-open cleanup, library unavailable/pending/successful forwarding, and FO flag setting only for locally completed file cleanup.
