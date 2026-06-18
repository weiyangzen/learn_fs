# sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.cpp

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.cpp` implements the TCP/RDMA accept thread. It creates epoll state, starts listening sockets from common config, accepts new StandardSocket/RDMASocket connections, applies TCP options, and transfers accepted sockets to the StreamListenerV2 chosen by file descriptor. More broadly, it participates in the V2 stream listener pipeline for accepting sockets, preprocessing message headers, dispatching worker jobs, and returning sockets to epoll.

### Important APIs, Types, And Functions
The main path is constructor -> initSocks()/startRDMASocket() -> run()/listenLoop() -> onIncomingStandardConnection() or onIncomingRDMAConnection(). updateLocalNicList() and handleNewLocalNicCaps() let runtime NIC capability changes add or remove the RDMA listen socket under localNicCapsMutex. RDMA accept loops over delayed events; TCP accepts one socket per event. Detected classes are none; structs ['epoll_event', 'epoll_event', 'epoll_event', 'epoll_event', 'sockaddr_storage', 'sockaddr_storage']; enums none; notable out-of-line methods ['ConnAcceptor::applySocketOptions()', 'ConnAcceptor::handleNewLocalNicCaps()', 'ConnAcceptor::initSocks()', 'ConnAcceptor::listenLoop()', 'ConnAcceptor::onIncomingRDMAConnection()', 'ConnAcceptor::onIncomingStandardConnection()', 'ConnAcceptor::run()', 'ConnAcceptor::startRDMASocket()', 'ConnAcceptor::updateLocalNicList()'].

### Control Flow
Important state is epollFD, tcpListenSock, rdmaListenSock, listenPort, cached NicListCapabilities, and app. Dependencies include AbstractApp, ICommonConfig, StandardSocket, RDMASocket, NetworkInterfaceCard, epoll, StreamListenerV2::SockReturnPipeInfo, SocketAddress, and LogContext. No durable data is written; persistence is accepted socket state.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/AbstractApp.h`, `common/components/worker/IncomingDataWork.h`, `common/components/streamlistenerv2/StreamListenerV2.h`, `common/toolkit/StringTk.h`, `ConnAcceptor.h`, `common/net/sock/IPAddress.h`, `sys/epoll.h`. Important local state or payload members include `struct epoll_event epollEvent`, `return false`, `return false`, `return true`, `return false`, `struct epoll_event epollEvent`, `return false`, `return false`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/ConnAcceptor.cpp -->
