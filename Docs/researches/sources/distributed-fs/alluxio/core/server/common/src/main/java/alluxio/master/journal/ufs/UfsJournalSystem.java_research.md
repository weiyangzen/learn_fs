# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalSystem.java

## Purpose
`UfsJournalSystem` is the current UFS-backed implementation of `AbstractJournalSystem`. It creates one `UfsJournal` per master under a shared base URI and coordinates lifecycle, primacy transitions, catchup, formatting, checkpointing, and sequence-number reporting across those journals.

## Important APIs, Types, and Functions
The important entry points are the constructor, `createJournal(Master)`, `gainPrimacy()`, `losePrimacy()`, `suspend()`, `resume()`, `catchup()`, `waitForCatchup()`, `getCurrentSequenceNumbers()`, `startInternal()`, `stopInternal()`, `isFormatted()`, `isEmpty()`, `format()`, and `checkpoint(StateLockManager)`. It uses `UfsJournal`, `UfsJournalCheckpointThread.CatchupState`, `CatchupFuture`, `JournalSink`, `StateLockManager`, `StateLockOptions`, `MetricsSystem`, `Timer`, `CommonUtils.invokeAll`, `CommonUtils.waitFor`, `Closer`, and `ExponentialTimeBoundedRetry`.

## Control Flow, State, and Persistence
The system stores `mBase`, a quiet-time gate for standby-to-primary promotion, a concurrent map from master name to journal, and `mInitialCatchupTimeMs` for one-time catchup metrics. `createJournal()` appends the master name to the base URI, builds a sink supplier, records the journal, and returns it to the caller. Primacy gain is parallelized with `CommonUtils.invokeAll()` and propagates failures as runtime exceptions so a standby master crashes instead of serving with partially promoted journals. Primacy loss first signals every journal, then waits for each one to finish demotion.

Catchup receives a map of master names to target sequence numbers, delegates to each journal, and returns a combined future. `waitForCatchup()` polls every journal until all checkpoint threads report `DONE` or the configured maximum catchup time expires, recording the initial catchup duration either way. Checkpointing takes the master state lock exclusively before invoking each journal checkpoint, so snapshot persistence is coordinated with state mutation.

## Dependencies and Integration Points
This class is integrated into master startup and leader election through `AbstractJournalSystem`. It depends on Alluxio configuration keys for UFS catchup timeout, metric keys for UFS journal catchup/initial replay, master journal sink registration, URI path helpers, retry helpers, and the per-master `UfsJournal` implementation. Persistent effects are all delegated to the per-master UFS journals.

## Risks and Test Signals
Risks include partial journal promotion if a journal blocks inside `gainPrimacy()`, timeout-only handling in `waitForCatchup()` where startup continues after logging, and `catchup()` assuming every journal name exists in the supplied sequence map. Useful signals are multi-master promotion/demotion tests, catchup timeout metrics, checkpoint tests verifying state-lock exclusion, retry-on-close behavior, and sequence-number consistency across all registered journals.
