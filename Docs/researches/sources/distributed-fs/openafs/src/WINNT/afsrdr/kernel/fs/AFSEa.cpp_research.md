# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSEa.cpp

Purpose: handles extended attribute query and set IRPs. The control device returns EA-not-supported immediately, while redirector objects are forwarded to the library if available.

Important APIs/types/functions: `AFSQueryEA()` handles `IRP_MJ_QUERY_EA`. `AFSSetEA()` handles `IRP_MJ_SET_EA`. Both default to `STATUS_EAS_NOT_SUPPORTED`, reject `AFSDeviceObject`, call `AFSCheckLibraryState()`, and forward to the library device on success.

Control flow: both functions share the same pattern: local invalid/not-supported completion for control device, library-state gate, then `IoSkipCurrentIrpStackLocation()` and `IoCallDriver()` for redirector objects.

State/persistence: no local state or EA persistence. Any actual EA behavior is delegated to the library.

Dependencies/integration: depends on shared control extension, `LibraryDeviceObject`, `AFSCheckLibraryState()`, and `AFSClearLibraryRequest()`.

Risks: the initial status communicates unsupported EAs for control-device requests, but redirector objects can still be library-handled; callers must not infer global EA absence from this wrapper alone. Pending and error completion rules mirror other wrappers and must stay consistent.

Test signals: query/set EA on control device, query/set EA on redirector when library ready/unavailable/pending, and exception path trace dump.
