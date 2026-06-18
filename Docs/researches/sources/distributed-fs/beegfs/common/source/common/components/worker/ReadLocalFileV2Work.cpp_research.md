# sources/distributed-fs/beegfs/common/source/common/components/worker/ReadLocalFileV2Work.cpp

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
