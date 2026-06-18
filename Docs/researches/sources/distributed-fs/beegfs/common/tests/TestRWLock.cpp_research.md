<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestRWLock.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestRWLock.cpp

**Purpose:** Contains disabled GoogleTest scenarios for BeeGFS `RWLock` reader/writer locking, try-lock behavior, ordering, and runtime under concurrent randomized threads.

**Important APIs/types/functions:** Helper methods `sortThreadsInLockTimestamp`, `checkRandomRuntime`, `checkRandomExecutionOrder`, `checkRandomExecutionOrderReader`, and `checkRandomExecutionOrderWriter`. Disabled tests cover reader-on-reader, reader-on-writer, writer-on-reader, writer-on-writer, random readers/writers, try-read, try-write, and random try-lock cases.

**Control flow:** Tests create `RWLock`, start `TestLockThread` workers from the companion header, sleep before unlocking initial locks, join with timeouts, and assert whether locks should or should not have been acquired. Random tests sort threads by lock timestamp, verify writers do not overlap with prior readers/writers, allow overlapping readers, and compare runtime against minimum sequential/parallel expectations.

**State and persistence behavior:** In-memory concurrency state only. Uses `Time` timestamps and `Random` delays.

**Dependencies and integration points:** Depends on BeeGFS `RWLock`, `PThread`, `Time`, `Random`, `StringTk`, and GoogleTest. These are stress-style tests for low-level synchronization primitives.

**Risks:** All tests are disabled via `DISABLED_` macro, probably due to long runtime/flakiness. Timing assertions are sensitive to scheduler delays and coarse clock resolution. Helper sorting uses a simple bubble sort and copies thread result state, not live threads.

**Test signals:** Valuable manual/stress coverage when enabled, but not part of normal test runs unless disabled tests are explicitly requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestRWLock.cpp -->
