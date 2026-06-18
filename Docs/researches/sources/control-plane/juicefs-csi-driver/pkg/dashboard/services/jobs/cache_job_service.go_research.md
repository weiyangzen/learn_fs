# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/cache_job_service.go

## Purpose
`CacheJobService` provides cached, time-ordered listing for dashboard smooth-upgrade Jobs and maintains an index through controller-runtime watches.

## Important APIs, Types, And Functions
It defines `CacheJobService`, `ListAllBatchJobs`, `Reconcile`, and `SetupWithManager`, plus a package logger.

## Control Flow
`ListAllBatchJobs` parses page, order, and name filters, iterates `jobIndexes`, fetches each Job from the cache, filters with `utils.IsUpgradeJob`, and returns a paginated result. `Reconcile` fetches the Job, removes missing entries, ignores deleting objects, and indexes upgrade jobs by creation time. `SetupWithManager` watches all Job create/update/delete events; delete events remove upgrade jobs directly from the index.

## State And Persistence
State is the in-memory `TimeOrderedIndexes[batchv1.Job]`. Kubernetes Job objects persist outside this service.

## Dependencies And Integration Points
It wraps `jobService`, shares result types from `service.go`, uses `dashboard/utils.TimeOrderedIndexes`, and is registered by `API.StartManager`.

## Risks
Create/update predicates return true for all jobs, so the reconciler sees unrelated jobs and filters later. The `descend` query only treats literal `descend` as descending, while other cached services default differently. Existing jobs before watch startup rely on manager cache/reconcile events to populate the index.

## Test Signals
No direct tests are present. Tests should cover ordering, filtering, delete removal, and query default consistency.
