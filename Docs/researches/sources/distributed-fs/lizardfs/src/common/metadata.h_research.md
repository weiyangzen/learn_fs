<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadata.h -->
# sources/distributed-fs/lizardfs/src/common/metadata.h

## Purpose
Declares metadata/changelog/session filenames, version helper functions, migration helper, and the global metadata lockfile pointer. The source was read completely for this report.

## Important APIs, Types, And Functions
Visible APIs are filename externs, `metadataGetVersion`, `changelogGetFirstLogVersion`, `changelogGetLastLogVersion`, `changelogsMigrateFrom_1_6_29`, `MetadataCheckException`, and `gMetadataLockfile`.

## Control Flow
The header has no runtime flow beyond declarations and exception macro expansion.

## State And Persistence Behavior
The named files are persisted metadata/changelog/session artifacts controlled by master processes.

## Dependencies And Integration Points
Depends on `exception.h` and `lockfile.h`; used by metadata startup/recovery code.

## Risks And Edge Cases
The global lockfile pointer makes lifecycle/order important during startup/shutdown.

## Test Signals
Integration tests should exercise the declarations through real recovery/startup code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/metadata.h -->
