## sources/distributed-fs/beegfs/storage/source/net/message/fsck/FetchFsckChunkListMsgEx.h

### Purpose
`FetchFsckChunkListMsgEx.h` declares the storage-side handler for fsck chunk enumeration polling.

### Important APIs, Types, And Functions
The class inherits `FetchFsckChunkListMsg` and overrides `processIncoming(ResponseContext&)`. It includes the common response message type used to return chunks and status.

### Control Flow, State, And Persistence
No state is stored in the handler object beyond the deserialized request. Runtime state is delegated to `ChunkFetcher`.

### Dependencies, Integration Points, Risks, And Test Signals
It is instantiated by `NetMessageFactory` for fsck list requests. Tests should confirm factory construction and response generation through the `.cpp` behavior.
