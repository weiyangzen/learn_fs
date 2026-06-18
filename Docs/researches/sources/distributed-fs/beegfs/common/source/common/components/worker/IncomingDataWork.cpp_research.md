# sources/distributed-fs/beegfs/common/source/common/components/worker/IncomingDataWork.cpp

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
