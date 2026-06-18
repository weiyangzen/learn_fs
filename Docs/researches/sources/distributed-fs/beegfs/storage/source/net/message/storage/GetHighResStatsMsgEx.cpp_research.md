## sources/distributed-fs/beegfs/storage/source/net/message/storage/GetHighResStatsMsgEx.cpp

### Purpose
`GetHighResStatsMsgEx.cpp` serves high-resolution storage statistics history since a caller-provided timestamp.

### Important APIs, Types, And Functions
`processIncoming()` reads `lastStatsMS` from `getValue()`, calls `StatsCollector::getStatsSince(lastStatsMS, statsHistory)`, and sends `GetHighResStatsRespMsg`.

### Control Flow, State, And Persistence
The handler is read-only. It snapshots stats history from the collector into a response list.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StatsCollector` and common high-res stats response messages. Risks include large responses if the timestamp is old and concurrent stats rotation. Tests should cover empty, partial, and full history windows plus serialization.
