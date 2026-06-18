# sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.cpp

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.cpp` implements the active stream socket event loop. It owns an epoll set, a PollList of live sockets, and a Pipe used by acceptors/workers to return sockets. It reads only message headers in the listener thread, queues IncomingPreprocessedMsgWork, then re-arms sockets when workers return them. More broadly, it participates in the V2 stream listener pipeline for accepting sockets, preprocessing message headers, dispatching worker jobs, and returning sockets to epoll.

### Important APIs, Types, And Functions
The control flow is constructor -> initSockReturnPipe() -> run()/listenLoop(). epoll events for the pipe call onSockReturn(); events for sockets call onIncomingData(). onIncomingData() filters RDMA false alarms, receives NETMSG_HEADER_LENGTH, deserializes the header, creates work, routes direct or indirect by socket/direct flag and target ID, marks activity, and removes the FD from PollList until return. onSockReturn() drains SockReturnPipeInfo records and ADDs/MODs epoll with EPOLLONESHOT|EPOLLET or immediately processes RDMA buffered data. Detected classes are none; structs ['epoll_event', 'epoll_event', 'epoll_event', 'epoll_event', 'epoll_event', 'epoll_event']; enums none; notable out-of-line methods ['StreamListenerV2::deleteAllConns()', 'StreamListenerV2::initSockReturnPipe()', 'StreamListenerV2::isFalseAlarm()', 'StreamListenerV2::listenLoop()', 'StreamListenerV2::onIncomingData()', 'StreamListenerV2::onSockReturn()', 'StreamListenerV2::rdmaConnIdleCheck()', 'StreamListenerV2::run()'].

### Control Flow
State is epollFD, pollList, sockReturnPipe, rdmaCheckT, rdmaCheckForceCounter, useAggressivePoll, and a StreamListenerWorkQueue. Dependencies include AbstractApp, IncomingPreprocessedMsgWork, StreamListenerWorkQueue, Pipe, PollList, StandardSocket/RDMASocket, NetMessage, and Linux epoll. Persistent effects are network/socket side effects only.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/AbstractApp.h`, `common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h`, `common/toolkit/StringTk.h`, `StreamListenerV2.h`, `sys/epoll.h`. Important local state or payload members include `struct epoll_event epollEvent`, `return false`, `return true`, `struct epoll_event epollEvents[EPOLL_EVENTS_NUM]`, `char msgHeaderBuf[NETMSG_HEADER_LENGTH]`, `NetMessageHeader msgHeader`, `SockReturnPipeInfo returnInfos[SOCKRETURN_SOCKS_NUM]`, `struct epoll_event epollEvent`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, borrowed pointer lifetime and deserialized buffer backing. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/StreamListenerV2.cpp -->
