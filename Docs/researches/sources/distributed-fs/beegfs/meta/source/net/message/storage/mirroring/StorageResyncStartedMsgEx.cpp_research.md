<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp

## Purpose
Handles notification that storage/metadata resync is starting for the local metadata node, quiescing workers and invalidating mirrored metadata caches before resync changes files on disk.

## Important APIs, Types, and Functions
`processIncoming()` validates that the message target ID matches the local node, calls `pauseWorkers()`, marks the root directory as buddy mirrored, clears mirrored sessions, invalidates mirrored directory inodes in `MetaStore`, sends `StorageResyncStartedRespMsg`, and returns true. `pauseWorkers()` enqueues `BarrierWork` on all other worker personal queues and waits twice on a `Barrier` so pre-existing messages drain before resync.

## Control Flow, State, and Persistence
The handler mutates in-memory state only: root mirror flag, mirrored session store, and cached directory inodes. It relies on target state (`NeedsResync`) plus worker barrier synchronization to ensure no mirrored operations are in flight while resync overwrites mirrored metadata.

## Dependencies and Integration Points
Depends on worker lists, `MultiWorkQueue`, `Barrier`, `PThread`, `BarrierWork`, mirrored sessions, `MetaStore::invalidateMirroredDirInodes()`, and the resync-started response message.

## Risks and Test Signals
Risks include deadlock if the current worker is accidentally enqueued, incorrect barrier count, target-ID mismatch returning false without response, and clearing sessions while operations still reference files. Tests should cover multi-worker barrier behavior, single-worker behavior, wrong target ID, cache invalidation, and session clearing before raw resync begins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp -->
