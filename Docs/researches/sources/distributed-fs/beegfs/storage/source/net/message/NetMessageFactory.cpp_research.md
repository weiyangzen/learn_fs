## sources/distributed-fs/beegfs/storage/source/net/message/NetMessageFactory.cpp

### Purpose
`NetMessageFactory.cpp` is the storage daemon's message type factory. It maps incoming BeeGFS wire message type IDs to concrete storage-side message handler objects.

### Important APIs, Types, And Functions
`NetMessageFactory::createFromMsgType()` switches over `NETMSGTYPE_*` constants and returns a `std::unique_ptr<NetMessage>`. The cases cover control, node, storage, session, monitoring, fsck, benchmark, chunk balancing, and optional NVFS RDMA messages. Unknown IDs produce `SimpleMsg(NETMSGTYPE_Invalid)`.

### Control Flow, State, And Persistence
The factory is stateless. Its control flow is a single switch grouped by message domain. Persistent behavior is indirect: choosing `*MsgEx` classes determines which `processIncoming()` methods can mutate storage state.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on a broad set of common response messages and storage-specific `*MsgEx` includes. Integration is central to message deserialization in the storage app. Risks include missing cases for new protocol messages, accidentally instantiating a common base instead of a storage handler, compile differences under `BEEGFS_NVFS`, and long switch maintenance. Tests should instantiate every expected storage message type, verify invalid fallback, and check RDMA cases under NVFS builds.
