<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.h -->
## sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.h

### Purpose
This internal header defines the concrete RDMA socket data structures and helper prototypes used by `IBVSocket.cpp`.

### Important APIs, Types, And Functions
It defines work-id offsets, private-data protocol constants, `IBVIncompleteRecv`, `IBVIncompleteSend`, `IBVTimeoutConfig`, packed `IBVCommDest`, `IBVCommContext`, and `IBVSocket`. It declares helper functions for context construction, buffer registration, private-data parsing, posting recv/send/read/write work requests, flow control, completion waiting, disconnect/close, and epoll setup.

### Control Flow
The structures encode the lifecycle: CM id/channel first, communication context creation after route/connect request, local/remote destination exchange during handshake, then queue operations and completion polling after connection establishment.

### State, Persistence, And Dependencies
State includes registered memory regions, CQs, QP, buffers, flow-control counters, incomplete transfer markers, delayed CM events, and timeout settings. The header depends on BeeGFS common utilities, serialization endian conversion, sockets, polling, `infiniband/verbs.h`, and `rdma/rdma_cma.h`.

### Integration Points
Only the RDMA socket implementation should include this header. `OpenTk_IBVSocket.h` exposes the smaller public C interface to the C++ adapter.

### Risks
The packed `IBVCommDest` is a wire/private-data ABI and must remain architecture-stable. Work-id constants are used to classify completions; changing them can break send/recv/read/write accounting. Many fields are raw pointers with manual ownership.

### Test Signals
ABI-sensitive tests should verify `sizeof(IBVCommDest)`, endian conversions, work-id classification, and cleanup behavior after partial context construction failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.h -->
