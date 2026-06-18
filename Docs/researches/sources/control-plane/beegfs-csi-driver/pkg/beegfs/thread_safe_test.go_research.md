# sources/control-plane/beegfs-csi-driver/pkg/beegfs/thread_safe_test.go

Purpose: Tests concurrency behavior of `threadSafeStringLock` and `threadSafeStatusMap`.

Important APIs/types/functions: `TestThreadSafeStringLock`, `TestThreadSafeStatusMapNoContention`, and `TestThreadSafeStatusMapContention`.

Control flow: The string-lock test launches several goroutines per lock string after random sleeps and expects exactly one success per string until release, then verifies relocking after release. The status-map no-contention test checks empty reads, writes, and reads. The contention test manually holds the map mutex, starts read and write goroutines, verifies neither completes while the lock is held, releases the lock, and expects completion.

State and persistence: Uses in-memory maps and goroutines only. Randomized sleep introduces scheduling variation to exercise contention.

Dependencies and integration points: Directly validates synchronization primitives used by `controllerServer` for per-volume concurrency and idempotent status memory.

Risks: The contention test's select/default plus elapsed-time check does not actually loop until timeout, so under unlucky scheduling it can miss late completions or fail to wait as intended. Random sleeps make test timing nondeterministic, though bounded.

Test signals: Confirms the intended invariant that only one goroutine can hold a given volume lock and that reads/writes block under the mutex.
