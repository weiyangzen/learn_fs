# sources/distributed-fs/eos/mgm/fuse-locks/LockTracker.hh

## Purpose
`LockTracker.hh` declares and partly implements a small POSIX byte-range lock model for MGM FUSE locking. It defines the range arithmetic, lock identity, lock-set container, and thread-safe tracker API used by the implementation file.

## Important APIs, Types, And Functions
`Offset` is an alias for `off_t`. The helpers `isPointBetween` and `isPointBetweenOrTouching` implement half-open and inclusive boundary checks.

`ByteRange` stores a start offset and length. Its `end()` returns `start + len` except `len == -1`, which is treated as an infinite range ending at `numeric_limits<Offset>::max()`. `f_lock_len()` converts internal `-1` back to `0` for `struct flock` EOF semantics. `absorb` merges overlapping or touching ranges, `contains` tests full coverage, `minus` subtracts another range and returns zero, one, or two ranges, and `overlap`/`overlapOrTouch` implement conflict and merge checks.

`Lock` combines a `ByteRange`, `pid_t`, and optional owner string. Overlap, containment, absorption, and subtraction only apply to locks with the same pid. `LockSet` declares add, overlap, remove, conflict, count, and owner-list operations over coalesced locks. `LockTracker` exposes `getlk`, `setlk`, `removelk(pid)`, `removelk(owner)`, `inuse`, `getrlks`, and `getwlks`, with private `addLock` and `canLock` helpers plus separate read and write lock sets.

## Control Flow
The header establishes range behavior before tracker behavior. `ByteRange` constructor immediately verifies that a range overlaps itself; invalid ranges print to stderr and terminate the process. `minus` handles six cases: no overlap left, no overlap right, complete removal, removal of start, removal of end, and middle removal with two surviving ranges. `LockSet` is responsible for coalescing and splitting, while `LockTracker` is responsible for read/write compatibility and synchronization.

## State And Persistence
State is in-memory only. `ByteRange` state is two offsets, `Lock` state is a range/pid/owner triple, `LockSet` state is a vector of coalesced locks, and `LockTracker` state is a mutex plus read and write `LockSet`s. The header does not expose persistence hooks, serialization, or distributed coordination.

## Dependencies And Integration Points
The header depends on STL containers, mutex, `fcntl.h` for POSIX lock constants and `struct flock`, `common/Assert.hh`, and MGM namespace macros. It exposes ostream operators for diagnostics. The API is shaped around POSIX locks, but the implementation stores simplified normalized ranges rather than kernel lock objects.

## Risks
Fatal `exit(EXIT_FAILURE)` from `ByteRange` and `updateEnd` makes malformed lock input process-wide fatal instead of returning an error. Internal EOF is represented as `len == -1`, while POSIX uses `l_len == 0`; callers must normalize inputs before construction or EOF locks will be interpreted as zero-length locks. `start + len` can overflow for large positive ranges. Owner metadata is not part of `Lock` equality or same-pid merge decisions, so owner cleanup semantics are approximate. The API does not document whether pid values are globally unique across clients, which matters for FUSE multi-client behavior.

## Test Signals
Unit tests should target `ByteRange::minus`, `absorb`, `overlap`, and EOF conversion first, because tracker correctness depends on those primitives. Additional tests should exercise `Lock::minus` owner preservation expectations, lock coalescing order independence, and public `LockTracker` behavior under conflicting readers and writers.
