# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/LoadJobTest.java

## Purpose
`LoadJobTest` validates batching, retry health, partial listing, and progress reporting for master load jobs.

## Important APIs, Types, and Functions
The test exercises `LoadJob.getNextBatchBlocks`, `addBlockToRetry`, `isHealthy`, `setJobState`, `addLoadedBytes`, `getProgress`, `addBlockFailure`, and `failJob`, with `FileIterable` backed by mocked `FileSystemMaster.listStatus`.

## Control Flow, State, and Persistence
Batch tests generate synthetic files and blocks, request fixed block counts, requeue failures, and verify distinct UFS paths in each batch. Partial-listing tests emulate `ListStatusContext` start-after and batch size handling. Progress tests compare exact text and JSON report strings before and after block failures and job failure.

## Dependencies and Integration Points
The tests depend on generated `FileInfo` fixtures from `LoadTestUtils`, scheduler job state, gRPC `Block`, `JobProgressReportFormat`, and runtime exception types.

## Risks
Progress report formatting is asserted as exact strings, so intended formatting changes require test updates. Randomized fixture generation can make debugging harder, though counts are deterministic enough for these assertions.

## Test Signals
Signals include retry queue ordering, end-of-iteration empty batches, partial listing skip of already-loaded files, unhealthy state after repeated retries, byte and file progress accounting, failure percentage, failed-file counting, and verbose/non-verbose error inclusion.
