## sources/distributed-fs/beegfs/storage/source/components/StorageStatsCollector.cpp

Purpose: Collects high-resolution storage worker stats across multiple per-target work queues.

Important APIs/types/functions: Overrides `collectStats()` to iterate `App::getWorkQueueMap()`, call `getAndResetStats()` on each queue, merge raw and incremental stats via `HighResolutionStatsTk`, stamp the current time, and maintain bounded history.

Control flow: It uses the first work queue as the base stats object, then merges remaining queues. The inherited `mutex` protects `statsList`.

State and persistence: Keeps in-memory stats history only; no persistence.

Dependencies and integration: Depends on `Program::getApp()`, `MultiWorkQueueMap`, `HighResolutionStatsTk`, `TimeAbs`, and common `StatsCollector`. Used by `App` as the storage stats component.

Risks and test signals: Assumes `workQueueMap` is non-empty. Tests should cover single global queue, multiple per-target queues, reset semantics, and history length trimming.
