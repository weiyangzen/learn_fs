# sources/distributed-fs/lizardfs/src/mount/client_common.h

## Purpose
`client_common.h` declares shared mount-client helpers and operation identifiers used by the LizardFS mount client implementation.

## Important APIs, Types, And Functions
- Anonymous enum assigns operation ids (`OP_STATFS` through `OP_FLOCK`, plus `STATNODES`) used for stats counters.
- `MagicFile` stores mutable pseudo-file value state with a mutex and read/write flags.
- `PthreadMutexWrapper` is an RAII wrapper around `pthread_mutex_t` with explicit unlock/relock support.
- `LizardClient::stats_inc`, `attr_to_stat`, and `makeattrstr` are declared utility functions.

## Control Flow
The enum provides indexes for statistics. `PthreadMutexWrapper` locks in its constructor, unlocks in its destructor if still locked, and allows manual unlock/lock with assertions. `MagicFile` is a small synchronized state container for special files.

## State And Persistence
No globals are defined here. `MagicFile` instances hold transient in-memory data. Attribute conversion helpers operate on metadata replies.

## Dependencies And Integration Points
It includes common attributes and `mount/lizard_client.h`. Operation ids are used by mount request handling and stats reporting.

## Risks
- Enum ordering is likely externally meaningful for stats arrays; inserting values can break reporting.
- `PthreadMutexWrapper` is noncopy-safe by convention only; no deleted copy constructor is declared.
- Assertions guard misuse but release builds may allow incorrect lock/unlock sequencing.

## Test Signals
Tests should verify RAII unlock behavior, explicit unlock/relock assertions in debug, operation count matching stats arrays, and attribute conversion output.
