# sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.cpp

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
