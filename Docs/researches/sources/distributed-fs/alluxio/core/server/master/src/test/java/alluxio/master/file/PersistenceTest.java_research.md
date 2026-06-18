# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PersistenceTest.java

## Purpose
PowerMock-based tests for FileSystemMaster asynchronous persistence scheduling and job tracking. The suite drives manual persistence scheduler/checker heartbeats, mocks JobMasterClient interactions, validates state transitions, retry/cancel behavior, rename/delete completion, and journal replay across master restarts.

## Important APIs/types/functions
- Uses `ManuallyScheduleHeartbeat` for `MASTER_PERSISTENCE_CHECKER` and `MASTER_PERSISTENCE_SCHEDULER`.
- Mocks `JobMasterClient.Factory.create` to return `mMockJobMasterClient`.
- Uses `scheduleAsyncPersistence`, `HeartbeatScheduler.execute`, `JobMasterClient.run`, `getJobStatus`, and UFS temp file touch.
- Whitebox helpers expose `mPersistRequests` and `mPersistJobs`.
- Helper methods: `createTestFile`, `checkEmpty`, `checkPersistenceRequested`, `checkPersistenceInProgress`, `waitUntilPersisted`, `startServices`, `stopServices`, and `createJobInfo`.

## Control flow
- `before()` sets UFS journal type, temporary root UFS, persistence retry intervals, authenticates a test user, then starts masters and mocks job client creation.
- Empty tests assert no residual requests/jobs across idle heartbeats.
- `successfulAsyncPersistence` moves from NOT_PERSISTED to requested, scheduled job, CREATED/RUNNING polling, temp UFS file creation, COMPLETED polling, and final PERSISTED state.
- `noRetryCanceled` ensures canceled job status clears queues without retry.
- `retryFailed` loops failed job status through checker/scheduler until max wait expires and state returns to not persisted with empty queues.
- `retryPersistJobRenameDelete` completes a job after the source file is renamed and source directory deleted, proving commit uses current file path by id.
- Replay tests stop/start services with the same journal and verify pending requests and in-progress jobs survive restart.

## State and persistence behavior
- Exercises both in-memory maps (`mPersistRequests`, `mPersistJobs`) and journaled persistence of their state.
- Touches temporary UFS files to simulate job output needed by the checker to mark files persisted.
- Validates `PersistenceState.NOT_PERSISTED`, `TO_BE_PERSISTED`, and `PERSISTED`, plus non-invalid UFS fingerprints after completion.

## Dependencies and integration points
- Integrates FileSystemMaster, block/metrics masters, UFS journal, job service client factory, heartbeats, UFS utilities, and security user state.
- Uses PowerMock static mocking, Mockito, and Whitebox reflection.

## Risks and edge cases
- Timing-sensitive loops and waits are bounded but can be flaky on slow environments.
- Whitebox field access is brittle against FileSystemMaster internal refactors.
- Static mocking of JobMasterClient factory can leak if teardown does not run.
- `mSafeModeManager`, `mStartTimeMs`, and `mPort` are initialized but not visibly used in the shown test body, suggesting legacy residue.

## Test signals
- High-value signal for async persistence lifecycle, retry policy, journal replay, and rename/delete race handling.
- Regression indicators: duplicate scheduling, missing persisted fingerprint, jobs lost after restart, or canceled/failed jobs staying in the wrong queue.
