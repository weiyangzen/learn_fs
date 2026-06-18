<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.c

Purpose: Implements an OSI try-lock stress test with two threads acquiring a three-lock hierarchy in opposite directions to validate nonblocking acquisition, fallback waits, and deadlock avoidance.

Important APIs, types, and functions: Global locks are `trylock_first` rwlock, `trylock_second` mutex, and `trylock_third` rwlock. `main_Neon` acquires read/mutex/write in hierarchy order and releases them. `main_Salmon` attempts to acquire read/mutex/write in reverse order using `lock_TryRead`, `lock_TryMutex`, and `lock_TryWrite`; on failure it releases held locks, waits for the contended lock, increments `interestingEvents`, and retries. `main_TryLockTest` initializes OSI and locks, starts both threads, periodically updates `main_screenText`, waits for `done == 2`, finalizes locks, and closes handles.

Control flow and state: `main_Neon` represents normal lock ordering. `main_Salmon` deliberately goes against hierarchy but uses try-lock/fallback to avoid deadlock. `done` is incremented under the mutex, while progress counters are unsynchronized and only used for display.

Persistence and dependencies: No persistence. Depends on Win32 threads/sleep, test UI globals, `trylock.h`, and OSI lock APIs.

Integration points: Invoked by the OSI test GUI/menu to exercise lock behavior and lock-order validation scenarios.

Risks: Progress counters are read without synchronization. If thread creation fails after the first thread starts, cleanup is incomplete. The test depends on scheduler timing (`Sleep(0)`, `Sleep(1000)`) and may be nondeterministic. The thematic function names do not explain lock roles, so maintainers must inspect code.

Test signals: The key signal is completing both threads without deadlock while showing nonzero or plausible `interestingEvents`. Run under base and stat lock types and with lock-order validation enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.c -->
