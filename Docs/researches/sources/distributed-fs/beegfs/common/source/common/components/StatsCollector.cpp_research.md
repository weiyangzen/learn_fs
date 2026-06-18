<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.cpp

### Purpose
`StatsCollector.cpp` implements periodic collection of high-resolution work-queue statistics and bounded in-memory history retrieval.

### Important APIs, Types, And Functions
Implemented methods are constructor, destructor, `run`, `collectLoop`, virtual `collectStats`, and `getStatsSince`.

### Control Flow
The thread registers signal handling, loops until self-termination with `waitForSelfTerminateOrder(collectIntervalMS)`, and calls `collectStats`. Default collection locks the stats list, calls `workQ->getAndResetStats`, stamps current time in milliseconds, trims history to configured length, and pushes newest stats to the front. Retrieval copies entries newer than `lastStatsMS` to the output list in iteration order.

### State, Persistence, And Dependencies
State is mutex-protected `HighResStatsList`, `MultiWorkQueue*`, interval, and history length. No durable persistence. Dependencies include `TimeAbs`, `PThread`, `AbstractApp`, `LogContext`, and work queue stats types.

### Integration Points
Service components expose recent operation stats through this collector. Derived classes can override `collectStats` for non-work-queue stats sources.

### Risks
The default `collectStats` assumes `workQ` is non-null. `getStatsSince` pushes newest-to-oldest into `outStatsList` despite the comment saying newer stats are pushed to the back; callers should verify ordering expectations.

### Test Signals
Tests should cover interval collection, bounded history, timestamp filtering, work queue reset semantics, null `workQ` behavior in derived classes, and output ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.cpp -->
