<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lockfile.h -->
# sources/distributed-fs/lizardfs/src/common/lockfile.h

## Purpose
Declares the `Lockfile` RAII-like manager and typed `LockfileException`. The source was read completely for this report.

## Important APIs, Types, And Functions
`Lockfile::StaleLock`, constructor/destructor, lock/message APIs, and `LockfileException::Reason` define the interface.

## Control Flow
The header describes operational flow; implementation performs POSIX locking in the `.cc` file.

## State And Persistence Behavior
Stores the lockfile name and `FileDescriptor`; persisted data is the actual lockfile and optional message.

## Dependencies And Integration Points
Depends on `cwrap.h` and `exceptions.h`; consumed by metadata locking and daemon startup paths.

## Risks And Edge Cases
The destructor does not automatically unlock, so callers must invoke `unlock` or rely on fd close/object ownership carefully.

## Test Signals
Integration tests should confirm behavior across processes, not only within one process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lockfile.h -->
