<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.cpp -->
## sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.cpp

### Purpose
`IBVSocket.cpp` implements a socket-like abstraction over RDMA CM and ibverbs. It handles RDMA connection setup, accept, buffer registration, queue pair creation, flow control, completion polling, shutdown, and optional NVFS RDMA read/write operations.

### Important APIs, Types, And Functions
Public C-style entry points include `IBVSocket_init`, `construct`, `destruct`, `rdmaDevicesExist`, `fork_init_once`, `connectByName`, `connectByIP`, `bind`, `bindToAddr`, `listen`, `accept`, `shutdown`, `recv`, `recvT`, `send`, `checkConnection`, `nonblockingRecvCheck`, `checkDelayedEvents`, getters, timeout/TOS setters, and test connection rejection. Key helpers include `__IBVSocket_createCommContext`, `cleanupCommContext`, `initCommDest`, `parseCommDest`, `postRecv`, `postSend`, `recvWC`, `flowControlOnRecv`, `flowControlOnSendWait`, `waitForRecvCompletionEvent`, `waitForTotalSendCompletion`, `disconnect`, `close`, and `initEpollFD`.

### Control Flow
Client connect resolves address and route, creates a communication context, posts receive buffers, sends private connection data, temporarily switches the CM fd to nonblocking mode, polls for `RDMA_CM_EVENT_ESTABLISHED` with exponential sleep, parses remote private data, and initializes epoll. Server accept consumes delayed or new CM events, validates private data, creates a child context, accepts the request, waits for the subsequent established event, then returns the child socket. Send copies user data into registered send buffers, waits for flow-control credit, posts sends, and waits for completions when all buffers are in use. Receive drains incomplete packet fragments first, waits for flow-control packets when necessary, polls receive completions, and reposts receive buffers.

### State, Persistence, And Dependencies
`IBVSocket` owns RDMA CM channel/id, local and remote `IBVCommDest`, `IBVCommContext`, epoll fd, error state, delayed CM event queue, type of service, timeout config, bind IP, and test rejection counters. `IBVCommContext` owns protection domain, memory regions, completion queues, queue pair, send/recv buffers, flow-control counters, and incomplete send/recv state. All state is process memory and registered memory; cleanup destroys QP/CQs/MRs/CM resources.

### Integration Points
`RDMASocketImpl` translates this API into BeeGFS socket exceptions. `StreamListener` relies on `getRecvCompletionFD`, `getConnManagerFD`, `nonblockingRecvCheck`, and `checkDelayedEvents`. The file depends on `rdmacm`, `ibverbs`, `epoll`, BeeGFS logging, threading app access for device removal, serialization endian helpers, and optional NVFS worker buffer definitions.

### Risks
The code is highly stateful and sensitive to RDMA event ordering. Accepted sockets may receive disconnect events through the listener channel, so cleanup and false alarms require careful coordination. Flow control uses tiny control sends and counters initialized to `bufNum - 1`; off-by-one errors can cause receiver-not-ready timeouts or hangs. Connection setup changes fd blocking mode and must restore it on all paths. `commCfg->bufSize * commCfg->bufNum` can overflow before the max check if types remain `unsigned`. NVFS memory-region caching can grow until socket destruction.

### Test Signals
High-value signals are RDMA loopback connect/listen/accept, rejected and malformed private data, route/address failures, device removal, flow-control exhaustion, partial receive continuation, nonblocking false-alarm clearing, idle disconnect checks, timeout configuration, shutdown with incomplete sends, and valgrind/resource-leak checks for MR/CQ/QP cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.cpp -->
