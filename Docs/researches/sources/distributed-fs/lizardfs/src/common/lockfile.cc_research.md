<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lockfile.cc -->
# sources/distributed-fs/lizardfs/src/common/lockfile.cc

## Purpose
Implements advisory lockfile creation, locking, optional stale-file rejection, removal, and message storage. The source was read completely for this report.

## Important APIs, Types, And Functions
`Lockfile::lock`, `unlock`, `isLocked`, `hasMessage`, `eraseMessage`, and `writeMessage` are implemented using POSIX open/fcntl/fstat/ftruncate/write.

## Control Flow
Locking checks for an existing file, optionally rejects stale files, opens/creates the path, then applies a write lock with `F_SETLK`. Unlock closes the fd and removes the file. Message helpers operate on the opened lockfile fd.

## State And Persistence Behavior
Persistent state is the lockfile path and its contents. Runtime state is the owned `FileDescriptor`; `isLocked` is equivalent to fd open.

## Dependencies And Integration Points
Depends on `cwrap`, `massert`, `exceptions`, POSIX file APIs, and `fs` helpers. Used to protect singleton daemons/metadata operations.

## Risks And Edge Cases
Open-before-lock races and stale-file semantics are subtle. `writeMessage` does not retry partial writes. `unlock` removes the path even if another process created a new file at the same name after close in unusual races.

## Test Signals
Needs process-level tests for stale rejection, contention, message truncation/write, and cleanup on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lockfile.cc -->
