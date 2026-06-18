# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/manager.go

## Purpose
This file implements BeeSync's local work manager. It durably journals assigned work requests, indexes them by job/request ID, feeds workers through a priority scheduler, handles cancellation/update requests from BeeRemote, and coordinates shutdown.

## Important APIs, Types, and Functions
`Config` defines work journal path, job store path, active queue size, and worker count. `Manager` owns readiness, worker/manager contexts, Badger-backed `workJournal` and `jobStore`, active work map, active queue, scheduler, RST client store, and BeeRemote client. Key methods are `NewAndStart`, `IsReady`, `UpdateConfig`, `manage`, `pullInWork`, `pullInRescheduledWork`, `initScheduler`, `SubmitWorkRequest`, `UpdateWork`, and `Stop`.

## Control Flow
Startup creates Badger stores, initializes the scheduler, recovers existing journal entries by priority, starts manager and worker goroutines, and waits for dynamic config before pulling work. `manage` receives priority tokens, moves ready new and rescheduled journal entries into `activeWork` and `activeWorkQueue`, and removes active entries when workers report completion. `SubmitWorkRequest` requires readiness, creates/locks a job index entry, rejects duplicate job/request IDs, creates a prioritized journal entry, initializes a scheduled work result, stores the job-to-submission mapping, and adds a scheduler token. `UpdateWork` supports cancellation: it finds the job mapping, cancels active contexts if present, carefully locks journal entries with documented lock ordering, deletes journal/job entries, adjusts scheduler tokens, and returns the final cancellation response.

## State and Persistence Behavior
`workJournal` stores `workEntry` values keyed by fixed-width priority/submission IDs; each entry contains the request, latest result, and optional execute-after time. `jobStore` maps job IDs to request IDs and submission IDs. `activeWork` is in-memory only and maps a `workIdentifier` to a cancellable context. On restart, `initScheduler` repopulates scheduler tokens from the journal. Completed work is removed only after the worker successfully reports results to BeeRemote; failed reporting leaves entries for retry/recovery.

## Dependencies and Integration Points
The manager depends on Badger/`kvstore`, `common/scheduler`, `common/rst.ClientStore`, `sync/internal/beeremote.Client`, protobuf `flex`, gRPC status codes, and worker code in `work.go`. It is invoked by the worker-node gRPC server and by `cmd/beegfs-sync`.

## Risks and Edge Cases
The code has explicit deadlock-sensitive lock ordering between `activeWorkMu` and journal entries. Cancellation of inactive work may block the manager from pulling new work while waiting for a journal lock. Work-result delivery to BeeRemote is retried by worker logic and can keep DB entries active indefinitely if Remote is unreachable. Dynamic RST updates after initial setup are not supported by underlying clients. The constructor uses `m.scheduler.GetPriorityLevels()` before assigning `m.scheduler`, which appears risky unless the zero-value manager has been initialized elsewhere; this path deserves review.

## Test Signals
`manager_test.go` covers config updates, duplicate submission rejection, successful and failed work processing, BeeRemote response failure retention, cancellation of failed/active/inactive requests, refusal to cancel completed work, DB cleanup, and benchmarks for submission and Badger operations. Tests use mock RSTs and mock BeeRemote providers.
