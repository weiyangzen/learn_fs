# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/work.go

## Purpose

This file implements the BeeSync worker-side execution path for BeeRemote work requests. It defines the durable journal entry shape used to persist requested work, the active work identity/context structures used by the manager, and the `worker` loop that pulls `workAssignment` objects from a queue, executes file-transfer or builder work against a remote storage target, reports results to BeeRemote, and cleans up journal/job-store state.

## Important APIs, Types, And Functions

`workEntry` persists a desired `workRequest`, actual `work` result, and `ExecuteAfter` reschedule time. The `workRequest` and `work` wrappers implement `GobEncode`/`GobDecode` by marshaling protobuf `flex.WorkRequest` and `flex.Work`, allowing Badger-backed `kvstore.MapStore` entries to store protobuf values through Go gob. `workIdentifier` keys active work by submission, job, and request IDs. `workAssignment` carries a cancellable context and identifier into a worker. `worker.run` drains the queue until its parent context is canceled. `worker.process` owns state validation, storage target lookup, readiness checks, journal commits, cleanup decisions, and dispatch to `processWork` or `processBuilder`. `sendWorkResult` retries BeeRemote updates until success, cancellation, or non-retryable failure.

## Control Flow

Processing starts by locking the work journal entry for the submission ID. Invalid or terminal starting states are converted to failed or resent to BeeRemote. Unknown remote storage targets fail immediately. Otherwise the selected `rst.Provider` is asked whether the work is ready; not-ready work is marked `RESCHEDULED`, assigned an `ExecuteAfter`, reported, and requeued through `rescheduleWork`. Ready work is marked `RUNNING` with an update-only journal commit. Non-builder work iterates unfinished parts and calls `ExecuteWorkRequestPart`, committing part progress after each transfer. Builder work streams generated `beeremote.JobRequest` values from `ExecuteJobBuilderRequest` and submits each to BeeRemote.

## State And Persistence

The work request is treated as desired state from BeeRemote, while the work result is actual local execution state. The journal is committed on every part completion so progress can survive crashes and be observed by readers. Completed and successfully reported work triggers cleanup of the journal entry and either the whole job-store entry or the single request ID within it. If cleanup of the job store fails, the journal entry is retained for retry. Canceled execution records local status but deliberately avoids result submission in some paths so the canceling owner can decide retry/report behavior.

## Dependencies And Integration Points

The worker depends on `common/kvstore` locking semantics, BeeSync metrics counters such as `beeSyncProcessed`, `beeSyncComplete`, and `beeSyncRescheduled`, `rst.ClientStore` providers, BeeRemote gRPC client methods `UpdateWorkRequest` and `SubmitJobRequest`, generated protobuf packages `flex` and `beeremote`, zap logging, and `unix.EAGAIN` for a BeeGFS client configuration hint. It is central to BeeSync restart/resume behavior because journal replay elsewhere can resubmit persisted work.

## Risks And Test Signals

The file is concurrency and persistence sensitive: errors in commit/delete ordering can duplicate BeeRemote reports or leak journal entries. `sendWorkResult` retries indefinitely with fixed one-second delay, which is robust for transient outages but can stall worker shutdown until context cancellation. Builder submission counts failed child jobs but still relies on BeeRemote-side status visibility. `processWork` currently treats all provider transfer errors as terminal, with TODOs noting retry classification gaps. No tests are in this file, so coverage likely comes from broader work manager or BeeSync integration tests that should assert cancellation, crash replay, reschedule, and cleanup behavior.
