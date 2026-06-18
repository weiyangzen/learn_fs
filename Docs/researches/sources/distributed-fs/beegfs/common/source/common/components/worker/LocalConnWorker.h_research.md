# sources/distributed-fs/beegfs/common/source/common/components/worker/LocalConnWorker.h

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
