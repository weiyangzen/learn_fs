# sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.h

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
