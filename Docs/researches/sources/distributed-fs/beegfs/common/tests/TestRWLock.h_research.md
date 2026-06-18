<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestRWLock.h -->
## sources/distributed-fs/beegfs/common/tests/TestRWLock.h

**Purpose:** Defines the `TestRWLock` fixture and nested `TestLockThread` worker used by the disabled RW lock stress tests.

**Important APIs/types/functions:** Test constants for thread counts, delays, sleeps, and timeouts; fixture helper declarations; nested `TestLockThread` constructors, `init`, `copy`, state getters, and `run`.

**Control flow:** `TestLockThread::run` sleeps for a configured start delay, attempts a read or write lock using either blocking or try-lock API, timestamps successful lock acquisition, sleeps while holding the lock, then timestamps and unlocks if it acquired the lock. The fixture uses getters to analyze ordering and runtime.

**State and persistence behavior:** Per-thread in-memory fields track lock pointer, sleep/delay, read/write mode, try mode, success flags, and timestamps. No persistence.

**Dependencies and integration points:** Depends on `Condition`, `RWLock`, `PThread`, `Time`, GoogleTest, and `unistd`. It is tightly coupled to `TestRWLock.cpp`.

**Risks:** `getSleepTimeMS` returns `bool` despite `sleepTimeMS` being `int`, truncating values for runtime analysis; this looks like a bug that can weaken `checkRandomRuntime`. Worker state is unsynchronized after join, which is acceptable if only read post-join. Long constants make tests expensive.

**Test signals:** Supports disabled stress tests; fixing the return type would make runtime validation meaningful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestRWLock.h -->
