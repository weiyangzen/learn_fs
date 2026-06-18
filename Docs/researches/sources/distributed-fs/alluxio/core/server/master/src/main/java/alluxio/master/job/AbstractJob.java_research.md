# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/AbstractJob.java

## Purpose
`AbstractJob` supplies common job identity, user, lifecycle state, start/end timing, and running/done predicates for master-side scheduler jobs.

## Important APIs, types, and functions
It implements `Job<T extends Task<?>>`. The constructor requires a user optional and job id, starts in `JobState.RUNNING`, and records `mStartTime`. APIs include `getJobId()`, `getEndTime()`, `setEndTime(long)`, `getJobState()`, `setJobState(JobState)`, `isRunning()`, and `isDone()`.

## Control flow
`setJobState` logs the transition and automatically sets `mEndTime` when the new state is not running or verifying. `isRunning` treats `RUNNING` and `VERIFYING` as active. `isDone` returns true only for `SUCCEEDED` and `FAILED`.

## State and persistence behavior
This base class stores runtime state in fields; subclasses decide what to journal. `LoadJob` journals job id, state, options, and optional end time but not all runtime counters inherited or created.

## Dependencies and integration points
It depends on the scheduler `Job`, `Task`, and `JobState` contracts. `LoadJob` extends it in this subset.

## Risks
The logger is initialized with `LoadJob.class`, which is odd for an abstract base and may mislabel logs for other future subclasses. State is mutable and not synchronized; subclasses are expected to be manipulated by the scheduler thread.

## Test signals
Tests should cover initial state, end-time setting on terminal state, verifying treated as running, done predicates, and subclass journal restore behavior for end time.
