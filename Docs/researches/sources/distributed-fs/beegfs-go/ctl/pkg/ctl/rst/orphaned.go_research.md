# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/orphaned.go

## Purpose
Scans BeeRemote job database paths and marks entries deleted when the corresponding BeeGFS path no longer exists, supporting cleanup of orphaned Remote DB records.

## Important APIs, Types, And Functions
Exports `CleanupOrphanedCfg`, `CleanupOrphanedResult`, and `CleanupOrphaned`. Internal helpers are `cleanupOrphanedPath` and `isNotFoundErr`.

## Control Flow
`CleanupOrphaned` validates path prefix, gets a BeeGFS client and BeeRemote client, starts `GetJobs` streaming, then uses an `errgroup` pipeline: one goroutine converts job responses into a path channel and worker goroutines lstat paths and update jobs. Worker count is `num-workers - 1` with a minimum of one. It returns a results channel plus wait function.

`cleanupOrphanedPath` skips existing paths, treats not-exist and ENOTDIR as orphaned, calls `UpdateJobs` with `NewState=DELETED` and `ForceUpdate=true`, and converts not-found update errors into skipped results.

## State And Persistence
Persistent effect is BeeRemote job state updates to deleted. Local state is transient channels and worker goroutines.

## Dependencies And Integration Points
Depends on `GetJobs`, BeeGFS filesystem provider `Lstat`, BeeRemote `UpdateJobs`, Viper worker count, gRPC status codes, and common RST not-found errors.

## Risks And Edge Cases
The scan only considers database paths returned by `GetJobs`; it does not reconcile filesystem paths absent from the DB. Race conditions are inherent: a path can be recreated after `Lstat` failure but before update. If `GetJobs` returns an error, the pipeline aborts. Results may be unordered due to parallel workers.

## Test Signals
No direct tests. Valuable tests would cover path exists, not exists, ENOTDIR, update not found, update false-ok response, streaming error, and worker cancellation.
