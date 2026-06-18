<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_lock.c -->
# sources/distributed-fs/openafs/src/budb/db_lock.c

## Purpose
Implements RPC-visible locks for budb text blocks and allocates client instance IDs. These locks protect multi-call text replacement operations.

## Important APIs, Types, And Functions
RPC wrappers `SBUDB_FreeAllLocks`, `SBUDB_FreeLock`, `SBUDB_GetInstanceId`, and `SBUDB_GetLock` audit calls and delegate to local implementations. `GetLock` validates `lockName`, checks expiration, records `lockState`, `lockTime`, `expires`, and `instanceId`, and returns a one-based handle. `FreeLock` and `FreeAllLocks` clear lock records. `checkLockHandle` validates handle range only.

## Control Flow
Lock acquisition is a write transaction. If an unexpired lock exists, the caller receives `BUDB_SELFLOCKED` for the same instance or `BUDB_LOCKED` for another. Expired locks can be overwritten. Release writes the cleared lock record back into the header.

## State And Persistence
Locks and `lastInstanceId` are persisted in the database header, so server restarts see the stored fields until overwritten/expired. Timestamps are stored in network order except local comparisons convert with `ntohl`.

## Dependencies And Integration Points
Used by `db_text.c` text save/get calls and backup clients managing dump schedules, volume sets, and tape hosts.

## Risks And Test Signals
`checkLockHandle` only checks range, not ownership or expiration, so callers must enforce protocol discipline. Signals are concurrent lock acquisition, self-lock behavior, expiration, freeing all locks for an instance, and text save rejection without a handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/db_lock.c -->
