# sources/distributed-fs/beegfs/common/source/common/components/worker/queue/MultiWorkQueue.cpp

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
