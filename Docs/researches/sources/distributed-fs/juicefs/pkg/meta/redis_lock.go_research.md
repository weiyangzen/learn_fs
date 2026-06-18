# sources/distributed-fs/juicefs/pkg/meta/redis_lock.go

## Purpose

`redis_lock.go` implements BSD-style flock and POSIX byte-range locks for the Redis metadata backend. It stores lock ownership in Redis hashes and tracks which lock keys belong to the current session for stale-session cleanup.

## Important APIs, Types, and Functions

`Flock` handles whole-file shared, exclusive, and unlock operations using `lockf$inode` hashes. `Getlk` inspects POSIX range lock conflicts in `lockp$inode`. `Setlk` adds, updates, merges, splits, or removes POSIX byte-range locks through helper functions such as `loadLocks`, `updateLocks`, and `dumpLocks` from the broader package. `ListLocks` returns parsed POSIX and flock items for diagnostics.

## Control Flow

`Flock` builds an owner field from session ID and owner ID. Unlock removes that field and removes the lock key from the session's `locked$sid` set if it was the last owner. Read locks ignore locks by the same owner and conflict only with other write locks. Write locks require no other owners. Blocking locks retry on `EAGAIN` with short sleeps and return `EINTR` if the context is canceled.

`Getlk` reads all POSIX lock owners except the caller and returns the first overlapping conflicting lock when either requested or existing lock is write. `Setlk` unlocks by updating the caller's serialized lock list and deleting the owner field if empty. For read/write locks, it checks other owners for overlapping write conflicts, updates the caller's lock list, writes it back, and records the lock key in `locked$sid`. All mutations go through `redisMeta.txn` and can emit changelog records.

## State and Persistence Behavior

Flock state is persisted as `lockf$inode` hash fields `sid_owner -> "R"` or `"W"`. POSIX locks are persisted as `lockp$inode` hash fields `sid_owner -> serialized plock records`. The current session's `locked$sid` set references lock keys so stale session cleanup can release them. Lock state is metadata-only and does not alter inode attrs.

## Dependencies and Integration Points

The file depends on Redis transactions from `redis.go`, owner key formatting from `redisMeta.ownerKey`, lock serialization helpers, lock constants such as `F_RDLCK`, `F_WRLCK`, and `F_UNLCK`, and stale session cleanup in `doCleanStaleSession`. `ListLocks` integrates with user-facing lock inspection.

## Risks and Edge Cases

Blocking waits are polling-based and not fair. Unlock cleanup checks the current hash key count and may leave session lock references behind if concurrent owners change between read and transaction retry. PID reporting in `Getlk` is only meaningful for the local session; remote sessions return PID zero. Correct stale-session cleanup depends on every lock acquisition adding the lock key to `locked$sid`, which read flock currently does not do when only `HSet` is issued for read locks. Range lock correctness depends on shared helper behavior for merging and splitting lock intervals.

## Test Signals

Tests should cover shared flock compatibility, exclusive flock exclusion, self-owner replacement, blocking cancellation, stale-session lock cleanup, POSIX overlap conflicts, unlock splitting/merging, `Getlk` PID behavior for local and remote owners, and `ListLocks` parsing. Failure tests should inject transaction retries and Redis errors during lock mutation.
