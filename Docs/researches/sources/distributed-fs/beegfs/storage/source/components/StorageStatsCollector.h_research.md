## sources/distributed-fs/beegfs/storage/source/components/StorageStatsCollector.h

Purpose: Declares the storage-specific stats collector.

Important APIs/types/functions: `StorageStatsCollector(unsigned collectIntervalMS, unsigned historyLength)` invokes the base `StatsCollector` with no single queue, and overrides `collectStats()`.

Control flow: Header contains only construction and override declaration.

State and persistence: Uses base collector state for interval and history.

Dependencies and integration: Inherits `StatsCollector`; `App` creates it with storage collector constants.

Risks and test signals: Behavior depends on cpp implementation. Constructor intentionally passes `NULL` because storage has multiple queues.
