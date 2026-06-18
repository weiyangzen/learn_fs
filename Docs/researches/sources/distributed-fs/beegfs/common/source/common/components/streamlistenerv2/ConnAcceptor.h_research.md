# sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.h -->
## sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.h` contains BeeGFS common code for `ConnAcceptor`. More broadly, it participates in the V2 stream listener pipeline for accepting sockets, preprocessing message headers, dispatching worker jobs, and returning sockets to epoll.

### Important APIs, Types, And Functions
Detected classes: [('AbstractApp', ''), ('ConnAcceptor', 'PThread')]. Detected functions: []. Detected classes are [('AbstractApp', ''), ('ConnAcceptor', 'PThread')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the functions listed above.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/components/worker/queue/MultiWorkQueue.h`, `common/components/ComponentInitException.h`, `common/net/sock/StandardSocket.h`, `common/net/sock/RDMASocket.h`, `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/threading/PThread.h`. Important local state or payload members include `class AbstractApp; // forward declaration`, `AbstractApp*      app`, `LogContext        log`, `unsigned short    listenPort`, `StandardSocket*   tcpListenSock`, `RDMASocket*       rdmaListenSock`, `int               epollFD`, `NicListCapabilities  localNicCaps`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.h -->
