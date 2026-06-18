# sources/distributed-fs/beegfs/common/source/common/components/worker/queue/UserWorkContainer.h

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
