# sources/distributed-fs/lizardfs/src/master/flocks_unittest.cc

Purpose: tests BSD-style whole-file lock behavior using the shared `FileLocks` implementation over range `[0,1)`.

Important APIs/types/functions: helper functions wrap `exclusiveLock()`, `sharedLock()`, `unlock()`, `gatherCandidates()`, and `apply()`; `SharedAndExclusive` exercises shared stacking, owner overwrite, queued exclusive locks, and queued shared locks; `Nonblocking` verifies nonblocking failures are not enqueued.

Control flow: tests apply locks, gather pending candidates after each potentially releasing operation, and flush candidates back through `apply()` to mimic server lock-wakeup behavior.

State and persistence behavior: uses in-memory `FileLocks`; no persistence is tested here.

Dependencies/integration: depends on GoogleTest and `master/locks.h`. It signals expected behavior for client flock handling layered on `FileLocks`.

Risks and test signals: tests focus on one inode and a one-byte interval, so they do not cover range splitting or serialization. They are strong signals for pending-queue semantics and nonblocking behavior.
