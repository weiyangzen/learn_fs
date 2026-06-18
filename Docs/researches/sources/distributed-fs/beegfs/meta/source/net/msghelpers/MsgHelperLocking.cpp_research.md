<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.cpp

## Purpose
Provides shared lock-message helpers, especially recovery of lost file sessions and append-style flock updates.

## Important APIs, Types, and Functions
`trySesssionRecovery()` logs recovery, opens the file with read/write access, builds a `SessionFile`, attempts `SessionFileStore::addAndReferenceRecoverySession()`, and compensates by closing metadata if the owner FD is already reused. `flockAppend()` references the client session and owner FD, ignores unlocks for missing sessions, handles lock-cancel on existing files without full recovery, recovers sessions for lock requests, calls `FileInode::flockAppend()`, and notifies waiters through `LockingNotifier`.

## Control Flow, State, and Persistence
The helper mutates session stores and file lock state. Recovery reopens metadata because client lock requests can imply a session that vanished after metadata-server restart. Failed recovery closes the reopened inode to avoid leaked references.

## Dependencies and Integration Points
Depends on `SessionStore`, `SessionFileStore`, `SessionFile`, `MetaStore`, `EntryLockDetails`, `LockingNotifier`, client IDs, and mirrored session selection based on `EntryInfo`.

## Risks and Test Signals
Risks include the misspelled API name `trySesssionRecovery`, recovering with broader read/write access than originally used, races where owner FD is reused, and lock cancel behavior without session state. Tests should cover missing session unlock, cancel, recover success/failure, WOULD_BLOCK locks, waiter notifications, and mirrored sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.cpp -->
