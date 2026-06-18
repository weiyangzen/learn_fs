# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/UfsLoadsTest.java

## Purpose
Early or skeletal tests for UFS load behavior in Metadata Sync V2. The current file sets up a full TaskTracker/MetadataSyncHandler test scaffold and contains a minimal `singleFileSync` test that only configures get-status state.

## Important APIs/types/functions
- Uses `TaskTracker`, `MetadataSyncHandler`, `MockUfsClient`, `DummySyncProcess`, `UfsSyncPathCache`, and `UfsAbsentPathCache`.
- Spies on `SyncProcess.performSync` to collect processed UFS items into `mProcessedItems`.
- `getClient` wraps `mUfsClient` in a `CloseableResource`.

## Control flow
- `before()` creates a cached thread pool, spy mock UFS client and sync process, mocks caches, constructs `TaskTracker`, and creates handler.
- The sync process spy peeks each load result's item stream to collect processed items before calling the real dummy process.
- `after()` asserts no running tasks, closes task tracker, and shuts down executor.
- `singleFileSync` currently only calls `mUfsClient.setGetStatusItem(mFileStatus)` and performs no sync assertion.

## State and persistence behavior
- Maintains in-memory processed item list; no real metadata or UFS persistence.
- Teardown still validates TaskTracker is idle.

## Dependencies and integration points
- Same mdsync scaffolding as TaskTracker tests, but underused in current test body.

## Risks and edge cases
- The single test has no assertion and does not trigger a task, so it provides almost no regression signal.
- The setup is heavier than the test behavior and may mask intended future work.

## Test signals
- Current signal is limited to fixture construction/teardown. It should be expanded or removed if no behavior is intended.
