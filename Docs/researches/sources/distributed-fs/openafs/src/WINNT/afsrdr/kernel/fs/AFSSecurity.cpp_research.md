# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSSecurity.cpp

## Purpose
`AFSSecurity.cpp` implements security descriptor query/set dispatch. It rejects control-device and redirector-root FCB operations, then forwards valid file security IRPs to the library driver.

## Important APIs, Control Flow, And State
`AFSSetSecurity` and `AFSQuerySecurity` share the same flow: trace entry, reject `AFSDeviceObject`, fetch `AFSFcb` from `FileObject->FsContext`, reject missing FCB or `AFS_REDIRECTOR_FCB` root opens, call `AFSCheckLibraryState`, complete on gate failure unless queued, skip the current stack, forward to `LibraryDeviceObject`, and call `AFSClearLibraryRequest`.

## Dependencies And Integration Points
The handlers depend on FCB node type definitions from shared redirector structures, library gating, common completion, and exception/dump support. Actual ACL/security descriptor semantics are delegated to the library driver.

## Risks And Test Signals
The code assumes `FileObject` and `FsContext` are valid when non-control device security IRPs arrive; malformed IRPs can fault into the exception path. Root opens are intentionally denied, so behavior must align with Windows expectations for network root security queries. Tests should cover root FCB rejection, null FsContext rejection, query and set forwarding, queued behavior during library load, and propagation of library security failures.
