<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMaster.java

## Purpose
Abstract base for masters running inside the core master process. It captures core-specific shared dependencies from `CoreMasterContext` and exposes them to subclasses.

## Important APIs, Types, And Functions
- Constructor accepts `CoreMasterContext`, `Clock`, and `ExecutorServiceFactory`, delegates to `AbstractMaster`, then stores safe mode manager, backup manager, journal system, primary selector, start time, and RPC port.

## Control Flow
There is no active control flow beyond construction. Subclasses use the protected fields during their own lifecycle, RPC handling, journaling, and service logic.

## State And Persistence Behavior
The class stores references rather than owning state transitions. Persistence flows through `mJournalSystem` and backup operations through `mBackupManager`.

## Dependencies And Integration Points
Depends on `AbstractMaster`, `CoreMasterContext`, `JournalSystem`, `SafeModeManager`, `BackupManager`, `PrimarySelector`, `Clock`, and executor-service factories. It is the shared superclass for core masters such as block, file system, meta, and metrics masters.

## Risks And Edge Cases
Because fields are protected, subclass behavior depends on `CoreMasterContext` being fully populated. Misconfigured context can cascade into many core master implementations.

## Test Signals
Signals are indirect through concrete core master tests. Construction tests should ensure context values propagate correctly to subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMaster.java -->
