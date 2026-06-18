## sources/distributed-fs/beegfs/storage/source/net/message/session/rw/WriteLocalFileRDMAMsgEx.h

### Purpose
`WriteLocalFileRDMAMsgEx.h` defines the NVFS/RDMA write specialization. It reads client data from remote RDMA buffers and feeds the shared local write/mirror state machine.

### Important APIs, Types, And Functions
When `BEEGFS_NVFS` is enabled, `WriteLocalFileRDMAMsgSender` derives from `WriteLocalFileRDMAMsg` and defines `WriteState` with RDMA descriptor state plus original receive size. Hooks include `recvPadding()`, `sendResponse()` using `WriteLocalFileRDMARespMsg`, `writeStateInit()`, `writeStateRecvData()`, and `writeStateNext()`. The typedef `WriteLocalFileRDMAMsgEx` binds it to `WriteLocalFileMsgExBase`.

### Control Flow, State, And Persistence
The RDMA specialization advances through `RdmaInfo` remote buffers, caps each read to remaining request bytes, remaining RDMA buffer bytes, and `WORKER_BUFIN_SIZE`, and signals an error if RDMA buffers are exhausted before all data is received. Local persistence is handled by the shared base write path.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on NVFS build flags, RDMA socket read support, common RDMA messages/responses, and the write base template. Risks include RDMA buffer exhaustion, partial RDMA reads, inconsistent `recvSize` accounting, and compile-only coverage when NVFS is disabled. Tests should cover empty/multiple RDMA buffers, buffer-boundary transitions, short RDMA reads, response codes, and normal non-NVFS builds.
