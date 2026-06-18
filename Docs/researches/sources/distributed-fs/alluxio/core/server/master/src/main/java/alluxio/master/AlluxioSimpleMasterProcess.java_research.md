<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSimpleMasterProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSimpleMasterProcess.java

## Purpose
Abstract base for simpler master processes that run a single master domain, such as job master style processes, while sharing journal, service, and primary/standby lifecycle behavior.

## Important APIs, Types, And Functions
- Constructor stores `mMasterName` and `mJournalDomain`, sets a hostname property if missing, and formats an unformatted journal.
- `start()` runs the standby/primary loop.
- `stop()` stops services, journal, components, and leader selector.
- `startMasterComponents` and `stopMasterComponents` wrap registry start/stop with master-specific error messages.

## Control Flow
Startup starts simple services and journal, then starts leader selection. Each loop starts registry components as standby, waits for primary, gains journal primacy, restarts components as leader, promotes services, waits for standby, demotes services, stops components, and loses journal primacy.

## State And Persistence Behavior
Persistent state is journal-backed and can be formatted during construction when absent. Runtime state includes registered simple services, registry components, and leader selector state.

## Dependencies And Integration Points
Extends `MasterProcess`, uses `JournalSystem`, `PrimarySelector`, `SimpleService`, `NodeState`, and network address utilities. It is a reusable lifecycle scaffold for non-core master domains.

## Risks And Edge Cases
Unlike `AlluxioMasterProcess`, this simpler loop does not include catchup protection, emergency backup, unstable-primacy callbacks, or explicit stop flags. Failures in registry start/stop become runtime exceptions.

## Test Signals
Relevant signals are promotion/demotion lifecycle tests for subclasses, journal formatting behavior, service promote/demote ordering, and readiness through inherited `MasterProcess` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/AlluxioSimpleMasterProcess.java -->
