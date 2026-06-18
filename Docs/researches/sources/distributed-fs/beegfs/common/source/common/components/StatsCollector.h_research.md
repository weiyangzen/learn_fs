<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.h -->
## sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.h

### Purpose
This header declares the statistics collector thread and its default history sizing constants.

### Important APIs, Types, And Functions
It defines `STATSCOLLECTOR_COLLECT_INTERVAL_MS`, `STATSCOLLECTOR_HISTORY_LENGTH`, class `StatsCollector`, constructor/destructor, `getStatsSince`, virtual `collectStats`, private `run` and `collectLoop`, and protected state for logging, mutex, stats list, work queue, interval, and history length.

### Control Flow
The class is a `PThread`; execution is internal, with extension through `collectStats` override.

### State, Persistence, And Dependencies
State is in-memory stats history and collection configuration. Dependencies include logging, app/threading, work queue, component exception, net message stats types, and `Common`.

### Integration Points
Common services can embed or subclass this collector to report recent high-resolution operational statistics.

### Risks
Thread-safety depends on all history access taking the mutex. Subclasses overriding `collectStats` need to preserve locking and history bounds if they use shared `statsList`.

### Test Signals
Compile tests for subclass overrides and runtime tests for locking/history behavior under concurrent collection and reads are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.h -->
