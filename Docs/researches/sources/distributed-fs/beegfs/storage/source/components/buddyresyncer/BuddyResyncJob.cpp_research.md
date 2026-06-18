## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncJob.cpp

Purpose: Implements a storage-target buddy resync job. It coordinates gather slaves, file sync slaves, directory sync slaves, target-state transitions, and final buddy notification.

Important APIs/types/functions: Constructor sizes slave vectors from config. `run()` is the main orchestration. `abort()` signals abort and disables idle-only termination. `startGatherSlaves()`, `startSyncSlaves()`, `joinGatherSlaves()`, `joinSyncSlaves()` manage worker threads. `getJobStats()` aggregates counters. `informBuddy()` sends final consistency state to the buddy. `checkTopLevelDir()` and `walkDirs()` discover sync candidates by mtime.

Control flow: `run()` guards against double running, marks target resync in progress, flushes all storage workers through `IncSyncedCounterWork`, notifies buddy with `StorageResyncStartedMsg`, starts slaves, computes last-buddy-comm threshold, scans top-level and shallow chunk dirs, queues deeper dirs to gather slaves, drains gather and sync slaves, evaluates abort/errors/offline flags, sets final job status, updates target last-buddy-comm/buddy-needs-resync state, informs buddy, clears resync-in-progress, and records end time.

State and persistence: Owns status, start/end times, sync candidate store, gather queue, slave pointers, discovered/matched counters, abort flag, and target-offline flag. It reads persistent target path/chunk mtime and target last-buddy-comm state; it may clear last-buddy-comm override and set buddy-needs-resync through `StorageTarget`.

Dependencies and integration: Depends on `App`, `StorageTargets`, `MirrorBuddyGroupMapper`, `TargetMapper`, `NodeStoreServers`, storage workers, resync slave classes, `MessagingTk`, `StorageResyncStartedMsg`, and target consistency messages.

Risks and test signals: `run()` dereferences `buddyNode` for `MessagingTk::requestResponse(*buddyNode, ...)` without a null check after `referenceNode()`. Failure cleanup waits on slave `isRunning` even if some start paths failed. Directory scan is mtime-based and applies a safety threshold; clock/filesystem timestamp issues can affect completeness. Tests should cover unknown buddy node, failed buddy notification, slave start failure, abort during walk, target offline during finalization, mtime threshold correctness, and status/stat aggregation.
