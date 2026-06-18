<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSecondaryMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSecondaryMaster.java

## Purpose
Runs the secondary master process that replays master journal logs and writes checkpoints without becoming primary.

## Important APIs, Types, And Functions
- Constructor builds a `JournalSystem`, `MasterRegistry`, and `CoreMasterContext` with `AlwaysStandbyPrimarySelector`.
- `start()` starts the journal, marks running, blocks on a latch, then stops journal and closes registry.
- `stop()` releases the latch.
- `waitForReady(int)` waits until `mRunning` becomes true.
- `main(String[] args)` validates no arguments and runs the process.

## Control Flow
Construction creates masters using secondary metastore directory configuration and validates journal formatting. Runtime is simple: start the journal, wait until stop is requested, then cleanly close resources.

## State And Persistence Behavior
The secondary uses journal replay/checkpoint state and metastore factories rooted at `SECONDARY_MASTER_METASTORE_DIR`. It does not own primary state transitions, because the primary selector is always standby.

## Dependencies And Integration Points
Depends on `JournalUtils`, `JournalSystem`, `MasterUtils`, `CoreMasterContext`, `BackupManager`, `MasterUfsManager`, `DefaultSafeModeManager`, and process utilities. It integrates with the same master factories as the primary process but in standby-only mode.

## Risks And Edge Cases
An unformatted journal is fatal at construction. Because startup blocks on a latch, failure to call `stop()` leaves the process waiting. The TODO notes process structure differs from newer master-process classes.

## Test Signals
Readiness is observable through `waitForReady`. Integration signals are successful journal start/replay and clean shutdown with registry close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSecondaryMaster.java -->
