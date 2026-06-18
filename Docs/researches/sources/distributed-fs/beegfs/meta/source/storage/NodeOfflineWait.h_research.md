## sources/distributed-fs/beegfs/meta/source/storage/NodeOfflineWait.h

Purpose: Implements a small timer gate used when a metadata node must delay reporting state so clients and mgmtd can observe it as offline before resync-sensitive work resumes.

Important APIs/types/functions: `NodeOfflineWait(Config*)` derives `waitTimeoutMS` from `OfflineWaitTimeoutTk<Config>`. `startTimer()` marks the wait active and resets `timer`. `hasTimeout()` returns whether the wait is still active, clears `active` once elapsed time reaches the configured timeout, and logs remaining seconds while active.

Control flow: Reads `active` under a read lock, then upgrades by taking a write lock to check elapsed time and possibly clear `active`. Logging happens outside the critical state update but after the write lock is released.

State and persistence: Maintains only in-memory state: `RWLock`, immutable timeout, `Time timer`, and `active`. It intentionally delays state reporting rather than persisting anything.

Dependencies and integration: Uses BeeGFS locking (`SafeRWLock`), timing, offline timeout calculation, `Config`, and `LogContext`. It integrates with metadata primary/buddy resync startup logic.

Risks and test signals: `hasTimeout()` is semantically inverted: true means the wait is still active, not expired. Race tests should cover concurrent `startTimer()` and `hasTimeout()` calls, timeout boundary behavior, and log throttling concerns if polled frequently.
