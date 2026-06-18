# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/LoadJob.java

## Purpose
`LoadJob` is a master scheduler job that loads persisted, completed files from UFS into Alluxio workers. It batches missing blocks, sends `LoadRequest`s to workers, tracks progress/failures, supports optional bandwidth limits and verification pass, and journals enough job metadata for recovery.

## Important APIs, types, and functions
The public job type is `TYPE = "load"`. `QUALIFIED_FILE_FILTER` selects non-folder, completed, persisted files not already 100 percent in Alluxio. Main APIs include `getDescription()`, `getBandwidth()`, `updateBandwidth()`, `isVerificationEnabled()`, `setVerificationEnabled()`, `failJob()`, `setJobSuccess()`, `getProgress()`, `getNextTask(WorkerInfo)`, `getNextBatchBlocks(int)`, `processResponse(LoadTask)`, `updateJob(Job<?>)`, `needVerification()`, `initiateVerification()`, and `toJournalEntry()`. Nested `LoadTask` runs a block-worker `load` RPC. Nested `LoadProgressReport` formats text or JSON progress.

## Control flow
The scheduler asks for tasks. `getNextBatchBlocks` lazily creates a file iterator, advances files and block ids, and emits blocks whose block info has no locations. Retry blocks are drained early only when the retry queue is near capacity or no new work remains. Worker responses subtract failed block lengths, retry retryable failures while the job remains healthy and retry capacity permits, and record per-file failure messages for non-retryable or unhealthy failures. Execution/cancellation/interruption exceptions route blocks back to retry or failure and preserve interrupt status. Verification resets current counters and iterator state for another pass when the previous pass is complete.

## State and persistence behavior
The job stores configuration (`path`, `user`, `jobId`, bandwidth, partial listing, verification flag), runtime queues/counters, failed file summaries, current iterators, state, and failure reason. `toJournalEntry()` persists path, state, partial listing, verify, job id, optional user, optional bandwidth, and optional end time. Runtime progress, retry blocks, loaded bytes, and failures are not journaled, so recovery reconstructs a fresh job over current file metadata.

## Dependencies and integration points
It depends on scheduler `Job`/`Task`, worker `BlockWorkerClient.load`, gRPC load messages, `FileIterable`, metrics, Jackson for JSON reports, Alluxio wire file/block/worker info, and configuration `JOB_BATCH_SIZE`. It integrates with the master scheduler and worker block loading RPC path.

## Risks
The class is explicitly not thread-safe and assumes scheduler-thread mutation, though it uses atomics for report counters. `isHealthy` relies on operator precedence; as written, the failure ratio can make a failed-state job appear healthy if the ratio is low, so callers should verify intended grouping. `mTotalByteCount` can be inaccurate for retries and verification as the comment notes. Recovery repeats work because runtime progress is not persisted. Failed-file map keys use UFS path and retain only the first failure message per file.

## Test signals
Tests should cover filtering, batching across files, retry threshold/capacity, response statuses, exception paths, health threshold edge cases, verification reset, progress text/JSON, metrics increments, journal serialization, update-job semantics, and recovery through `JournalLoadJobFactory`.
