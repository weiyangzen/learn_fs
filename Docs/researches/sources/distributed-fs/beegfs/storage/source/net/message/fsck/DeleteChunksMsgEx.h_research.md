## sources/distributed-fs/beegfs/storage/source/net/message/fsck/DeleteChunksMsgEx.h

### Purpose
`DeleteChunksMsgEx.h` declares the storage-side fsck deletion handler.

### Important APIs, Types, And Functions
`DeleteChunksMsgEx` derives from common `DeleteChunksMsg` and overrides `processIncoming(ResponseContext&)`. It includes both request and response message types.

### Control Flow, State, And Persistence
The header has no state; deletion state and failed chunk lists are local to processing.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with `NetMessageFactory` for `NETMSGTYPE_DeleteChunks`. Risks are primarily in the `.cpp` deletion semantics. Tests should verify the handler can be constructed and dispatched through the factory.
