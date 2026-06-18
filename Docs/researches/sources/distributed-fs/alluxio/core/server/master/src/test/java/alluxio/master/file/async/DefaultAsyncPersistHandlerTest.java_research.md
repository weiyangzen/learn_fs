# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/async/DefaultAsyncPersistHandlerTest.java

## Purpose
Unit tests for worker-side assignment behavior in `DefaultAsyncPersistHandler`. It validates that files are scheduled for persistence only when their blocks are all on one worker and that deleted files are skipped when workers poll.

## Important APIs/types/functions
- Mocks `FileSystemMaster` and wraps it in `FileSystemMasterView`.
- Uses `DefaultAsyncPersistHandler.scheduleAsyncPersistence` and `pollFilesToPersist(workerId)`.
- Builds `FileBlockInfo`, `BlockInfo`, `BlockLocation`, `FileInfo`, and expects `PersistFile` block IDs.

## Control flow
- `scheduleAsyncPersist` sets one block on one worker, schedules the path, polls that worker, and expects one `PersistFile` with the block id.
- `persistenceFileWithBlocksOnMultipleWorkers` creates two blocks on different workers and verifies neither worker receives a persist assignment.
- `persistenceFileAfterDeletion` schedules a file, then makes `getFileInfo(fileId)` throw `FileDoesNotExistException`; poll returns no work.

## State and persistence behavior
- Handler stores scheduled file ids internally until polled; the test verifies it consults current master view at poll time.
- No real UFS persistence is performed; output is a `PersistFile` work description.

## Dependencies and integration points
- Integrates async persist handler with FileSystemMaster block metadata and path/id lookup APIs.
- Depends on completed, non-empty `FileInfo` as persistence eligibility signal.

## Risks and edge cases
- Tests do not cover incomplete files, zero-length files, repeated polling, or multiple eligible files.
- Multi-worker behavior assumes a file with blocks split across workers should not be assigned, which is a key scheduling invariant.

## Test signals
- Good signal for avoiding impossible worker assignments and for pruning deleted scheduled files.
