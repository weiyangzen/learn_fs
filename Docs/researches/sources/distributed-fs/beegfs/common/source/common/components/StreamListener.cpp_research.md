<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StreamListener.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/StreamListener.cpp

### Purpose
`StreamListener.cpp` implements the TCP/RDMA stream acceptor and event dispatcher. It accepts incoming connections, watches active sockets with epoll one-shot edge-triggered events, hands sockets to worker queues, and re-arms returned sockets.

### Important APIs, Types, And Functions
Key methods are constructor/destructor, `initSockReturnPipe`, `initSocks`, `run`, `listenLoop`, `onIncomingStandardConnection`, `onIncomingRDMAConnection`, `onIncomingData`, `onSockReturn`, `rdmaConnIdleCheck`, `applySocketOptions`, `isFalseAlarm`, and `deleteAllConns`.

### Control Flow
Construction creates epoll, a nonblocking return pipe, RDMA listen socket if local capabilities allow, and a TCP listen socket. The listen loop waits on epoll, dispatches listen sockets to accept handlers, dispatches returned socket pipe events to re-arm sockets, and dispatches data sockets to workers. TCP accepts apply TCP options and add accepted sockets with `EPOLLONESHOT | EPOLLET`. RDMA accept loops through delayed CM events and ignores internal events. Incoming data on RDMA first calls `nonblockingRecvCheck` to avoid blocking on false alarms. Real data creates `IncomingDataWork`, marks activity, queues direct or indirect work, and removes the socket from `pollList` until a worker returns it via pipe.

### State, Persistence, And Dependencies
State includes listen sockets, work queue, epoll fd, `PollList`, return pipe, RDMA idle-check timer/counter, and log context. No durable persistence. Dependencies include `AbstractApp`, `IncomingDataWork`, `StandardSocket`, `RDMASocket`, `Pipe`, `PollList`, `NetworkInterfaceCard`, and epoll.

### Integration Points
This is the main network ingress for stream messages. Worker code must return sockets through `sockReturnPipe` after processing so epoll can be re-armed. RDMA behavior depends on `RDMASocketImpl` and `IBVSocket` false-alarm semantics.

### Risks
Ownership moves between `pollList`, worker queue, and return pipe; double deletion or lost sockets are the key hazards. `onSockReturn` reads batches of raw socket pointers and has delicate partial-pointer handling. RDMA idle check deletes inactive RDMA sockets without active probing. RDMA accept currently loops only while `checkDelayedEvents()` returns true, so behavior depends on that function detecting the current readiness event. Edge-triggered one-shot use requires every return path to re-arm correctly.

### Test Signals
Tests should cover TCP accept and socket option failures, RDMA accept ignore/success paths, false-alarm rearming, worker handoff and return pipe batching, epoll rearm failure cleanup, idle RDMA disposal, destructor cleanup, and stress with many simultaneous events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StreamListener.cpp -->
