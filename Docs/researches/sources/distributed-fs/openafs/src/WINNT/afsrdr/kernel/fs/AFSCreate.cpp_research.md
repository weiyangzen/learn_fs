# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSCreate.cpp

Purpose: handles `IRP_MJ_CREATE` for the control device and redirector. It opens the control device, opens the redirector root, or forwards real file creates to the library.

Important APIs/types/functions: `AFSCreate()` chooses control versus redirector handling. `AFSCommonCreate()` validates the current process AuthGroup, treats null filename/root opens as redirector opens, checks library state, and forwards create IRPs. `AFSControlDeviceCreate()` completes control opens with `FILE_OPENED`. `AFSOpenRedirector()` assigns the redirector FCB to `FileObject->FsContext` and returns opened status.

Control flow: control-device creates complete locally. Redirector creates first call `AFSValidateProcessEntry()` for current process AuthGroup tracing. If the file object or name buffer is null, it opens the redirector root locally; otherwise it forwards through `LibraryDeviceObject` after `AFSCheckLibraryState()`.

State/persistence: root opens store `pDeviceExt->Fcb` in the file object's `FsContext`. Process validation may populate process/auth tracking outside this file. No durable persistence.

Dependencies/integration: depends on AuthGroup validation in the control process tree, `AFSDeviceObject`, `AFSRDRDeviceObject`, library-device state, `RtlStringFromGUID()`, and common completion/exception tracing.

Risks: create-time process validation side effects are security-sensitive. Null filename is interpreted as a volume/root open. Pending library state must not complete the IRP locally. Root-open `FsContext` must remain valid through cleanup/close paths.

Test signals: control open, root/volume open, regular file create forwarding, process AuthGroup located/not located, library unavailable and pending states, and exception status translation to `STATUS_ACCESS_DENIED`.
