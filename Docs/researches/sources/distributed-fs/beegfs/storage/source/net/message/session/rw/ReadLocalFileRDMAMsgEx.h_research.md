## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/ReadLocalFileRDMAMsgEx.h

### Purpose
`ReadLocalFileRDMAMsgEx.h` defines the NVFS/RDMA read specialization for the shared read-message template. It reads local chunk data and writes it directly into client-provided RDMA buffers.

### Important APIs, Types, And Functions
When `BEEGFS_NVFS` is enabled, `ReadLocalFileRDMAMsgSender` derives from `ReadLocalFileRDMAMsg` and defines `ReadState` with `RdmaInfo*`, remote buffer address, length, and offset. Template hooks include `sendLengthInfo()`, `readStateSendData()`, `getReadLength()`, `readStateInit()`, `readStateNext()`, and `getBuffers()`. The typedef `ReadLocalFileRDMAMsgEx` binds the sender to `ReadLocalFileMsgExBase`.

### Control Flow, State, And Persistence
The base read state machine performs file open/read/offset handling. This RDMA specialization obtains remote buffer descriptors via `RdmaInfo::next()`, caps each transfer to the current RDMA buffer and worker buffer size, writes data through `Socket::write()` with remote key, and sends final length over the socket.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on NVFS build flags, RDMA-capable sockets, `ReadLocalFileV2MsgEx.h`, and worker buffer sizes. Risks include remote buffer exhaustion, partial RDMA writes, alignment/length boundaries, and final length signaling after RDMA data. Tests require NVFS builds with valid/empty/multiple RDMA buffers, short remote writes, buffer boundary transitions, and fallback compile checks when NVFS is disabled.
