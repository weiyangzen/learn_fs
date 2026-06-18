# sources/distributed-fs/eos/mgm/fuse-locks/LockTracker.cc

## Purpose
`LockTracker.cc` implements the in-memory POSIX byte-range lock tracker declared in `LockTracker.hh`. It models read and write locks for a single tracked object, answers `F_GETLK`-style conflict queries, applies non-blocking and short blocking `F_SETLK`/`F_SETLKW`-style requests, removes locks by pid or owner, and exposes owner-based lock listings for FUSE-related cleanup.

## Important APIs, Types, And Functions
Stream operators print `ByteRange` as half-open ranges and `Lock` with its pid. `LockSet::add` merges overlapping or touching ranges for the same pid. `LockSet::conflict` and `LockSet::getconflict` detect overlapping ranges held by different pids. `LockSet::remove(const Lock&)` subtracts a range from all matching-pid locks and may split one lock into two. `LockSet::remove(pid_t)` and `remove(owner)` drop all matching locks. `lslocks(owner)` returns pids held by an owner.

`LockTracker::getlk` checks if a requested read or write lock would be granted and mutates the supplied `struct flock` to `F_UNLCK` or to the blocking lock details. `setlk` delegates to `addLock` for non-sleeping calls, or retries for up to roughly 10 ms with 1 ms sleeps for sleeping calls. `addLock` holds the mutex, handles unlock requests, enforces read/write conflict rules, adds the new lock to `rlocks` or `wlocks`, and removes converted locks from the opposite set. `removelk`, `inuse`, `getrlks`, and `getwlks` are all mutex-protected.

## Control Flow
All public tracker operations take a `std::lock_guard<std::mutex>` either directly or through `addLock`, except `setlk` only locks per retry through `addLock`. Conflict logic follows POSIX-style compatibility: unlock always succeeds; read locks conflict only with write locks from other pids; write locks conflict with read or write locks from other pids. Same-pid overlaps are not conflicts and are coalesced, allowing lock upgrade/downgrade by adding the requested lock and subtracting the same range from the opposite lock set.

`getlk` builds a temporary `Lock` from `l_start` and `l_len`. If the request can lock, it sets `l_type` to `F_UNLCK`. If not, `canLock` has replaced `l_start`, `l_len`, `l_pid`, `l_whence`, and `l_type` with the conflicting lock's information. `setlk` returns `1` for success and `0` after the bounded retry loop gives up.

## State And Persistence
The implementation is entirely in-memory. `LockTracker` owns two `LockSet` instances, `rlocks` and `wlocks`, plus a mutex. No lock state is persisted to disk or shared hash. `LockSet` stores coalesced `Lock` objects in a vector, so lock identity is normalized by pid and merged ranges rather than preserving individual requests.

## Dependencies And Integration Points
The file depends on `fcntl.h` constants and `struct flock`, `unistd.h`/`pid_t`, C++ threads and chrono for retry sleep, and the EOS MGM namespace macros. It is intended to sit under MGM FUSE lock handling, where owners likely represent FUSE clients or sessions and pid cleanup is needed when clients disconnect.

## Risks
The blocking path is only a polling retry for about 10 ms, not a true condition-variable wait, so it may not match full `F_SETLKW` expectations under contention. `Lock::minus` recreates split locks without preserving `owner`, so partial unlocks can drop owner metadata for surviving ranges; owner-based cleanup/listing can then miss those ranges. `LockSet::add` merges same-pid locks regardless of owner, so different owners using the same pid namespace can be collapsed. Return values use `1` and `0` rather than errno-rich errors, so callers must map failures carefully.

## Test Signals
Strong tests should cover overlapping, touching, disjoint, zero-length, and EOF ranges. Add tests for read/read compatibility, read/write conflicts, same-pid upgrades and downgrades, unlock splitting into two ranges, pid cleanup, owner cleanup after partial unlocks, `getlk` conflict field mutation, and bounded sleeping behavior. Threaded tests can check that concurrent `setlk` and `removelk` do not corrupt lock vectors.
