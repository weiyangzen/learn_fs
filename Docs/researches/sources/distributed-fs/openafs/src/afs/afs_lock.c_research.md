# sources/distributed-fs/openafs/src/afs/afs_lock.c

## Purpose
`afs_lock.c` provides the generic AFS lock implementation used by Cache Manager structures. It supports read, write, shared, and boosted write lock acquisition, lock release policies biased toward readers or writers, wait-time accounting, and optional ICL tracing of lock operations.

## Important APIs, types, and functions
`Lock_Init` initializes `struct afs_lock` counters and ownership/debug fields. `Afs_Lock_Obtain` implements acquisition for `READ_LOCK`, `WRITE_LOCK`, `SHARED_LOCK`, and `BOOSTED_LOCK`. `Afs_Lock_ReleaseR` and `Afs_Lock_ReleaseW` choose which waiter class to wake. `Afs_Lock_Trace` emits lock trace records when `afs_trclock` is enabled while avoiding recursive tracing of ICL locks.

## Control flow
Acquisition records a start timestamp, increments `num_waiting`, sets a wait-state bit, sleeps on either `readers_reading` or `excl_locked`, and loops until the requested condition is satisfied. Read locks wait only for a write lock. Write locks wait for both exclusive state and readers. Shared locks wait for no exclusive state and then set `excl_locked` to `SHARED_LOCK`. Boosted locks wait for readers to drain and then become write locks. After acquisition, elapsed wait time is accumulated into the lock object and optionally traced.

Release paths inspect `wait_states`, clear the selected class, and wake the corresponding sleep address. `Afs_Lock_ReleaseR` prefers queued readers; `Afs_Lock_ReleaseW` prefers queued exclusive locks.

## State and persistence behavior
The lock state is entirely in memory: counts of readers, exclusive lock kind, waiter bitmask, number waiting, last reader/writer pid fields, source indicator, and cumulative `time_waiting`. No state is persisted beyond runtime diagnostics.

## Dependencies and integration points
The implementation depends on OSI sleep/wakeup primitives, time helpers, AFS stats macros, and ICL tracing globals. Lock macros elsewhere in the tree wrap these functions, so changes affect cache, vcache, dcache, ICL, DNLC, NFS translator, and PAG code.

## Risks and edge cases
Correctness depends on callers holding the expected global synchronization around lock operations. Wakeup policy can affect fairness. `BOOSTED_LOCK` skips waiting on existing exclusive state and only waits for readers, so it must only be used in contexts matching that convention. Lock tracing must avoid tracing ICL internal locks or it can recurse.

## Test signals
Exercise concurrent read/write/shared acquisition, boosted lock transitions, reader- and writer-preferred releases, cumulative wait-time accounting, and lock tracing with non-ICL locks while ICL logging is active.
