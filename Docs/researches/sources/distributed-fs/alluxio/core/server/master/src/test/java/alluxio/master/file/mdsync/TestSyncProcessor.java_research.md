# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/TestSyncProcessor.java

## Purpose
Test subclass of `DefaultSyncProcess` that adds hooks around `performSyncOne` for concurrency and mutation-race tests. It can invoke callbacks before each inode sync and block/release when the nth sync operation is reached.

## Important APIs/types/functions
- Extends `DefaultSyncProcess`.
- Functional interfaces: `Callback` and `SyncOneCallback`.
- Overrides protected `performSyncOne(SyncProcessState, UfsItem, InodeIterationResult)`.
- Public hook methods: `beforePerformSyncOne` and `blockUntilNthSyncThenDo`.
- Uses a `Semaphore` to coordinate the blocking callback.

## Control flow
- On every `performSyncOne`, optional pre-sync callback receives the `SyncProcessContext`.
- Sync count increments; when it reaches configured `mBlockOnNth`, the callback runs and the semaphore is released.
- After hook logic, delegates to `super.performSyncOne`.
- `blockUntilNthSyncThenDo` sets the target count/callback and waits until the sync thread reaches that point.

## State and persistence behavior
- Adds mutable hook state (`mBlockOnNth`, `mSyncCount`, callbacks, semaphore) around real DefaultSyncProcess behavior.
- Persistence and inode mutations are still performed by the superclass when used with real master/inode dependencies.

## Dependencies and integration points
- Constructor mirrors DefaultSyncProcess dependencies: file master, inode store, mount table, inode tree, sync path cache, and absent path cache.
- Intended for tests that need precise synchronization with individual inode sync operations.

## Risks and edge cases
- Callback exceptions are converted to generic `RuntimeException`, losing original detail.
- `blockUntilNthSyncThenDo` acquires the semaphore after setting callbacks; if nth sync already passed, it can block forever.
- State is not reset between uses except by replacing callbacks/target.

## Test signals
- Useful scaffold for race-condition tests involving metadata sync and concurrent namespace changes.
