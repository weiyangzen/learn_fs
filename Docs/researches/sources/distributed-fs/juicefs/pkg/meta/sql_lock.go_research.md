# sources/distributed-fs/juicefs/pkg/meta/sql_lock.go

## Purpose

`sql_lock.go` implements SQL-backed BSD flock and POSIX byte-range lock persistence for `dbMeta`. It keeps lock state in the `flock` and `plock` tables so locks are visible across JuiceFS clients sharing the same SQL metadata backend.

## Important APIs, Types, And Functions

`Flock` handles whole-file read/write/unlock operations. It maps the caller owner to signed int64, removes rows on `F_UNLCK`, or loads all flock rows for an inode under `ForUpdate`, checks conflicts, and inserts or updates the caller's row with `Ltype` `R` or `W`.

`Getlk` inspects `plock` rows for conflicting POSIX byte-range locks and returns the first conflict by mutating `ltype`, `start`, `end`, and `pid`. `Setlk` inserts, updates, or deletes byte-range records for the caller after conflict detection against other session/owner pairs. `ListLocks` returns both POSIX and flock states for diagnostics.

## Control Flow

Both `Flock` and `Setlk` perform conflict checks inside write transactions. The code first validates the target inode exists by locking the corresponding `node` row, then locks and reads all relevant `flock` or `plock` rows for that inode. Own locks are ignored for conflict purposes. Nonblocking calls return `EAGAIN` on conflict; blocking calls sleep and retry until the lock succeeds, a non-retry error occurs, or the context is canceled.

For `Setlk`, unlock requests load the caller's serialized byte-range records, call `updateLocks`, and either delete the `plock` row or update its `Records` blob. Lock requests compare ranges with all other owners, merge/update the caller's records, then insert or update the serialized blob only when it changed.

## State And Persistence Behavior

Whole-file locks are one row per `(inode, sid, owner)` with a single lock type byte. POSIX locks are one row per `(inode, sid, owner)` with a serialized `Records` blob produced by `dumpLocks` and parsed by `loadLocks`. Successful state changes emit changelog operations such as `FLOCK`, `SETLK`, and unlock variants. Stale session cleanup in `sql.go` deletes both `flock` and `plock` rows by session id.

## Dependencies And Integration Points

The code depends on lock constants (`F_UNLCK`, `F_RDLCK`, `F_WRLCK`), serialized `plockRecord` helpers (`loadLocks`, `updateLocks`, `dumpLocks`), `ownerKey`, diagnostic item types, `dbMeta.txn`, xorm row locking, and the session id `m.sid`. It integrates with `ListSessions(detail=true)` through the same persisted lock tables.

## Risks And Edge Cases

Blocking locks use polling sleeps rather than database wait/notify, so high contention can add latency and transaction churn. `Getlk` reads with `m.db.Rows` outside `roTxn`, so it has weaker snapshot/retry behavior than the transactional update paths. Owner values are cast from uint64 to int64; callers using values above max int64 would wrap. Conflict reporting returns the first map iteration conflict, which is not deterministic.

## Test Signals

The listed `sql_test.go` file does not directly test SQL locks. Lock behavior is likely exercised through shared meta tests, but SQL-specific persistence, stale-session cleanup, blocking cancellation, owner casting, and byte-range merge/split behavior warrant focused tests.
