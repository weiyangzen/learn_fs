## sources/distributed-fs/beegfs/storage/source/net/message/session/FSyncLocalFileMsgEx.h

### Purpose
`FSyncLocalFileMsgEx.h` declares the storage-side fsync handler for local chunk file sessions.

### Important APIs, Types, And Functions
The class derives from `FSyncLocalFileMsg`, overrides `processIncoming(ResponseContext&)`, and has a private `fsync()` helper returning `FhgfsOpsErr`.

### Control Flow, State, And Persistence
The handler has no additional data members. Inherited session, handle, target, and feature flags drive fsync behavior.

### Dependencies, Integration Points, Risks, And Test Signals
It is factory-created for `NETMSGTYPE_FSyncLocalFile`. Tests should validate response codes and session lookup behavior implemented in the `.cpp`.
