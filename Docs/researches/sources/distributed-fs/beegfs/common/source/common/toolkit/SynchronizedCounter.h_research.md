<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/SynchronizedCounter.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/SynchronizedCounter.h

**Purpose:** Provides a mutex/condition-protected unsigned counter that threads can wait on until it reaches an exact value.

**Important APIs/types/functions:** Constructor initializes count to zero. `waitForCount`, `timedWaitForCount`, `incCount`, and `resetUnsynced`.

**Control flow:** Wait methods lock the mutex and wait on the condition. `waitForCount` loops until exact equality. `timedWaitForCount` waits once and returns false on timeout or when count remains below the desired value. `incCount` increments and broadcasts.

**State and persistence behavior:** In-memory `count`, `Mutex`, and `Condition` only. No persistence.

**Dependencies and integration points:** Uses BeeGFS threading primitives and `std::lock_guard`. Useful for tests or coordination barriers inside common code.

**Risks:** `resetUnsynced` does not lock or broadcast and is only safe under external synchronization. Exact-equality waits can block forever if `count` jumps past `waitCount`; timed wait partially handles count below but returns true if count is greater. Overflow is not guarded.

**Test signals:** No direct tests. Concurrency tests should cover exact match, overshoot, timeout, broadcast behavior, and safe reset usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/SynchronizedCounter.h -->
