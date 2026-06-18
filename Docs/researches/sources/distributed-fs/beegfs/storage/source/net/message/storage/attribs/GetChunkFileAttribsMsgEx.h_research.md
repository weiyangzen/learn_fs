## sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/GetChunkFileAttribsMsgEx.h

### Purpose
`GetChunkFileAttribsMsgEx.h` declares the storage-side chunk dynamic attribute query handler.

### Important APIs, Types, And Functions
The class derives from `GetChunkFileAttribsMsg`, overrides `processIncoming(ResponseContext&)`, and declares private helper `getTargetFD(const StorageTarget&, ResponseContext&, bool*)`.

### Control Flow, State, And Persistence
No state is stored in the handler. The helper's `outResponseSent` contract supports early `GenericResponseMsg` replies when mirrored target consistency is unsuitable.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common get-attribs message definitions and `StorageTarget`. Tests should validate normal response, early response suppression, and target FD selection for normal and mirrored chunks.
