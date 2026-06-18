# sources/distributed-fs/beegfs/common/source/common/components/worker/Worker.cpp

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
