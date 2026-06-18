## sources/distributed-fs/beegfs/storage/source/net/message/fsck/MoveChunkFileMsgEx.h

### Purpose
`MoveChunkFileMsgEx.h` declares the storage-side fsck chunk move handler.

### Important APIs, Types, And Functions
The class derives from `MoveChunkFileMsg`, overrides `processIncoming(ResponseContext&)`, and keeps `moveChunk()` private as the local filesystem operation helper.

### Control Flow, State, And Persistence
The handler has no own state beyond inherited request fields. Persistence is performed by `moveChunk()` in the `.cpp`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common fsck move request/response message classes. Tests should verify factory dispatch and direct `processIncoming()` response codes for move success/failure.
