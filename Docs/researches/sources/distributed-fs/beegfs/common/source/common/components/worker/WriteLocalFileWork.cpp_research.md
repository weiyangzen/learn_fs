# sources/distributed-fs/beegfs/common/source/common/components/worker/WriteLocalFileWork.cpp

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
