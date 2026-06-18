# sources/distributed-fs/eos/unit_tests/mgm/LockTrackerTests.cc

## Purpose
Tests MGM FUSE byte-range lock tracking. It validates range overlap math, range subtraction, lock coalescing by pid, lock-set conflict detection, and POSIX-style read/write/unlock behavior through `flock` inputs.

## Important APIs, types, and functions
Coverage includes `ByteRange::overlap`, `overlapOrTouch`, `absorb`, `contains`, `minus`; `Lock::absorb`; `LockSet::add`, `remove`, `overlap`, `conflict`, `nlocks`; and `LockTracker::setlk`.

## Control flow
Byte-range tests enumerate touching, infinite-length, middle/start/end subtraction, and whole-range removal cases. Lock-set tests add overlapping locks from different pids, remove subranges, and verify conflicts. `LockTracker` tests model write lock acquisition, failed competing lock, unlock splitting, read-lock conversion, shared read locks, and write upgrade when only one reader remains.

## State and persistence
State is in-memory lock ranges keyed by owners/pids. No persistence is involved, but correctness affects live FUSE file locking semantics.

## Dependencies and integration points
Depends on Google Test, `mgm/fuse-locks/LockTracker.hh`, and POSIX `fcntl.h` lock constants.

## Risks and test signals
The test suite is strong for boundary arithmetic. Risks include integer overflow on large offsets, owner-string semantics, process death cleanup, and multithreaded access not covered by these single-threaded tests.
