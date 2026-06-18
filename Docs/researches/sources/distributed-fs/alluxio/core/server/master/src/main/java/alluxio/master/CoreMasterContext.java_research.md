<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMasterContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMasterContext.java

## Purpose
Carries shared dependencies and configuration needed by core master implementations, including journal access, safe mode, backup, metastore factories, UFS manager, primary selector, start time, and port.

## Important APIs, Types, And Functions
- `CoreMasterContext` extends `MasterContext<MasterUfsManager>`.
- Getters expose `SafeModeManager`, `BackupManager`, `BlockMetaStore.Factory`, `InodeStore.Factory`, `JournalSystem`, start time, port, and nullable `PrimarySelector`.
- `Builder` provides setters for all fields and `build()`.

## Control Flow
The builder collects dependencies, then the private constructor validates required fields with Guava `Preconditions.checkNotNull` and passes journal, selector, user state, and UFS manager to the superclass.

## State And Persistence Behavior
This is immutable context after construction. Persistence-related behavior is represented by the journal system and metastore factory choices rather than direct I/O.

## Dependencies And Integration Points
Integrates `JournalSystem`, `PrimarySelector`, `UserState`, `BackupManager`, `BlockMetaStore`, `InodeStore`, and `MasterUfsManager`. It is built by `AlluxioMasterProcess` and `AlluxioSecondaryMaster` before `MasterUtils.createMasters` instantiates services.

## Risks And Edge Cases
`PrimarySelector` is nullable by API but many consumers may assume it is available. Builder defaults for start time and port are primitive zero values if omitted, so callers must set them intentionally.

## Test Signals
Signals include construction failure for missing required dependencies and correct propagation into core master subclasses and backup roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/CoreMasterContext.java -->
