# subset-b-000544 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.cpp` processes a message after StreamListenerV2 has already read its header. It receives the remaining payload, creates a concrete NetMessage, enforces channel authentication, invokes processIncoming(), and either releases or invalidates the socket. More broadly, it participates in the V2 stream listener pipeline for accepting sockets, preprocessing message headers, dispatching worker jobs, and returning sockets to epoll.

### Important APIs, Types, And Functions
process() attaches stats, checks payload length against the worker buffer, recvExactT()s the payload, calls AbstractNetMessageFactory::createFromPreprocessedBuf(), rejects NETMSGTYPE_Invalid, checks cfg->getConnAuthHash()/socket authentication, builds NetMessage::ResponseContext, then handles msg->getReleaseSockAfterProcessing(). releaseSocket() unsets stats, checks RDMA immediate data, and writes a SockReturnPipeInfo back to the listener. invalidateConnection() shutdowns then deletes the socket. Detected classes are none; structs none; enums none; notable out-of-line methods ['IncomingPreprocessedMsgWork::checkRDMASocketImmediateData()', 'IncomingPreprocessedMsgWork::invalidateConnection()', 'IncomingPreprocessedMsgWork::process()', 'IncomingPreprocessedMsgWork::releaseSocket()'].

### Control Flow
State is app, sock, copied NetMessageHeader, and inherited HighResolutionStats. Dependencies include AbstractApp, PThread current app, NetMessage, Socket/RDMASocket, StreamListenerV2, and LogContext.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/app/AbstractApp.h`, `common/components/streamlistenerv2/StreamListenerV2.h`, `common/threading/PThread.h`, `common/net/message/NetMessage.h`, `IncomingPreprocessedMsgWork.h`. Important local state or payload members include `std::unique_ptr<NetMessage> msg`, `return false`, `return false; // no more data available at the moment`, `return true`, `return true`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_AuthenticateChannel`, `NETMSGTYPE_Invalid`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h` contains BeeGFS common code for `IncomingPreprocessedMsgWork`. More broadly, it participates in the V2 stream listener pipeline for accepting sockets, preprocessing message headers, dispatching worker jobs, and returning sockets to epoll.

### Important APIs, Types, And Functions
Detected classes: [('IncomingPreprocessedMsgWork', 'Work'), ('is', '')]. Detected functions: []. Detected classes are [('IncomingPreprocessedMsgWork', 'Work'), ('is', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the functions listed above.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/AbstractApp.h`, `common/components/worker/Work.h`, `common/net/message/NetMessage.h`, `common/net/sock/Socket.h`, `common/Common.h`. Important local state or payload members include `AbstractApp* app`, `Socket* sock`, `NetMessageHeader msgHeader`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/DecAtomicWork.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/DecAtomicWork.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/DecAtomicWork.cpp` is a tiny translation unit for `DecAtomicWork` related template/header code. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
The file only includes headers and declares no standalone runtime APIs. Included dependencies are IncAtomicWork.h. Detected classes are none; structs none; enums none; notable out-of-line methods none.

### Control Flow
There is no runtime control flow; its role is build/link participation for the corresponding header-defined template or inline code.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `IncAtomicWork.h`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/DecAtomicWork.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/DecAtomicWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/DecAtomicWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/DecAtomicWork.h` defines or implements worker component `DecAtomicWork` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('TemplateType', ''), ('DecAtomicWork', 'Work')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/app/log/LogContext.h, common/components/worker/Work.h, common/threading/Atomics.h. Detected classes are [('TemplateType', ''), ('DecAtomicWork', 'Work')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/components/worker/Work.h`, `common/threading/Atomics.h`. Important local state or payload members include `Atomic<TemplateType>* atomicValue`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/DecAtomicWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/DummyWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/DummyWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/DummyWork.h` defines or implements worker component `DummyWork` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('DummyWork', 'Work')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include Work.h. Detected classes are [('DummyWork', 'Work')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `Work.h`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/DummyWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp` implements worker-side quota retrieval and aggregation for storage quota queries. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
process() creates GetQuotaInfoMsg, prepareMessage() sets target-selection and ID-list/range/single-ID query mode, requestResponse() fetches GetQuotaInfoRespMsg, mergeOrInsertNewQuotaData() merges QuotaData into a shared QuotaDataMap under quotaResultsMutex, and mergeQuotaInodeSupportUnlocked() combines support states. Every completion increments a SynchronizedCounter and updates result on failures. Detected classes are none; structs none; enums none; notable out-of-line methods ['GetQuotaInfoWork::getIDRangeForMessage()', 'GetQuotaInfoWork::getIDsFromListForMessage()', 'GetQuotaInfoWork::mergeOrInsertNewQuotaData()', 'GetQuotaInfoWork::mergeQuotaInodeSupportUnlocked()', 'GetQuotaInfoWork::prepareMessage()', 'GetQuotaInfoWork::process()'].

### Control Flow
State is borrowed shared quota results, quotaInodeSupport, mutex, counter, result pointer, cfg, storageNode, messageNumber, and storagePoolId. Dependencies include GetQuotaInfoMsg/Resp, MessagingTk, QuotaData, NodeHandle, Mutex, and StringTk.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `GetQuotaInfoWork.h`, `common/net/message/storage/quota/GetQuotaInfoRespMsg.h`, `common/toolkit/MessagingTk.h`, `mutex`. Important local state or payload members include `GetQuotaInfoRespMsg* respMsgCast`, `unsigned startRange, endRange`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_GetQuotaInfoResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h` defines or implements worker component `GetQuotaInfoWork` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('GetQuotaInfoWork', 'Work')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/Common.h, common/net/message/storage/quota/GetQuotaInfoMsg.h, common/nodes/Node.h, common/storage/quota/Quota.h, common/storage/quota/QuotaData.h, common/storage/quota/GetQuotaInfo.h, common/toolkit/SynchronizedCounter.h, Work.h. Detected classes are [('GetQuotaInfoWork', 'Work')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/net/message/storage/quota/GetQuotaInfoMsg.h`, `common/nodes/Node.h`, `common/storage/quota/Quota.h`, `common/storage/quota/QuotaData.h`, `common/storage/quota/GetQuotaInfo.h`, `common/toolkit/SynchronizedCounter.h`, `Work.h`. Important local state or payload members include `GetQuotaInfoConfig cfg;       // configuration qith all information to query the quota data`, `NodeHandle storageNode;       // the node query`, `int messageNumber;            // the message number which is processed by this work`, `QuotaDataMap* quotaResults;   // the quota data from the server after requesting the server`, `QuotaInodeSupport* quotaInodeSupport;  // the support level for inode quota of the blockdevice`, `Mutex* quotaResultsMutex;     // synchronize quotaResults and quotaInodeSupport`, `SynchronizedCounter* counter; // counter for finished worker`, `uint16_t* result;             // result of the worker, 0 if success, if error the TargetNumID`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncAtomicWork.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/IncAtomicWork.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/IncAtomicWork.cpp` is a tiny translation unit for `IncAtomicWork` related template/header code. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
The file only includes headers and declares no standalone runtime APIs. Included dependencies are IncAtomicWork.h. Detected classes are none; structs none; enums none; notable out-of-line methods none.

### Control Flow
There is no runtime control flow; its role is build/link participation for the corresponding header-defined template or inline code.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `IncAtomicWork.h`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncAtomicWork.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncAtomicWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/IncAtomicWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/IncAtomicWork.h` defines or implements worker component `IncAtomicWork` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('TemplateType', ''), ('IncAtomicWork', 'Work')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/app/log/LogContext.h, common/components/worker/Work.h, common/threading/Atomics.h. Detected classes are [('TemplateType', ''), ('IncAtomicWork', 'Work')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/components/worker/Work.h`, `common/threading/Atomics.h`. Important local state or payload members include `Atomic<TemplateType>* atomicValue`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncAtomicWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncSyncedCounterWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/IncSyncedCounterWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/IncSyncedCounterWork.h` defines or implements worker component `IncSyncedCounterWork` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('IncSyncedCounterWork', 'Work')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/app/log/LogContext.h, common/components/worker/Work.h, common/toolkit/SynchronizedCounter.h. Detected classes are [('IncSyncedCounterWork', 'Work')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/components/worker/Work.h`, `common/toolkit/SynchronizedCounter.h`. Important local state or payload members include `SynchronizedCounter* counter`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncSyncedCounterWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.cpp` implements the older stream-worker path that reads the full message, including header, in the worker thread and returns raw Socket* pointers to the legacy StreamListener. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
process() receives NETMSG_MIN_LENGTH, extracts msgLength, receives the rest, uses createFromRaw(), checks auth, calls processIncoming(), unsets stats, checks RDMA immediate data, and writes the socket pointer back to streamListener->getSockReturnFD(). Static helpers delete invalid sockets and create immediate RDMA work when RDMASocket::nonblockingRecvCheck() reports buffered data. Detected classes are none; structs none; enums none; notable out-of-line methods ['IncomingDataWork::checkRDMASocketImmediateData()', 'IncomingDataWork::invalidateConnection()', 'IncomingDataWork::process()'].

### Control Flow
State is streamListener, sock, and inherited stats. Dependencies include StreamListener, AbstractApp, NetMessage, Socket/RDMASocket, PThread, and LogContext.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/app/AbstractApp.h`, `common/threading/PThread.h`, `common/net/message/NetMessage.h`, `IncomingDataWork.h`. Important local state or payload members include `return false`, `return false`, `return true`, `return true`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_AuthenticateChannel`, `NETMSGTYPE_Invalid`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.h` defines or implements worker component `IncomingDataWork` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('IncomingDataWork', 'Work'), ('is', '')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/components/worker/Work.h, common/components/StreamListener.h, common/net/sock/Socket.h. Detected classes are [('IncomingDataWork', 'Work'), ('is', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/components/worker/Work.h`, `common/components/StreamListener.h`, `common/net/sock/Socket.h`. Important local state or payload members include `StreamListener* streamListener`, `Socket* sock`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.cpp` implements a local socket-pair worker for self-directed messages, avoiding deadlocks with the normal queue path. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Construction creates a StandardSocket pair, applies keepalive, and exposes clientEndpoint. run() allocates aligned buffers then workLoop() waits on workerEndpoint. processIncomingData() reads a full NetMessage, deserializes it through the local factory, processes it with locallyGenerated ResponseContext, and invalidates on invalid messages or socket exceptions. Detected classes are none; structs none; enums none; notable out-of-line methods ['LocalConnWorker::applySocketOptions()', 'LocalConnWorker::initBuffers()', 'LocalConnWorker::invalidateConnection()', 'LocalConnWorker::processIncomingData()', 'LocalConnWorker::run()', 'LocalConnWorker::workLoop()'].

### Control Flow
State is workerEndpoint, clientEndpoint, bufIn, bufOut, log, and inherited factory pointer. Dependencies include UnixConnWorker, StandardSocket, NetMessage, AbstractApp/PThread, and ComponentInitException.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/app/AbstractApp.h`, `common/components/worker/Worker.h`, `common/net/message/NetMessage.h`, `common/threading/PThread.h`, `LocalConnWorker.h`. Important local state or payload members include `HighResolutionStats stats; // ignored currently`, `return false`, `return false`, `return false`, `return true`, `return false`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_Invalid`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.h` defines or implements worker component `LocalConnWorker` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('LocalConnWorker', 'UnixConnWorker')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/components/ComponentInitException.h, common/components/worker/UnixConnWorker.h, common/threading/PThread.h, common/net/sock/StandardSocket.h. Detected classes are [('LocalConnWorker', 'UnixConnWorker')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/components/ComponentInitException.h`, `common/components/worker/UnixConnWorker.h`, `common/threading/PThread.h`, `common/net/sock/StandardSocket.h`. Important local state or payload members include `char* bufIn`, `char* bufOut`, `StandardSocket* workerEndpoint`, `StandardSocket* clientEndpoint`, `return clientEndpoint`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.cpp` implements per-target local file reads from storage nodes. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
process() resolves targetID to a Node using NodeStoreServers and TargetMapper, then communicate() acquires a stream socket, serializes ReadLocalFileV2Msg, optionally sets READLOCALFILEMSG_FLAG_SESSION_CHECK, sends it, and reads repeated lengthInfo records plus data into the caller buffer until zero or negative status. It releases sockets on clean EOF and invalidates on errors. Detected classes are none; structs none; enums none; notable out-of-line methods ['ReadLocalFileV2Work::communicate()', 'ReadLocalFileV2Work::process()'].

### Control Flow
State is borrowed file handle, destination buffer, target/path info, result slot, readInfo, offset/size/access flags, and firstWriteDoneForTarget. Dependencies include NodeConnPool, ReadLocalFileV2Msg, NodeStoreServers, TargetMapper, StorageErrors, and common config long timeouts.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/app/AbstractApp.h`, `common/threading/PThread.h`, `common/net/message/NetMessage.h`, `common/toolkit/MessagingTk.h`, `common/nodes/NodeStoreServers.h`, `common/storage/StorageErrors.h`, `common/net/message/session/rw/ReadLocalFileV2Msg.h`. Important local state or payload members include `FhgfsOpsErr resolveErr`, `int64_t lengthInfo; // length info in fhgfs host byte order`, `return retVal`, `return retVal`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, borrowed pointer lifetime and deserialized buffer backing. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.h` defines or implements worker component `ReadLocalFileV2Work` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('ReadLocalFileV2Work', 'Work')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/Common.h, common/net/sock/Socket.h, common/components/worker/Work.h, common/storage/PathInfo.h, common/toolkit/SynchronizedCounter.h, common/nodes/NumNodeID.h, common/nodes/TargetMapper.h, common/nodes/NodeStoreServers.h. Detected classes are [('ReadLocalFileV2Work', 'Work')]; structs ['ReadLocalFileWorkInfo']; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/net/sock/Socket.h`, `common/components/worker/Work.h`, `common/storage/PathInfo.h`, `common/toolkit/SynchronizedCounter.h`, `common/nodes/NumNodeID.h`, `common/nodes/TargetMapper.h`, `common/nodes/NodeStoreServers.h`. Important local state or payload members include `NumNodeID localNodeNumID`, `TargetMapper* targetMapper`, `NodeStoreServers* storageNodes`, `SynchronizedCounter* counter`, `const char* fileHandleID`, `char* buf`, `unsigned accessFlags`, `off_t offset`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/UnixConnWorker.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/UnixConnWorker.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/UnixConnWorker.h` defines or implements worker component `UnixConnWorker` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('UnixConnWorker', 'PThread')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/components/ComponentInitException.h, common/net/sock/StandardSocket.h, common/threading/PThread.h. Detected classes are [('UnixConnWorker', 'PThread')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/components/ComponentInitException.h`, `common/net/sock/StandardSocket.h`, `common/threading/PThread.h`. Important local state or payload members include `LogContext log`, `const AbstractNetMessageFactory* netMessageFactory`, `bool available; // == !acquired`, `return available`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/UnixConnWorker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/Work.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/Work.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/Work.h` defines or implements worker component `Work` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('Work', ''), ('Work', '')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/toolkit/HighResolutionStats.h, common/toolkit/TimeFine.h, common/Common.h. Detected classes are [('Work', ''), ('Work', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/toolkit/HighResolutionStats.h`, `common/toolkit/TimeFine.h`, `common/Common.h`. Important local state or payload members include `class Work`, `HighResolutionStats stats`, `TimeFine age`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/Work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.cpp` implements the generic worker thread that executes Work objects from MultiWorkQueue using reusable aligned input/output buffers. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
run() registers signal handling, allocates buffers, validates direct or indirect work type, and calls workLoop(). workLoop() registers the worker in queue stats, waits via waitForWorkByType(), resets stats, calls work->process(), merges high-resolution stats, optionally logs profiling latency, and deletes the Work. initBuffers() uses posix_memalign for NUMA-friendly delayed allocation. Detected classes are none; structs none; enums none; notable out-of-line methods ['Worker::initBuffers()', 'Worker::run()', 'Worker::waitForWorkByType()', 'Worker::workLoop()'].

### Control Flow
State is log, termination policy, buffer sizes/pointers, queue pointer, work type, personal queue, and stats. Dependencies include MultiWorkQueue, PersonalWorkQueue, PThread, HighResolutionStats, TimeFine, and ComponentInitException.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/toolkit/TimeFine.h`, `Worker.h`. Important local state or payload members include `TimeFine workStartTime`, `TimeFine workEndTime`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.h` defines or implements worker component `Worker` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('Worker', 'PThread')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/app/log/LogContext.h, common/app/AbstractApp.h, common/components/worker/queue/MultiWorkQueue.h, common/components/worker/queue/PersonalWorkQueue.h, common/components/ComponentInitException.h, common/threading/PThread.h. Detected classes are [('Worker', 'PThread')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/app/AbstractApp.h`, `common/components/worker/queue/MultiWorkQueue.h`, `common/components/worker/queue/PersonalWorkQueue.h`, `common/components/ComponentInitException.h`, `common/threading/PThread.h`. Important local state or payload members include `LogContext log`, `size_t bufInLen`, `char* bufIn`, `size_t bufOutLen`, `char* bufOut`, `MultiWorkQueue* workQueue`, `QueueWorkType workType`, `PersonalWorkQueue* personalWorkQueue`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.cpp` implements per-target writes to storage nodes. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
process() resolves targetID and communicate() acquires a stream socket, serializes WriteLocalFileMsg, optionally sets WRITELOCALFILEMSG_FLAG_SESSION_CHECK, sends the payload with writeMsg.sendData(), receives a response buffer, checks NETMSGTYPE_WriteLocalFileResp, returns the response value, and releases or invalidates the socket. Completion increments writeInfo->counter. Detected classes are none; structs none; enums none; notable out-of-line methods ['WriteLocalFileWork::communicate()', 'WriteLocalFileWork::process()'].

### Control Flow
State is borrowed file handle, source buffer, path info, result slot, writeInfo, target, offset/size/access flags, and firstWriteDoneForTarget. Dependencies include WriteLocalFileMsg/Resp, MessagingTk, NodeConnPool, NodeStoreServers, TargetMapper, and StorageErrors.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/app/AbstractApp.h`, `common/threading/PThread.h`, `common/net/message/NetMessage.h`, `common/toolkit/MessagingTk.h`, `common/nodes/NodeStoreServers.h`, `common/storage/StorageErrors.h`, `common/net/message/session/rw/WriteLocalFileMsg.h`. Important local state or payload members include `FhgfsOpsErr resolveErr`, `return retVal`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_WriteLocalFileResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.h` defines or implements worker component `WriteLocalFileWork` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('WriteLocalFileWork', 'Work')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/Common.h, common/net/sock/Socket.h, common/components/worker/Work.h, common/toolkit/SynchronizedCounter.h, common/nodes/NumNodeID.h, common/nodes/TargetMapper.h, common/nodes/NodeStoreServers.h. Detected classes are [('WriteLocalFileWork', 'Work')]; structs ['WriteLocalFileWorkInfo']; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/net/sock/Socket.h`, `common/components/worker/Work.h`, `common/toolkit/SynchronizedCounter.h`, `common/nodes/NumNodeID.h`, `common/nodes/TargetMapper.h`, `common/nodes/NodeStoreServers.h`. Important local state or payload members include `NumNodeID localNodeNumID`, `TargetMapper* targetMapper`, `NodeStoreServers* storageNodes`, `SynchronizedCounter* counter`, `const char* fileHandleID`, `const char* buf`, `unsigned accessFlags`, `off_t offset`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/AbstractWorkContainer.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/queue/AbstractWorkContainer.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/queue/AbstractWorkContainer.h` defines queue infrastructure `AbstractWorkContainer` for scheduling Work objects. More broadly, it participates in worker queue scheduling, ownership of Work pointers, condition-variable wakeups, fairness, and queue statistics.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('AbstractWorkContainer', '')]. Methods include enqueue/dequeue, size/empty checks, stats formatting, and condition-variable waits depending on the class. Detected classes are [('AbstractWorkContainer', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow centers on producer enqueue, blocking wait, FIFO or per-user selection, and deletion of leftover Work* in destructors. Synchronization is external for container types and internal for WorkQueue/MultiWorkQueue.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/components/worker/Work.h`, `common/Common.h`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/AbstractWorkContainer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/ListWorkContainer.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/queue/ListWorkContainer.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/queue/ListWorkContainer.h` defines queue infrastructure `ListWorkContainer` for scheduling Work objects. More broadly, it participates in worker queue scheduling, ownership of Work pointers, condition-variable wakeups, fairness, and queue statistics.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('ListWorkContainer', 'AbstractWorkContainer')]. Methods include enqueue/dequeue, size/empty checks, stats formatting, and condition-variable waits depending on the class. Detected classes are [('ListWorkContainer', 'AbstractWorkContainer')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow centers on producer enqueue, blocking wait, FIFO or per-user selection, and deletion of leftover Work* in destructors. Synchronization is external for container types and internal for WorkQueue/MultiWorkQueue.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `AbstractWorkContainer.h`. Important local state or payload members include `WorkList workList`, `return work`, `std::ostringstream statsStream`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/ListWorkContainer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.cpp` implements the synchronized direct/indirect/personal work scheduler used by BeeGFS worker threads and stream listeners. More broadly, it participates in worker queue scheduling, ownership of Work pointers, condition-variable wakeups, fairness, and queue statistics.

### Important APIs, Types, And Functions
waitForDirectWork() blocks until direct or personal work exists, prioritizes the personal queue, adjusts busy-worker stats, and pops direct work. waitForAnyWork() blocks until any global or personal work exists, prioritizes personal work, then rotates through direct/indirect containers using lastWorkListVecIdx. incNumWorkers(), setIndirectWorkList(), and getStatsAsStr() maintain stats and replace the indirect container. Detected classes are none; structs none; enums none; notable out-of-line methods ['MultiWorkQueue::getStatsAsStr()', 'MultiWorkQueue::incNumWorkers()', 'MultiWorkQueue::setIndirectWorkList()', 'MultiWorkQueue::waitForAnyWork()', 'MultiWorkQueue::waitForDirectWork()'].

### Control Flow
State is directWorkList, indirectWorkList, workListVec, numPendingWorks, lastWorkListVecIdx, Mutex, two Conditions, and HighResolutionStats. Dependencies include ListWorkContainer, PersonalWorkQueue, Condition/Mutex, StringTk, and logging/profiling macros.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `MultiWorkQueue.h`, `PersonalWorkQueue.h`. Important local state or payload members include `return work`, `return work`, `return work`, `return work`, `std::ostringstream busyStream`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.h` defines queue infrastructure `MultiWorkQueue` for scheduling Work objects. More broadly, it participates in worker queue scheduling, ownership of Work pointers, condition-variable wakeups, fairness, and queue statistics.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('MultiWorkQueue', ''), ('MultiWorkQueue', 'StreamListenerWorkQueue')]. Methods include enqueue/dequeue, size/empty checks, stats formatting, and condition-variable waits depending on the class. Detected classes are [('MultiWorkQueue', ''), ('MultiWorkQueue', 'StreamListenerWorkQueue')]; structs none; enums ['QueueWorkType']; notable out-of-line methods none.

### Control Flow
Control flow centers on producer enqueue, blocking wait, FIFO or per-user selection, and deletion of leftover Work* in destructors. Synchronization is external for container types and internal for WorkQueue/MultiWorkQueue.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/components/worker/queue/StreamListenerWorkQueue.h`, `common/components/worker/Work.h`, `common/threading/Mutex.h`, `common/threading/Condition.h`, `common/toolkit/NamedException.h`, `common/toolkit/HighResolutionStats.h`, `common/toolkit/Time.h`. Important local state or payload members include `class MultiWorkQueue; // forward declaration`, `AbstractWorkContainer* directWorkList`, `AbstractWorkContainer* indirectWorkList`, `Mutex mutex`, `Condition newDirectWorkCond; // direct workers wait only on this condition`, `WorkListVec workListVec; // used to toggle next work type with nextWorkType as index`, `HighResolutionStats stats`, `return numPendingWorks`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/PersonalWorkQueue.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/queue/PersonalWorkQueue.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/queue/PersonalWorkQueue.h` defines queue infrastructure `PersonalWorkQueue` for scheduling Work objects. More broadly, it participates in worker queue scheduling, ownership of Work pointers, condition-variable wakeups, fairness, and queue statistics.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('has', ''), ('PersonalWorkQueue', ''), ('MultiWorkQueue', '')]. Methods include enqueue/dequeue, size/empty checks, stats formatting, and condition-variable waits depending on the class. Detected classes are [('has', ''), ('PersonalWorkQueue', ''), ('MultiWorkQueue', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow centers on producer enqueue, blocking wait, FIFO or per-user selection, and deletion of leftover Work* in destructors. Synchronization is external for container types and internal for WorkQueue/MultiWorkQueue.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/components/worker/Work.h`, `common/toolkit/NamedException.h`, `common/Common.h`. Important local state or payload members include `friend class MultiWorkQueue; /* to make sure that our methods are not called without the`, `WorkList workList`, `return work`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/PersonalWorkQueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/StreamListenerWorkQueue.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/queue/StreamListenerWorkQueue.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/queue/StreamListenerWorkQueue.h` defines queue infrastructure `StreamListenerWorkQueue` for scheduling Work objects. More broadly, it participates in worker queue scheduling, ownership of Work pointers, condition-variable wakeups, fairness, and queue statistics.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('StreamListenerWorkQueue', '')]. Methods include enqueue/dequeue, size/empty checks, stats formatting, and condition-variable waits depending on the class. Detected classes are [('StreamListenerWorkQueue', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow centers on producer enqueue, blocking wait, FIFO or per-user selection, and deletion of leftover Work* in destructors. Synchronization is external for container types and internal for WorkQueue/MultiWorkQueue.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/components/worker/Work.h`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/StreamListenerWorkQueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/UserWorkContainer.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/queue/UserWorkContainer.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/queue/UserWorkContainer.h` defines queue infrastructure `UserWorkContainer` for scheduling Work objects. More broadly, it participates in worker queue scheduling, ownership of Work pointers, condition-variable wakeups, fairness, and queue statistics.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('UserWorkContainer', 'AbstractWorkContainer')]. Methods include enqueue/dequeue, size/empty checks, stats formatting, and condition-variable waits depending on the class. Detected classes are [('UserWorkContainer', 'AbstractWorkContainer')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow centers on producer enqueue, blocking wait, FIFO or per-user selection, and deletion of leftover Work* in destructors. Synchronization is external for container types and internal for WorkQueue/MultiWorkQueue.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/toolkit/NamedException.h`, `common/Common.h`, `AbstractWorkContainer.h`. Important local state or payload members include `UserWorkMap workMap; // entries added on demand and removed when queue empty`, `size_t numWorks; // number of works in all queues`, `return work`, `return numWorks`, `std::ostringstream statsStream`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/UserWorkContainer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/WorkQueue.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/queue/WorkQueue.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/queue/WorkQueue.h` defines queue infrastructure `WorkQueue` for scheduling Work objects. More broadly, it participates in worker queue scheduling, ownership of Work pointers, condition-variable wakeups, fairness, and queue statistics.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('WorkQueue', '')]. Methods include enqueue/dequeue, size/empty checks, stats formatting, and condition-variable waits depending on the class. Detected classes are [('WorkQueue', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow centers on producer enqueue, blocking wait, FIFO or per-user selection, and deletion of leftover Work* in destructors. Synchronization is external for container types and internal for WorkQueue/MultiWorkQueue.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/components/worker/Work.h`, `common/threading/Mutex.h`, `common/threading/Condition.h`, `common/Common.h`, `mutex`. Important local state or payload members include `return work`, `WorkList workList`, `Mutex mutex`, `Condition newWorkCond`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/queue/WorkQueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckChunk.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckChunk.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckChunk.h` defines the `FsckChunk` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckChunk', ''), ('FsckChunk', ''), ('TestDatabase', '')] []. Key stored fields include FsckChunk, TestDatabase, id, targetID, storeStorageDirectory, byte, usedBlocks, epoch, epoch, epoch. Detected classes are [('FsckChunk', ''), ('FsckChunk', ''), ('TestDatabase', '')]; structs ['ListSerializationHasLength']; enums none; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/storage/Path.h`, `common/storage/PathInfo.h`, `common/toolkit/serialization/Serialization.h`, `iostream`. Important local state or payload members include `class FsckChunk`, `friend class TestDatabase`, `std::string id`, `uint16_t targetID`, `Path savedPath; // the path, where the chunk was found; relative to storeStorageDirectory`, `int64_t fileSize; // in byte`, `uint64_t usedBlocks`, `int64_t creationTime; // secs since the epoch`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckChunk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckContDir.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckContDir.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckContDir.h` defines the `FsckContDir` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckContDir', ''), ('FsckContDir', '')] []. Key stored fields include FsckContDir, id, saveNodeID, isBuddyMirrored, saveNodeID, true, false. Detected classes are [('FsckContDir', ''), ('FsckContDir', '')]; structs ['ListSerializationHasLength']; enums none; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/nodes/NumNodeID.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `class FsckContDir`, `std::string id`, `NumNodeID saveNodeID`, `bool isBuddyMirrored`, `return saveNodeID`, `return true`, `return false`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckContDir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckDirEntry.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckDirEntry.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckDirEntry.h` defines the `FsckDirEntry` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckDirEntry', ''), ('FsckDirEntry', ''), ('TestDatabase', '')] ['FsckDirEntryType', 'FsckDirEntryType']. Key stored fields include FsckDirEntry, TestDatabase, entry, name, parentDirID, entryOwnerNodeID, owner, entryType, hasInlinedInode, isBuddyMirrored. Detected classes are [('FsckDirEntry', ''), ('FsckDirEntry', ''), ('TestDatabase', '')]; structs ['ListSerializationHasLength']; enums ['FsckDirEntryType', 'FsckDirEntryType']; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/nodes/NumNodeID.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `class FsckDirEntry`, `friend class TestDatabase`, `std::string id; // a filesystem-wide identifier for this entry`, `std::string name; // the user-friendly name`, `std::string parentDirID`, `NumNodeID entryOwnerNodeID`, `NumNodeID inodeOwnerNodeID; // 0 for unknown owner`, `FsckDirEntryType entryType`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckDirEntry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckDirInode.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckDirInode.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckDirInode.h` defines the `FsckDirInode` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckDirInode', ''), ('FsckDirInode', ''), ('TestDatabase', '')] []. Key stored fields include FsckDirInode, TestDatabase, string, parentDirID, parentNodeID, ownerNodeID, subentries, numHardLinks, stripeTargets, stripePatternType. Detected classes are [('FsckDirInode', ''), ('FsckDirInode', ''), ('TestDatabase', '')]; structs ['ListSerializationHasLength']; enums none; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/toolkit/FsckTk.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `class FsckDirInode`, `friend class TestDatabase`, `std::string id; // filesystem-wide unique string`, `std::string parentDirID`, `NumNodeID parentNodeID`, `NumNodeID ownerNodeID`, `int64_t size; // # of subentries`, `uint32_t numHardLinks`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckDirInode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h` defines the `FsckDuplicateInodeInfo` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckDuplicateInodeInfo', ''), ('to', ''), ('FsckDuplicateInodeInfo', '')] []. Key stored fields include FsckDuplicateInodeInfo, entryID, parentDirID, saveNodeID, isInlined, isBuddyMirrored, dirEntryType. Detected classes are [('FsckDuplicateInodeInfo', ''), ('to', ''), ('FsckDuplicateInodeInfo', '')]; structs ['ListSerializationHasLength']; enums none; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `class FsckDuplicateInodeInfo`, `std::string entryID`, `std::string parentDirID`, `uint32_t saveNodeID`, `bool isInlined`, `bool isBuddyMirrored`, `DirEntryType dirEntryType`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckDuplicateInodeInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckFileInode.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckFileInode.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckFileInode.h` defines the `FsckFileInode` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckFileInode', ''), ('FsckFileInode', ''), ('TestDatabase', '')] []. Key stored fields include FsckFileInode, TestDatabase, settableFileAttribs, string, parentDirID, parentNodeID, pathInfo, userID, groupID, 512byte-blocks. Detected classes are [('FsckFileInode', ''), ('FsckFileInode', ''), ('TestDatabase', '')]; structs ['ListSerializationHasLength']; enums none; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/toolkit/FsckTk.h`, `common/storage/PathInfo.h`, `common/storage/StatData.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `class FsckFileInode`, `friend class TestDatabase`, `SettableFileAttribs settableFileAttribs`, `std::string id; // filesystem-wide unique string`, `std::string parentDirID`, `NumNodeID parentNodeID`, `PathInfo pathInfo`, `uint32_t userID`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckFileInode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckFsID.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckFsID.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckFsID.h` defines the `FsckFsID` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckFsID', ''), ('FsckFsID', ''), ('TestDatabase', '')] []. Key stored fields include FsckFsID, TestDatabase, id, parentDirID, saveNodeID, saveDevice, saveInode, isBuddyMirrored, true, false. Detected classes are [('FsckFsID', ''), ('FsckFsID', ''), ('TestDatabase', '')]; structs ['ListSerializationHasLength']; enums none; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/nodes/NumNodeID.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `class FsckFsID`, `friend class TestDatabase`, `std::string id`, `std::string parentDirID`, `NumNodeID saveNodeID`, `int32_t saveDevice`, `uint64_t saveInode`, `bool isBuddyMirrored`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckFsID.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckModificationEvent.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckModificationEvent.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckModificationEvent.h` defines the `FsckModificationEvent` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckModificationEvent', ''), ('FsckModificationEvent', ''), ('TestDatabase', '')] []. Key stored fields include FsckModificationEvent, TestDatabase, eventType, entryID, true, true, false, false, false, true. Detected classes are [('FsckModificationEvent', ''), ('FsckModificationEvent', ''), ('TestDatabase', '')]; structs ['ListSerializationHasLength']; enums none; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/toolkit/MetadataTk.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `class FsckModificationEvent`, `friend class TestDatabase`, `ModificationEventType eventType`, `std::string entryID`, `return true`, `return true`, `return false`, `return false`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckModificationEvent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h -->
## sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h` defines the `FsckTargetID` fsck record type used by consistency scans, database comparisons, and fsck messages. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important APIs include list typedefs, constructors including deserialization constructors, getters/setters, comparison operators, and serialize(). Classes/enums: [('FsckTargetID', '')] ['FsckTargetIDType']. Key stored fields include id, targetIDType, id, targetIDType, true, true, false, false, false, true. Detected classes are [('FsckTargetID', '')]; structs ['ListSerializationHasLength']; enums ['FsckTargetIDType']; notable out-of-line methods none.

### Control Flow
Control flow is value-object behavior: construct, compare/order, optionally mutate repair fields, print in a few types, and serialize through BeeGFS serdes. ListSerializationHasLength=false marks list wire format expectations for these fsck objects.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `uint16_t id`, `FsckTargetIDType targetIDType`, `return id`, `return targetIDType`, `return true`, `return true`, `return false`, `return false`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/fsck/FsckTargetID.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/logging/Backtrace.h -->
## sources/distributed-fs/beegfs/common/source/common/logging/Backtrace.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/logging/Backtrace.h` contains BeeGFS common code for `Backtrace`. More broadly, it provides logging support utility code.

### Important APIs, Types, And Functions
Detected classes: [('to', ''), ('Backtrace', ''), ('T', ''), ('Backtrace', '')]. Detected functions: []. Detected classes are [('to', ''), ('Backtrace', ''), ('T', ''), ('Backtrace', '')]; structs ['free_delete']; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the functions listed above.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `execinfo.h`, `memory`, `sstream`. Important local state or payload members include `void* btbuf[LEN + 2]`, `std::ostringstream oss`, `std::string bt`, `return os`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include ordering/equality consistency with serialized fields. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include compile-time inclusion and boundary-value checks for public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/logging/Backtrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/MallocBuffer.h -->
## sources/distributed-fs/beegfs/common/source/common/memory/MallocBuffer.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/memory/MallocBuffer.h` defines memory/string helper type(s) `MallocBuffer` for local non-owning views or malloc-backed ownership. More broadly, it provides allocation-free or malloc-backed memory/string utility types.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('that', ''), ('MallocBuffer', '')]. Members/functions cover data pointers, byte sizes, reset/drop or offset/limit operations, move-only ownership where applicable, and conversions to Slice/String views. Detected classes are [('that', ''), ('MallocBuffer', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is local utility behavior with no external I/O. State is pointer plus size/capacity; persistence is heap allocation for Malloc* classes and borrowed memory for Slice/String classes.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `Slice.h`, `cstdlib`, `utility`. Important local state or payload members include `return mData`, `return mCapacity`, `return false`, `return true`, `return *this`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include compile-time inclusion and boundary-value checks for public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/MallocBuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/MallocString.h -->
## sources/distributed-fs/beegfs/common/source/common/memory/MallocString.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/memory/MallocString.h` defines memory/string helper type(s) `MallocString` for local non-owning views or malloc-backed ownership. More broadly, it provides allocation-free or malloc-backed memory/string utility types.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('MallocString', '')]. Members/functions cover data pointers, byte sizes, reset/drop or offset/limit operations, move-only ownership where applicable, and conversions to Slice/String views. Detected classes are [('MallocString', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is local utility behavior with no external I/O. State is pointer plus size/capacity; persistence is heap allocation for Malloc* classes and borrowed memory for Slice/String classes.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `String.h`. Important local state or payload members include `return mSizeBytes`, `return false`, `return true`, `return *this`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include compile-time inclusion and boundary-value checks for public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/MallocString.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/Slice.h -->
## sources/distributed-fs/beegfs/common/source/common/memory/Slice.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/memory/Slice.h` defines memory/string helper type(s) `Slice` for local non-owning views or malloc-backed ownership. More broadly, it provides allocation-free or malloc-backed memory/string utility types.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('Slice', ''), ('RO_Slice', ''), ('WO_Slice', ''), ('Slice', '')]. Members/functions cover data pointers, byte sizes, reset/drop or offset/limit operations, move-only ownership where applicable, and conversions to Slice/String views. Detected classes are [('Slice', ''), ('RO_Slice', ''), ('WO_Slice', ''), ('Slice', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is local utility behavior with no external I/O. State is pointer plus size/capacity; persistence is heap allocation for Malloc* classes and borrowed memory for Slice/String classes.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `assert.h`, `string.h`. Important local state or payload members include `class Slice`, `return mData`, `return mSize`, `return mData`, `return mSize`, `return mData`, `return mSize`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include compile-time inclusion and boundary-value checks for public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/Slice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/String.h -->
## sources/distributed-fs/beegfs/common/source/common/memory/String.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/memory/String.h` defines memory/string helper type(s) `String` for local non-owning views or malloc-backed ownership. More broadly, it provides allocation-free or malloc-backed memory/string utility types.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('String', ''), ('StringZ', '')]. Members/functions cover data pointers, byte sizes, reset/drop or offset/limit operations, move-only ownership where applicable, and conversions to Slice/String views. Detected classes are [('String', ''), ('StringZ', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is local utility behavior with no external I/O. State is pointer plus size/capacity; persistence is heap allocation for Malloc* classes and borrowed memory for Slice/String classes.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `string.h`, `Slice.h`. Important local state or payload members include `return mData`, `return mSizeBytes`, `return false`, `return false`, `return false`, `return mData`, `return mData`, `return mSizeBytes`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include compile-time inclusion and boundary-value checks for public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/String.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp` implements common NetMessage deserialization and validation before dispatching payloads to concrete message classes. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
createFromRaw() checks NETMSG_MIN_LENGTH, deserializes NetMessageHeader, and delegates to createFromPreprocessedBuf(). createFromPreprocessedBuf() calls virtual createFromMsgType(), applies feature flags, rejects unsupported feature flags, validates generic header flags against supportsMirroring(), copies the header into the message, and calls deserializePayload(). Failures return SimpleMsg(NETMSGTYPE_Invalid). Detected classes are none; structs none; enums none; notable out-of-line methods ['AbstractNetMessageFactory::createFromPreprocessedBuf()', 'AbstractNetMessageFactory::createFromRaw()'].

### Control Flow
No state is retained. Dependencies include NetMessage, SimpleMsg, NetMessageLogHelper, LogContext, StringTk, and serialization. Integration is central to stream workers, LocalConnWorker, and MessagingTk response parsing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/net/message/NetMessageLogHelper.h`, `AbstractNetMessageFactory.h`, `SimpleMsg.h`. Important local state or payload members include `NetMessageHeader header`, `return msg`, `return msg`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_Invalid`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h` defines NetMessage infrastructure or simple payload base `AbstractNetMessageFactory`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('AbstractNetMessageFactory', '')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: handled by derived classes or switch tables. Detected classes are [('AbstractNetMessageFactory', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`. Important local state or payload members include `return result`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include compile-time inclusion and boundary-value checks for public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AcknowledgeableMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/AcknowledgeableMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/AcknowledgeableMsg.h` defines NetMessage infrastructure or simple payload base `AcknowledgeableMsg`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('AcknowledgeableMsg', 'NetMessage'), ('AcknowledgeableMsgSerdes', 'AcknowledgeableMsg')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: serializeAckID. Detected classes are [('AcknowledgeableMsg', 'NetMessage'), ('AcknowledgeableMsgSerdes', 'AcknowledgeableMsg')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `NetMessage.h`, `common/net/message/control/AckMsg.h`. Important local state or payload members include `const char* ackID`, `unsigned ackIDLen`, `return false`, `return true`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AcknowledgeableMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h` defines BeeGFS wire message header layout, base message behavior, response context, and CRTP serialization helpers. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
NetMessageHeader stores length, feature/compat flags, generic flags, BeeGFS data-version prefix, message type, target/user IDs, and sequence fields. NetMessage serializes by writing a header, serializing payload, then fixing the length field; it also exposes feature flag, target/user, sequence, generic flag, and socket-release helpers. ResponseContext sends responses over stream or datagram sockets. NetMessageSerdes and MirroredMessageBase implement common payload patterns. Detected classes are [('NetMessage', ''), ('AbstractNetMessageFactory', ''), ('TestMsgSerializationBase', ''), ('ResponseContext', ''), ('NetMessage', ''), ('NetMessageSerdes', 'NetMessage'), ('MirroredMessageBase', 'NetMessage')]; structs ['NetMessageHeader', 'NetMessageHeader', 'sockaddr', 'sockaddr']; enums none; notable out-of-line methods none.

### Control Flow
State is per-message header, releaseSockAfterProcessing, and optional backingBuffer for vector-backed deserialization. Dependencies include Socket, NetworkInterfaceCard, Serialization, HighResolutionStats, NetMessageTypes, NetMessageLogHelper, and IPAddress.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/sock/NetworkInterfaceCard.h`, `common/net/sock/Socket.h`, `common/toolkit/HighResolutionStats.h`, `common/toolkit/serialization/Serialization.h`, `common/Common.h`, `NetMessageLogHelper.h`, `NetMessageTypes.h`, `common/net/sock/IPAddress.h`. Important local state or payload members include `uint32_t       msgLength; // in bytes`, `uint8_t        msgCompatFeatureFlags`, `uint8_t        msgFlags`, `uint16_t       msgType; // the type of payload, defined as NETMSGTYPE_x`, `uint32_t       msgUserID; // system user ID for per-user msg queues, stats etc.`, `uint64_t       msgSequence; // for retries, 0 if not present`, `uint64_t       msgSequenceDone; // a sequence number that has been fully processed, or 0`, `uint32_t length`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_Invalid`, `NETMSGTYPE_x`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageLogHelper.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageLogHelper.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageLogHelper.h` defines NetMessage infrastructure or simple payload base `NetMessageLogHelper`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: []. Message type coverage: NETMSGTYPE_Ack, NETMSGTYPE_AckNotify, NETMSGTYPE_AckNotifyResp, NETMSGTYPE_AddStoragePool, NETMSGTYPE_AddStoragePoolResp, NETMSGTYPE_AdjustChunkPermissions, NETMSGTYPE_AdjustChunkPermissionsResp, NETMSGTYPE_AuthenticateChannel, NETMSGTYPE_BumpFileVersion, NETMSGTYPE_BumpFileVersionResp, NETMSGTYPE_ChangeTargetConsistencyStates, NETMSGTYPE_ChangeTargetConsistencyStatesResp.... Serialization fields detected: handled by derived classes or switch tables. Detected classes are none; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessageTypes.h`, `string`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_Ack`, `NETMSGTYPE_AckNotify`, `NETMSGTYPE_AckNotifyResp`, `NETMSGTYPE_AddStoragePool`, `NETMSGTYPE_AddStoragePoolResp`, `NETMSGTYPE_AdjustChunkPermissions`, `NETMSGTYPE_AdjustChunkPermissionsResp`, `NETMSGTYPE_AuthenticateChannel`, ... State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageLogHelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h` defines NetMessage infrastructure or simple payload base `NetMessageTypes`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('NetMsgStrMapping', '')]. Message type coverage: NETMSGTYPE_Ack, NETMSGTYPE_AckNotify, NETMSGTYPE_AckNotifyResp, NETMSGTYPE_AddStoragePool, NETMSGTYPE_AddStoragePoolResp, NETMSGTYPE_AdjustChunkPermissions, NETMSGTYPE_AdjustChunkPermissionsResp, NETMSGTYPE_AuthenticateChannel, NETMSGTYPE_BumpFileVersion, NETMSGTYPE_BumpFileVersionResp, NETMSGTYPE_ChangeTargetConsistencyStates, NETMSGTYPE_ChangeTargetConsistencyStatesResp.... Serialization fields detected: handled by derived classes or switch tables. Detected classes are [('NetMsgStrMapping', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Protocol persistence depends on stable message IDs: `NETMSGTYPE_Ack`, `NETMSGTYPE_AckNotify`, `NETMSGTYPE_AckNotifyResp`, `NETMSGTYPE_AddStoragePool`, `NETMSGTYPE_AddStoragePoolResp`, `NETMSGTYPE_AdjustChunkPermissions`, `NETMSGTYPE_AdjustChunkPermissionsResp`, `NETMSGTYPE_AuthenticateChannel`, ... State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleInt64Msg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/SimpleInt64Msg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/SimpleInt64Msg.h` defines NetMessage infrastructure or simple payload base `SimpleInt64Msg`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('SimpleInt64Msg', 'NetMessageSerdes<SimpleInt64Msg>')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: value. Detected classes are [('SimpleInt64Msg', 'NetMessageSerdes<SimpleInt64Msg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `NetMessage.h`. Important local state or payload members include `int64_t value`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleInt64Msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleIntMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/SimpleIntMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/SimpleIntMsg.h` defines NetMessage infrastructure or simple payload base `SimpleIntMsg`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('SimpleIntMsg', 'NetMessageSerdes<SimpleIntMsg>')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: value. Detected classes are [('SimpleIntMsg', 'NetMessageSerdes<SimpleIntMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `NetMessage.h`. Important local state or payload members include `int32_t value`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleIntMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleIntStringMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/SimpleIntStringMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/SimpleIntStringMsg.h` defines NetMessage infrastructure or simple payload base `SimpleIntStringMsg`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('SimpleIntStringMsg', 'NetMessageSerdes<SimpleIntStringMsg>')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: intValue, strValue. Detected classes are [('SimpleIntStringMsg', 'NetMessageSerdes<SimpleIntStringMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `NetMessage.h`. Important local state or payload members include `int32_t intValue`, `std::string strValue`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleIntStringMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/SimpleMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/SimpleMsg.h` defines NetMessage infrastructure or simple payload base `SimpleMsg`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('SimpleMsg', 'NetMessage')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: handled by derived classes or switch tables. Detected classes are [('SimpleMsg', 'NetMessage')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `NetMessage.h`. Important local state or payload members include `return true`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleStringMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/SimpleStringMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/SimpleStringMsg.h` defines NetMessage infrastructure or simple payload base `SimpleStringMsg`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('SimpleStringMsg', 'NetMessageSerdes<SimpleStringMsg>')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: value, valueLen. Detected classes are [('SimpleStringMsg', 'NetMessageSerdes<SimpleStringMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `NetMessage.h`. Important local state or payload members include `const char* value`, `unsigned valueLen`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleStringMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleUInt16Msg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/SimpleUInt16Msg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/SimpleUInt16Msg.h` defines NetMessage infrastructure or simple payload base `SimpleUInt16Msg`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('SimpleUInt16Msg', 'NetMessageSerdes<SimpleUInt16Msg>')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: value. Detected classes are [('SimpleUInt16Msg', 'NetMessageSerdes<SimpleUInt16Msg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `NetMessage.h`. Important local state or payload members include `uint16_t value`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/SimpleUInt16Msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/AckMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/AckMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/AckMsg.h` defines or processes the `AckMsg` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [('AcknowledgeableMsg', ''), ('AckMsg', 'SimpleStringMsg')], message type(s) NETMSGTYPE_Ack, constructors, getters, and processIncoming() where present. The file depends on common/net/message/SimpleStringMsg.h. Detected classes are [('AcknowledgeableMsg', ''), ('AckMsg', 'SimpleStringMsg')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/SimpleStringMsg.h`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_Ack`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/AckMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsg.h` defines or processes the `AuthenticateChannelMsg` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [('AuthenticateChannelMsg', 'SimpleInt64Msg')], message type(s) NETMSGTYPE_AuthenticateChannel, constructors, getters, and processIncoming() where present. The file depends on common/net/message/SimpleInt64Msg.h. Detected classes are [('AuthenticateChannelMsg', 'SimpleInt64Msg')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/SimpleInt64Msg.h`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_AuthenticateChannel`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsgEx.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsgEx.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsgEx.cpp` defines or processes the `AuthenticateChannelMsgEx` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [], message type(s) no NETMSGTYPE constant found, constructors, getters, and processIncoming() where present. The file depends on common/app/config/ICommonConfig.h, common/app/log/LogContext.h, common/app/AbstractApp.h, AuthenticateChannelMsgEx.h. Detected classes are none; structs none; enums none; notable out-of-line methods ['AuthenticateChannelMsgEx::processIncoming()'].

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/config/ICommonConfig.h`, `common/app/log/LogContext.h`, `common/app/AbstractApp.h`, `AuthenticateChannelMsgEx.h`. Important local state or payload members include `return true`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsgEx.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsgEx.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsgEx.h` defines or processes the `AuthenticateChannelMsgEx` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [('AuthenticateChannelMsgEx', 'AuthenticateChannelMsg')], message type(s) no NETMSGTYPE constant found, constructors, getters, and processIncoming() where present. The file depends on common/net/message/control/AuthenticateChannelMsg.h. Detected classes are [('AuthenticateChannelMsgEx', 'AuthenticateChannelMsg')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/control/AuthenticateChannelMsg.h`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/AuthenticateChannelMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/DummyMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/DummyMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/DummyMsg.h` defines or processes the `DummyMsg` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [('DummyMsg', 'SimpleMsg')], message type(s) NETMSGTYPE_Dummy, constructors, getters, and processIncoming() where present. The file depends on common/net/message/SimpleMsg.h. Detected classes are [('DummyMsg', 'SimpleMsg')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/SimpleMsg.h`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_Dummy`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/DummyMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/GenericResponseMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/GenericResponseMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/GenericResponseMsg.h` defines or processes the `GenericResponseMsg` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [('GenericResponseMsg', 'SimpleIntStringMsg')], message type(s) NETMSGTYPE_GenericResponse, constructors, getters, and processIncoming() where present. The file depends on common/net/message/SimpleIntStringMsg.h. Detected classes are [('GenericResponseMsg', 'SimpleIntStringMsg')]; structs none; enums ['GenericRespMsgCode']; notable out-of-line methods none.

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/SimpleIntStringMsg.h`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_GenericResponse`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/GenericResponseMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsg.h` defines or processes the `PeerInfoMsg` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [('PeerInfoMsg', 'NetMessageSerdes<PeerInfoMsg>')], message type(s) NETMSGTYPE_PeerInfo, constructors, getters, and processIncoming() where present. The file depends on common/net/message/NetMessage.h, common/nodes/Node.h. Detected classes are [('PeerInfoMsg', 'NetMessageSerdes<PeerInfoMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`, `common/nodes/Node.h`. Important local state or payload members include `NodeType type`, `NumNodeID id`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_PeerInfo`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsgEx.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsgEx.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsgEx.cpp` defines or processes the `PeerInfoMsgEx` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [], message type(s) no NETMSGTYPE constant found, constructors, getters, and processIncoming() where present. The file depends on common/app/config/ICommonConfig.h, common/app/log/LogContext.h, common/app/AbstractApp.h, PeerInfoMsgEx.h. Detected classes are none; structs none; enums none; notable out-of-line methods ['PeerInfoMsgEx::processIncoming()'].

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/config/ICommonConfig.h`, `common/app/log/LogContext.h`, `common/app/AbstractApp.h`, `PeerInfoMsgEx.h`. Important local state or payload members include `return true`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsgEx.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsgEx.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsgEx.h` defines or processes the `PeerInfoMsgEx` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [('PeerInfoMsgEx', 'PeerInfoMsg')], message type(s) no NETMSGTYPE constant found, constructors, getters, and processIncoming() where present. The file depends on common/net/message/control/PeerInfoMsg.h. Detected classes are [('PeerInfoMsgEx', 'PeerInfoMsg')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/control/PeerInfoMsg.h`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/PeerInfoMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/SetChannelDirectMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/control/SetChannelDirectMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/control/SetChannelDirectMsg.h` defines or processes the `SetChannelDirectMsg` control message for connection/session control. More broadly, it defines a control-plane NetMessage used for acknowledgments, authentication, peer metadata, generic responses, or channel state.

### Important APIs, Types, And Functions
Important APIs are [('SetChannelDirectMsg', 'SimpleIntMsg')], message type(s) NETMSGTYPE_SetChannelDirect, constructors, getters, and processIncoming() where present. The file depends on common/net/message/SimpleIntMsg.h. Detected classes are [('SetChannelDirectMsg', 'SimpleIntMsg')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is either simple payload serialization through Simple* message bases or processIncoming() mutating socket state such as authentication or peer identity without a payload response.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/SimpleIntMsg.h`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_SetChannelDirect`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/control/SetChannelDirectMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/AdjustChunkPermissionsMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/AdjustChunkPermissionsMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/AdjustChunkPermissionsMsg.h` defines the `AdjustChunkPermissionsMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('AdjustChunkPermissionsMsg', 'NetMessageSerdes<AdjustChunkPermissionsMsg>')], message type(s) NETMSGTYPE_AdjustChunkPermissions, getters, constructors for outbound and deserialization use, and serialization fields: currentContDirID, currentContDirIDLen, hashDirNum, maxEntries, lastHashDirOffset, lastContDirOffset, isBuddyMirrored. Detected classes are [('AdjustChunkPermissionsMsg', 'NetMessageSerdes<AdjustChunkPermissionsMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`. Important local state or payload members include `uint32_t hashDirNum`, `const char *currentContDirID`, `uint32_t currentContDirIDLen`, `uint32_t maxEntries`, `int64_t lastHashDirOffset`, `int64_t lastContDirOffset`, `bool isBuddyMirrored`, `return currentContDirID`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_AdjustChunkPermissions`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/AdjustChunkPermissionsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/AdjustChunkPermissionsRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/AdjustChunkPermissionsRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/AdjustChunkPermissionsRespMsg.h` defines the `AdjustChunkPermissionsRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('AdjustChunkPermissionsRespMsg', 'NetMessageSerdes<AdjustChunkPermissionsRespMsg>')], message type(s) NETMSGTYPE_AdjustChunkPermissionsResp, getters, constructors for outbound and deserialization use, and serialization fields: currentContDirID, currentContDirIDLen, count, newHashDirOffset, newContDirOffset, errorCount. Detected classes are [('AdjustChunkPermissionsRespMsg', 'NetMessageSerdes<AdjustChunkPermissionsRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`. Important local state or payload members include `const char* currentContDirID`, `unsigned currentContDirIDLen`, `uint32_t count`, `int64_t newHashDirOffset`, `int64_t newContDirOffset`, `uint32_t errorCount`, `return count`, `return newHashDirOffset`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_AdjustChunkPermissionsResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/AdjustChunkPermissionsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CheckAndRepairDupInodeMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CheckAndRepairDupInodeMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CheckAndRepairDupInodeMsg.h` defines the `CheckAndRepairDupInodeMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('CheckAndRepairDupInodeMsg', 'NetMessageSerdes<CheckAndRepairDupInodeMsg>')], message type(s) NETMSGTYPE_CheckAndRepairDupInode, getters, constructors for outbound and deserialization use, and serialization fields: dupInodes, parsed. Detected classes are [('CheckAndRepairDupInodeMsg', 'NetMessageSerdes<CheckAndRepairDupInodeMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`, `common/fsck/FsckDuplicateInodeInfo.h`. Important local state or payload members include `FsckDuplicateInodeInfoVector* dupInodes`, `FsckDuplicateInodeInfoVector dupInodes`, `return *dupInodes`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_CheckAndRepairDupInode`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CheckAndRepairDupInodeMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CheckAndRepairDupInodeRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CheckAndRepairDupInodeRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CheckAndRepairDupInodeRespMsg.h` defines the `CheckAndRepairDupInodeRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('CheckAndRepairDupInodeRespMsg', 'NetMessageSerdes<CheckAndRepairDupInodeRespMsg>')], message type(s) NETMSGTYPE_CheckAndRepairDupInodeResp, getters, constructors for outbound and deserialization use, and serialization fields: failedEntryIDList. Detected classes are [('CheckAndRepairDupInodeRespMsg', 'NetMessageSerdes<CheckAndRepairDupInodeRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`, `common/storage/StorageDefinitions.h`, `common/toolkit/ListTk.h`. Important local state or payload members include `StringList failedEntryIDList`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_CheckAndRepairDupInodeResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CheckAndRepairDupInodeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateDefDirInodesMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateDefDirInodesMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateDefDirInodesMsg.h` defines the `CreateDefDirInodesMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('CreateDefDirInodesMsg', 'NetMessageSerdes<CreateDefDirInodesMsg>')], message type(s) NETMSGTYPE_CreateDefDirInodes, getters, constructors for outbound and deserialization use, and serialization fields: items. Detected classes are [('CreateDefDirInodesMsg', 'NetMessageSerdes<CreateDefDirInodesMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`. Important local state or payload members include `std::vector<Item> items`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_CreateDefDirInodes`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateDefDirInodesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateDefDirInodesRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateDefDirInodesRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateDefDirInodesRespMsg.h` defines the `CreateDefDirInodesRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('CreateDefDirInodesRespMsg', 'NetMessageSerdes<CreateDefDirInodesRespMsg>')], message type(s) NETMSGTYPE_CreateDefDirInodesResp, getters, constructors for outbound and deserialization use, and serialization fields: failedInodeIDs, parsed, createdInodes. Detected classes are [('CreateDefDirInodesRespMsg', 'NetMessageSerdes<CreateDefDirInodesRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `StringList* failedInodeIDs`, `FsckDirInodeList* createdInodes`, `StringList failedInodeIDs`, `FsckDirInodeList createdInodes`, `return *failedInodeIDs`, `return *createdInodes`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_CreateDefDirInodesResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateDefDirInodesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateEmptyContDirsMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateEmptyContDirsMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateEmptyContDirsMsg.h` defines the `CreateEmptyContDirsMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('CreateEmptyContDirsMsg', 'NetMessageSerdes<CreateEmptyContDirsMsg>')], message type(s) NETMSGTYPE_CreateEmptyContDirs, getters, constructors for outbound and deserialization use, and serialization fields: items. Detected classes are [('CreateEmptyContDirsMsg', 'NetMessageSerdes<CreateEmptyContDirsMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`. Important local state or payload members include `std::vector<Item> items`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_CreateEmptyContDirs`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateEmptyContDirsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateEmptyContDirsRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateEmptyContDirsRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateEmptyContDirsRespMsg.h` defines the `CreateEmptyContDirsRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('CreateEmptyContDirsRespMsg', 'NetMessageSerdes<CreateEmptyContDirsRespMsg>')], message type(s) NETMSGTYPE_CreateEmptyContDirsResp, getters, constructors for outbound and deserialization use, and serialization fields: failedDirIDs, parsed. Detected classes are [('CreateEmptyContDirsRespMsg', 'NetMessageSerdes<CreateEmptyContDirsRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`. Important local state or payload members include `StringList* failedDirIDs`, `StringList failedDirIDs`, `return *failedDirIDs`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_CreateEmptyContDirsResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/CreateEmptyContDirsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteChunksMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteChunksMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteChunksMsg.h` defines the `DeleteChunksMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('DeleteChunksMsg', 'NetMessageSerdes<DeleteChunksMsg>')], message type(s) NETMSGTYPE_DeleteChunks, getters, constructors for outbound and deserialization use, and serialization fields: chunks, parsed. Detected classes are [('DeleteChunksMsg', 'NetMessageSerdes<DeleteChunksMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckChunk.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckChunkList* chunks`, `FsckChunkList chunks`, `return *chunks`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_DeleteChunks`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteChunksMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteChunksRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteChunksRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteChunksRespMsg.h` defines the `DeleteChunksRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('DeleteChunksRespMsg', 'NetMessageSerdes<DeleteChunksRespMsg>')], message type(s) NETMSGTYPE_DeleteChunksResp, getters, constructors for outbound and deserialization use, and serialization fields: failedChunks, parsed. Detected classes are [('DeleteChunksRespMsg', 'NetMessageSerdes<DeleteChunksRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckChunk.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckChunkList* failedChunks`, `FsckChunkList failedChunks`, `return *failedChunks`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_DeleteChunksResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteChunksRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteDirEntriesMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteDirEntriesMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteDirEntriesMsg.h` defines the `DeleteDirEntriesMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('DeleteDirEntriesMsg', 'NetMessageSerdes<DeleteDirEntriesMsg>')], message type(s) NETMSGTYPE_DeleteDirEntries, getters, constructors for outbound and deserialization use, and serialization fields: entries, parsed. Detected classes are [('DeleteDirEntriesMsg', 'NetMessageSerdes<DeleteDirEntriesMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirEntry.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckDirEntryList* entries`, `FsckDirEntryList entries`, `return *entries`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_DeleteDirEntries`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteDirEntriesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteDirEntriesRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteDirEntriesRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteDirEntriesRespMsg.h` defines the `DeleteDirEntriesRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('DeleteDirEntriesRespMsg', 'NetMessageSerdes<DeleteDirEntriesRespMsg>')], message type(s) NETMSGTYPE_DeleteDirEntriesResp, getters, constructors for outbound and deserialization use, and serialization fields: failedEntries, parsed. Detected classes are [('DeleteDirEntriesRespMsg', 'NetMessageSerdes<DeleteDirEntriesRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirEntry.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckDirEntryList* failedEntries`, `FsckDirEntryList failedEntries`, `return *failedEntries`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_DeleteDirEntriesResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/DeleteDirEntriesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FetchFsckChunkListMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FetchFsckChunkListMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FetchFsckChunkListMsg.h` defines the `FetchFsckChunkListMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FetchFsckChunkListMsg', 'NetMessageSerdes<FetchFsckChunkListMsg>')], message type(s) NETMSGTYPE_FetchFsckChunkList, getters, constructors for outbound and deserialization use, and serialization fields: maxNumChunks, lastStatus, forceRestart. Detected classes are [('FetchFsckChunkListMsg', 'NetMessageSerdes<FetchFsckChunkListMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`, `common/toolkit/FsckTk.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `uint32_t maxNumChunks`, `FetchFsckChunkListStatus lastStatus`, `bool forceRestart`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FetchFsckChunkList`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FetchFsckChunkListMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FetchFsckChunkListRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FetchFsckChunkListRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FetchFsckChunkListRespMsg.h` defines the `FetchFsckChunkListRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FetchFsckChunkListRespMsg', 'NetMessageSerdes<FetchFsckChunkListRespMsg>')], message type(s) NETMSGTYPE_FetchFsckChunkListResp, getters, constructors for outbound and deserialization use, and serialization fields: chunkList, parsed, status. Detected classes are [('FetchFsckChunkListRespMsg', 'NetMessageSerdes<FetchFsckChunkListRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckChunk.h`, `common/net/message/NetMessage.h`, `common/toolkit/FsckTk.h`, `common/toolkit/ListTk.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `FsckChunkList* chunkList`, `FetchFsckChunkListStatus status`, `FsckChunkList chunkList`, `return *chunkList`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FetchFsckChunkListResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FetchFsckChunkListRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h` defines the `FixInodeOwnersInDentryMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FixInodeOwnersInDentryMsg', 'NetMessageSerdes<FixInodeOwnersInDentryMsg>')], message type(s) NETMSGTYPE_FixInodeOwnersInDentry, getters, constructors for outbound and deserialization use, and serialization fields: dentries, parsed, owners. Detected classes are [('FixInodeOwnersInDentryMsg', 'NetMessageSerdes<FixInodeOwnersInDentryMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirEntry.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckDirEntryList* dentries`, `NumNodeIDList* owners`, `FsckDirEntryList dentries`, `NumNodeIDList owners`, `return *dentries`, `return *owners`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FixInodeOwnersInDentry`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryRespMsg.h` defines the `FixInodeOwnersInDentryRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FixInodeOwnersInDentryRespMsg', 'NetMessageSerdes<FixInodeOwnersInDentryRespMsg>')], message type(s) NETMSGTYPE_FixInodeOwnersInDentryResp, getters, constructors for outbound and deserialization use, and serialization fields: failedEntries, parsed. Detected classes are [('FixInodeOwnersInDentryRespMsg', 'NetMessageSerdes<FixInodeOwnersInDentryRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirEntry.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckDirEntryList* failedEntries`, `FsckDirEntryList failedEntries`, `return *failedEntries`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FixInodeOwnersInDentryResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersInDentryRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersMsg.h` defines the `FixInodeOwnersMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FixInodeOwnersMsg', 'NetMessageSerdes<FixInodeOwnersMsg>')], message type(s) NETMSGTYPE_FixInodeOwners, getters, constructors for outbound and deserialization use, and serialization fields: inodes, parsed. Detected classes are [('FixInodeOwnersMsg', 'NetMessageSerdes<FixInodeOwnersMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckDirInodeList* inodes`, `FsckDirInodeList inodes`, `return *inodes`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FixInodeOwners`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersRespMsg.h` defines the `FixInodeOwnersRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FixInodeOwnersRespMsg', 'NetMessageSerdes<FixInodeOwnersRespMsg>')], message type(s) NETMSGTYPE_FixInodeOwnersResp, getters, constructors for outbound and deserialization use, and serialization fields: failedInodes, parsed. Detected classes are [('FixInodeOwnersRespMsg', 'NetMessageSerdes<FixInodeOwnersRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckDirInodeList* failedInodes`, `FsckDirInodeList failedInodes`, `return *failedInodes`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FixInodeOwnersResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FixInodeOwnersRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckModificationEventMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckModificationEventMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckModificationEventMsg.h` defines the `FsckModificationEventMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FsckModificationEventMsg', 'AcknowledgeableMsgSerdes<FsckModificationEventMsg>')], message type(s) NETMSGTYPE_FsckModificationEvent, getters, constructors for outbound and deserialization use, and serialization fields: modificationEventTypeList, parsed, entryIDList, eventsMissed, serializeAckID. Detected classes are [('FsckModificationEventMsg', 'AcknowledgeableMsgSerdes<FsckModificationEventMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/AcknowledgeableMsg.h`, `common/toolkit/serialization/Serialization.h`, `common/toolkit/ListTk.h`. Important local state or payload members include `UInt8List* modificationEventTypeList`, `StringList* entryIDList`, `bool eventsMissed`, `UInt8List eventTypes`, `StringList entryIDList`, `return *modificationEventTypeList`, `return *entryIDList`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FsckModificationEvent`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckModificationEventMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckSetEventLoggingMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckSetEventLoggingMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckSetEventLoggingMsg.h` defines the `FsckSetEventLoggingMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FsckSetEventLoggingMsg', 'NetMessageSerdes<FsckSetEventLoggingMsg>')], message type(s) NETMSGTYPE_FsckSetEventLogging, getters, constructors for outbound and deserialization use, and serialization fields: enableLogging, portUDP, nicList, parsed, forceRestart. Detected classes are [('FsckSetEventLoggingMsg', 'NetMessageSerdes<FsckSetEventLoggingMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`, `common/toolkit/ListTk.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `bool enableLogging`, `uint32_t portUDP`, `NicAddressList* nicList`, `bool forceRestart`, `NicAddressList nicList`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FsckSetEventLogging`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckSetEventLoggingMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckSetEventLoggingRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckSetEventLoggingRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckSetEventLoggingRespMsg.h` defines the `FsckSetEventLoggingRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('FsckSetEventLoggingRespMsg', 'NetMessageSerdes<FsckSetEventLoggingRespMsg>')], message type(s) NETMSGTYPE_FsckSetEventLoggingResp, getters, constructors for outbound and deserialization use, and serialization fields: result, loggingEnabled, missedEvents. Detected classes are [('FsckSetEventLoggingRespMsg', 'NetMessageSerdes<FsckSetEventLoggingRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`, `common/toolkit/ListTk.h`, `common/toolkit/serialization/Serialization.h`. Important local state or payload members include `bool result`, `bool loggingEnabled`, `bool missedEvents`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_FsckSetEventLoggingResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/FsckSetEventLoggingRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h` defines the `LinkToLostAndFoundMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('LinkToLostAndFoundMsg', 'NetMessageSerdes<LinkToLostAndFoundMsg>')], message type(s) NETMSGTYPE_LinkToLostAndFound, getters, constructors for outbound and deserialization use, and serialization fields: entryType, lostAndFoundInfoPtr, lostAndFoundInfo, dirInodes, parsed, fileInodes. Detected classes are [('LinkToLostAndFoundMsg', 'NetMessageSerdes<LinkToLostAndFoundMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`, `common/toolkit/FsckTk.h`. Important local state or payload members include `FsckDirEntryType entryType; // to indicate, whether dir inodes or file inodes should be`, `FsckDirInodeList* dirInodes; // not owned by this object`, `FsckFileInodeList* fileInodes; // not owned by this object`, `EntryInfo* lostAndFoundInfoPtr; // not owned by this object`, `EntryInfo lostAndFoundInfo`, `FsckDirInodeList dirInodes`, `FsckFileInodeList fileInodes`, `return *dirInodes`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_LinkToLostAndFound`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundRespMsg.h` defines the `LinkToLostAndFoundRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('LinkToLostAndFoundRespMsg', 'NetMessageSerdes<LinkToLostAndFoundRespMsg>')], message type(s) NETMSGTYPE_LinkToLostAndFoundResp, getters, constructors for outbound and deserialization use, and serialization fields: entryType, failedDirInodes, parsed, failedFileInodes, createdDentries. Detected classes are [('LinkToLostAndFoundRespMsg', 'NetMessageSerdes<LinkToLostAndFoundRespMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`, `common/toolkit/FsckTk.h`. Important local state or payload members include `FsckDirEntryType entryType; // to indicate, whether dir inodes or file inodes should be`, `FsckDirInodeList* failedDirInodes`, `FsckFileInodeList* failedFileInodes`, `FsckDirEntryList* createdDentries`, `FsckDirInodeList failedDirInodes`, `FsckFileInodeList failedFileInodes`, `FsckDirEntryList createdDentries`, `return *failedDirInodes`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_LinkToLostAndFoundResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/LinkToLostAndFoundRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/MoveChunkFileMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/MoveChunkFileMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/MoveChunkFileMsg.h` defines the `MoveChunkFileMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('MoveChunkFileMsg', 'NetMessageSerdes<MoveChunkFileMsg>')], message type(s) NETMSGTYPE_MoveChunkFile, getters, constructors for outbound and deserialization use, and serialization fields: chunkName, oldPath, newPath, targetID, isMirrored, overwriteExisting. Detected classes are [('MoveChunkFileMsg', 'NetMessageSerdes<MoveChunkFileMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`. Important local state or payload members include `std::string chunkName`, `std::string oldPath`, `std::string newPath`, `uint16_t targetID`, `bool isMirrored`, `bool overwriteExisting`, `return chunkName`, `return targetID`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_MoveChunkFile`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/MoveChunkFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/MoveChunkFileRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/MoveChunkFileRespMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/MoveChunkFileRespMsg.h` defines the `MoveChunkFileRespMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('MoveChunkFileRespMsg', 'SimpleIntMsg')], message type(s) NETMSGTYPE_MoveChunkFileResp, getters, constructors for outbound and deserialization use, and serialization fields: payload fields are declared in the class body. Detected classes are [('MoveChunkFileRespMsg', 'SimpleIntMsg')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/SimpleIntMsg.h`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_MoveChunkFileResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/MoveChunkFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateDentriesMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateDentriesMsg.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateDentriesMsg.h` defines the `RecreateDentriesMsg` fsck network message used by consistency checking and repair workflows. More broadly, it defines an fsck value type used to transport, compare, or repair filesystem consistency records.

### Important APIs, Types, And Functions
Important API surface includes class declarations [('RecreateDentriesMsg', 'NetMessageSerdes<RecreateDentriesMsg>')], message type(s) NETMSGTYPE_RecreateDentries, getters, constructors for outbound and deserialization use, and serialization fields: fsIDs, parsed. Detected classes are [('RecreateDentriesMsg', 'NetMessageSerdes<RecreateDentriesMsg>')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is mostly constructor setup plus CRTP NetMessageSerdes serialization/deserialization. Outbound messages usually borrow caller-owned lists or strings; inbound messages use parsed backing storage where serdes::backedPtr is present.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/fsck/FsckFsID.h`, `common/net/message/NetMessage.h`. Important local state or payload members include `FsckFsIDList* fsIDs`, `FsckFsIDList fsIDs`, `return *fsIDs`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_RecreateDentries`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, comparison operators and list serialization for mirrored and non-mirrored records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RecreateDentriesMsg.h -->
