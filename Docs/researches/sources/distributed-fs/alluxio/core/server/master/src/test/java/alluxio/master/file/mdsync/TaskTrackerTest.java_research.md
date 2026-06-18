# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/TaskTrackerTest.java

## Purpose
Comprehensive concurrency and error-handling tests for `TaskTracker`, the orchestrator for Metadata Sync V2 UFS load requests and sync processing. It validates rate limiting, concurrent loading/processing, directory nested loads, retries, failure propagation, stats accounting, and duplicate in-flight task blocking.

## Important APIs/types/functions
- Creates `TaskTracker(concurrentProcessing, concurrentUfsLoads, ..., UfsSyncPathCache, UfsAbsentPathCache, SyncProcess, clientSupplier)`.
- Uses `MetadataSyncHandler.checkTask` flow via `mTaskTracker.checkTask`.
- `MockUfsClient` supplies listings, errors, and rate limiter.
- `DummySyncProcess` simulates sync result processing and nested directory scheduling.
- `checkStats` validates `TaskStats`: batches, statuses, load errors, load requests, load/process failure flags, and first-load-was-file.

## Control flow
- Setup creates one-thread defaults, mocked sync/absent caches, mocked file master journal context, and a metadata sync handler.
- Rate limit test uses a fake ticker and semaphore to prove each load acquires permits.
- Concurrent tests configure multiple UFS load and processing lanes, block processing with latches/semaphores, and wait until the expected number of loads/processes are active.
- Error tests inject IO/runtime failures in processing or listing under single-listing and directory-load modes, then assert `waitComplete` throws and stats mark load/process failures.
- Directory load test returns both file and directory statuses and verifies nested `/dir` load happens only when `UfsSyncPathCache.shouldSyncPath` permits it.
- Basic/multi-batch/retry tests validate successful stats under scripted single and multiple truncated batches.
- Blocking sync test submits two same-path tasks while processing is blocked and expects one execution to satisfy both callers.

## State and persistence behavior
- State under test is TaskTracker's running task registry, executor queues, retry counters, and stats.
- No real Alluxio metadata persistence; `NoopJournalContext` is used and `DummySyncProcess` avoids inode writes.
- Teardown asserts no running tasks remain before closing the tracker.

## Dependencies and integration points
- Integrates task tracking with rate limiter, UFS client callbacks, sync path cache, absent path cache, MetadataSyncHandler, and `BaseTask` completion.
- Uses `CommonUtils.waitForResult` and `WaitForOptions` for concurrency synchronization.

## Risks and edge cases
- Heavy loops repeat many tests 100 times, increasing runtime but catching races.
- Timeout/latch-based concurrency checks can be flaky under severe scheduler delays.
- Exact load error count expectations encode retry policy details.
- Some comments are inaccurate copy-pastes, but assertions are specific.

## Test signals
- Very strong signal for mdsync task orchestration correctness under concurrency and failure.
- Regression indicators: over/under-parallel loading, duplicate same-path task execution, nested directory loads ignored, retry counts changed, or tasks left running after failure.
