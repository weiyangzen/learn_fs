# sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.h -->
## sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.h` contains BeeGFS common code for `StreamListenerV2`. More broadly, it participates in the V2 stream listener pipeline for accepting sockets, preprocessing message headers, dispatching worker jobs, and returning sockets to epoll.

### Important APIs, Types, And Functions
Detected classes: [('AbstractApp', ''), ('StreamListenerV2', 'PThread')]. Detected functions: []. Detected classes are [('AbstractApp', ''), ('StreamListenerV2', 'PThread')]; structs ['SockReturnPipeInfo']; enums ['SockPipeReturnType']; notable out-of-line methods none.

### Control Flow
Control flow follows the functions listed above.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/components/worker/queue/StreamListenerWorkQueue.h`, `common/components/ComponentInitException.h`, `common/net/sock/StandardSocket.h`, `common/net/sock/RDMASocket.h`, `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/threading/PThread.h`. Important local state or payload members include `class AbstractApp; // forward declaration`, `SockPipeReturnType returnType`, `Socket* sock`, `AbstractApp*      app`, `LogContext        log`, `int               epollFD`, `PollList          pollList`, `Pipe*             sockReturnPipe`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.h -->
