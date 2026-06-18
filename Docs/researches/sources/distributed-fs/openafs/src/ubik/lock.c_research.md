# sources/distributed-fs/openafs/src/ubik/lock.c

## Purpose
Provides ubik transaction-level read/write locking over a single database-wide `rwlock`. It supports two-phase locking by associating one lock type with each transaction and releasing only when the transaction ends.

## Important APIs, Types, And Functions
Public functions are `ulock_Init`, `ulock_getLock`, `ulock_relLock`, and `ulock_Debug`. The module-level lock is `struct Lock rwlock`. Helper macros `WouldReadBlock` and `WouldWriteBlock` inspect existing write/read/wait state for nonblocking lock attempts.

## Control Flow
`ulock_Init` initializes the lock. `ulock_getLock` validates requested type and transaction state, rejects duplicate locks and some read/write upgrade misuse, optionally checks whether a nonblocking attempt would fail, marks the transaction as `LOCKWAIT`, releases the DB lock, obtains the read or write lock unless `TRREADWRITE` is set, reacquires the DB lock, and records the final lock type. `ulock_relLock` releases the recorded read/write lock unless the transaction is flagged `TRREADWRITE`, then clears the transaction lock type. `ulock_Debug` reports current read/write lock presence.

## State And Persistence
State is process-local: the global lock and each transaction's `locktype`. No disk state is modified directly, but lock behavior controls safe access to transactional database state.

## Dependencies And Integration Points
The module depends on OpenAFS lock primitives, DBHOLD/DBRELE ordering from ubik internals, transaction flags from `ubik.h`, and `udisk_end`, which releases locks at transaction teardown.

## Risks And Test Signals
Risks include a likely inverted nonblocking helper macro interpretation, deadlocks if callers request locks out of order, aborts on duplicate lock attempts, and special `TRREADWRITE` behavior bypassing actual locks. Tests should cover read/read concurrency, write exclusion, nonblocking `EAGAIN`, lock release on abort/end, duplicate lock detection, and debug field accuracy.
