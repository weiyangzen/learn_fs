# sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.cpp

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
