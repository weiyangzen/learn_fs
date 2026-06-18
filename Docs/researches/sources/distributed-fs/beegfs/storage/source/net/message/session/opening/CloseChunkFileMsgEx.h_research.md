## sources/distributed-fs/beegfs/storage/source/net/message/session/opening/CloseChunkFileMsgEx.h

### Purpose
`CloseChunkFileMsgEx.h` declares the storage-side close handler for chunk file sessions and its dynamic attribute response helpers.

### Important APIs, Types, And Functions
The class derives from `CloseChunkFileMsg` and overrides `processIncoming(ResponseContext&)`. Private `DynamicAttribs` carries size, allocated blocks, mtime, atime, and storage version. Helpers include `forwardToSecondary()`, `getDynamicAttribsByFD()`, `getDynamicAttribsByPath()`, and `close()`.

### Control Flow, State, And Persistence
The handler stores no persistent members; dynamic attributes are local to one request. The helper split reflects the two close paths: network mirror forwarding and local session/file cleanup.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common close message definitions and storage implementation details in the `.cpp`. Tests should validate helper-return response behavior, especially communication errors that suppress the normal close response.
