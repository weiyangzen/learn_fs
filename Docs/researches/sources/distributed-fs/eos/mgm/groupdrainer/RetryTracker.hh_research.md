# sources/distributed-fs/eos/mgm/groupdrainer/RetryTracker.hh

## Purpose
Provides a small retry backoff tracker for filesystem drain retry attempts.

## Important APIs, types, and functions
`DEFAULT_RETRY_INTERVAL` is four hours. `RetryTracker` stores `count` and `last_run_time`. `need_update()` returns true before the first run or after the configured interval has elapsed. `update()` increments the count and records the current steady-clock time. Both methods accept an optional `SteadyClock` test hook.

## Control flow
`GroupDrainer::populateFids()` and `handleRetries()` use this tracker to suppress repeated retries for failed FIDs on the same FSID until the interval passes.

## State and persistence
State is in memory per FSID inside `GroupDrainer::mFsidRetryCtr`.

## Dependencies and integration points
Depends on `common/SteadyClock.hh` for testable time.

## Risks and test signals
The comparison uses `>` rather than `>=`, so exactly equal elapsed intervals do not retry. Count is `uint16_t`; long-running services should avoid overflow assumptions. Tests should cover first run, before/after interval, exact boundary, injected clock, and update count progression.
