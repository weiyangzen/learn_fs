# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/BuddyResyncJob.cpp

## Purpose
Implements the metadata buddy resync job thread. It coordinates a full resync of the local metadata mirror subtree to the buddy metadata node, captures concurrent mirrored mutations, resyncs mirrored sessions, and finally publishes the buddy consistency result.

## Important APIs And Types
Key APIs are the constructor, run(), abort(), startGatherSlaves(), startSyncSlaves(), stopAllWorkersOn(), getJobStats(), newBuddyState(), informBuddy(), and informMgmtd(). The constructor resolves the buddy node, sizes bulk sync slaves from tuneNumResyncSlaves, and creates gather, bulk, modification, and session-store resync helpers. threadCount tracks mirrored request handlers that have registered in-flight changesets.

## Control Flow
run() clears candidates, resolves the buddy, optionally triggers debug termination, blocks all workers with BarrierWork, sends StorageResyncStartedMsg, transitions to RUNNING, marks InternodeSyncer resync-in-progress, starts gather and sync slaves, releases the initial worker barrier, joins the gatherer, lets bulk syncers drain, conditionally blocks workers again for session quiescence, drains the modification sync slave, performs session-store sync, collects errors, clears the needs-resync marker, informs buddy and management of GOOD or BAD, restarts workers, and on errors drains pending modification candidates so waiting workers can complete. abort() marks INTERRUPTED, terminates slaves, and optionally waits for registered worker operations while signaling queued changesets.

## State And Persistence
State lives in BuddyResyncJobState guarded by stateMutex plus start/end timestamps, sync candidate queues, per-slave atomic counters, session sync counters, and the meta-path needs-resync marker. The job persists no new object itself, but it drives remote raw-inode/session replacement and target consistency state changes on the buddy and management services.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
The barrier choreography is deadlock-sensitive: workers must be stopped only where no mod-sync queue waiters can block forever. abort(true) depends on threadCount and queue signaling to unblock mirrored operations. A communication failure before StorageResyncStarted or during final state updates can leave the buddy needing another resync. Statistics aggregation assumes slave counters are stable after isRunning clears.

## Test Signals
Exercise successful resync, missing buddy node, StorageResyncStarted failure, bulk sync failure, mod sync failure, abort(false/true), worker barrier release, session sync failure, and final GOOD/BAD propagation. Debug variables BEEGFS_RESYNC_DIE_AT_N and BEEGFS_DEBUG_FAIL_MODSYNC are useful fault-injection signals.
