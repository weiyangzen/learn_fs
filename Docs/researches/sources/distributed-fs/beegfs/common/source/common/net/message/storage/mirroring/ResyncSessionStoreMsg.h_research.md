<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreMsg.h

### Purpose
`ResyncSessionStoreMsg` transfers a serialized session store as extra stream data after a small header payload that announces the buffer size.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<ResyncSessionStoreMsg>` with `NETMSGTYPE_ResyncSessionStore`. Serialization writes only `sessionStoreBufSize`. `registerStreamoutHook()` installs `streamToSocketFn()` into `RequestResponseArgs` to send the actual buffer. `receiveStoreBuf()` allocates a buffer and reads exactly `sessionStoreBufSize` bytes with a timeout.

### Control Flow
The normal send path serializes the size, then the request/response framework calls the extra-data hook to stream the buffer. The receive path deserializes the size first, then explicitly receives the store bytes from the socket.

### State, Persistence, And Dependencies
The message owns deserialized storage through `parsed.sessionStoreBuf`; send-side memory is non-owned. The payload represents persistent session state to restore on a buddy or resync target. Dependencies include `MessagingTk`, `Socket`, and exact-timeout receive helpers.

### Integration Points
Metadata resync uses it when synchronizing open/session state between buddies.

### Risks
`streamToSocketFn()` does not verify that `send()` wrote the full buffer beyond relying on socket semantics/exceptions. `receiveStoreBuf()` allocates based on wire size, so receiver-side size limits must exist in handlers. Tests should cover zero-size stores, allocation failure, short reads, timeout behavior, and extra-data hook registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreMsg.h -->
