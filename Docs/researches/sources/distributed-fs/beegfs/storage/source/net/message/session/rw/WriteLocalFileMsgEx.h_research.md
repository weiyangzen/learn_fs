## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileMsgEx.h

### Purpose
`WriteLocalFileMsgEx.h` declares the generic write state machine and TCP write protocol specialization for storage chunk writes.

### Important APIs, Types, And Functions
`WriteStateBase` stores receive sizing, remaining bytes, write offset, and session file pointer. `WriteLocalFileMsgExBase<Msg, WriteState>` owns `mirrorToSock`, `mirrorRetriesLeft`, and shared write helpers: `write()`, `doWrite()`, `openFile()`, mirroring setup/send/finish, session checking, incremental receive/write, and receive-padding. `WriteLocalFileMsgSender` implements TCP receive and `WriteLocalFileRespMsg` response hooks. The typedef `WriteLocalFileMsgEx` binds the TCP sender to the base.

### Control Flow, State, And Persistence
The CRTP design shares file/session/mirror logic between TCP and RDMA variants. `WRITEMSG_MIRROR_RETRIES_NUM` allows one mirror retry, but the implementation limits retry to safe pre-payload points.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on common write message/response classes, `SessionLocalFile`, storage errors, and sockets. Risks include template hook mismatch, raw socket pointer lifetime, integer sign conversions for negative error responses, and stateful retry counters per handler object. Tests should instantiate TCP/RDMA variants, validate response encoding, receive chunk sizing, and mirror retry counter behavior.
