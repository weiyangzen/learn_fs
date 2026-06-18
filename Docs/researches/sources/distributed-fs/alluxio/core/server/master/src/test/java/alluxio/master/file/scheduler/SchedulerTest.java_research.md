# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/SchedulerTest.java

## Purpose
`SchedulerTest` validates master-side load-job scheduling: worker discovery, job submission/stop, journaling, capacity limits, asynchronous block load dispatch, exception handling, and stale job retention.

## Important APIs, Types, and Functions
The test exercises `Scheduler.updateWorkers`, `getActiveWorkers`, `submitJob`, `stopJob`, `start`, `stop`, `getJobProgress`, `getJobs`, and `cleanupStaleJob`. It uses `DefaultWorkerProvider`, `JournaledJobMetaStore`, `LoadJob`, `FileIterable`, mocked `BlockWorkerClient.load`, and helper `buildResponseFuture`.

## Control Flow, State, and Persistence
Worker tests simulate changing `FileSystemMaster.getWorkerInfoList` results and unavailable exceptions. Submit/stop tests verify journal entries for created, stopped, succeeded, and resubmitted jobs. Scheduling tests start the scheduler thread, feed mocked workers async futures with success, partial failure, full failure, and exceptions, then wait for terminal states. Retention mutates job states and cleans terminal jobs when retention is zero.

## Dependencies and Integration Points
The test integrates scheduler logic with authenticated user context, file-system master listing, file-system context worker clients, journal context append calls, load-job progress reporting, gRPC load requests/responses, and global job capacity/retention configuration.

## Risks
Several tests use sleeps and polling loops around asynchronous scheduling. Randomized block statuses and large full-capacity runs can make timing sensitive. Exact journal predicates encode persistence contract for job metadata.

## Test Signals
Signals include worker set stability across transient errors, duplicate job update behavior, capacity rejection, stop idempotence, successful async load completion with verification, handling worker exceptions and retryable listing failures, resource exhaustion, and cleanup of failed/succeeded/stopped while retaining created/verifying jobs.
