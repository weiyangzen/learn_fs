<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.h

Purpose: Declares the base Windows OSI mutex and read/write lock ABI used by the client-side OSI layer. It is the public contract for lock objects, lock-order validation references, core lock operations, sleep-while-unlocking helpers, initialization, finalization, conversion, and assertion macros.

Important APIs, types, and functions: `osi_mutex_t` represents either a built-in exclusive mutex (`type == 0`) or a dynamically dispatched mutex using `d.privateDatap`; its state includes `flags`, owner `tid`, waiter count, hierarchy `level`, and a turnstile. `osi_rwlock_t` tracks exclusive flag, reader count, waiter count, writer/read owner thread ids, hierarchy level, and either private data or turnstile. `osi_lock_ref_t` records per-thread lock-order references and uses `OSI_LOCK_MUTEX` / `OSI_LOCK_RW`. The header exports `lock_ObtainRead`, `lock_ObtainWrite`, `lock_ReleaseRead`, `lock_ReleaseWrite`, `lock_ObtainMutex`, `lock_ReleaseMutex`, try-lock calls, `osi_SleepR/W/M`, generic `osi_Sleep` / `osi_Wakeup`, lock finalizers, `lock_InitializeMutex`, `lock_InitializeRWLock`, conversion calls, state query calls, `osi_BaseInit`, and `osi_SetLockOrderValidation`.

Control flow and state: Callers initialize OSI once, initialize each lock with a name and hierarchy level, then use obtain/release operations. For type-zero locks the implementation uses critical sections, turnstiles, flags, waiter counts, and reader counts; for nonzero lock types the implementation dispatches through `osi_lockOps`. The assertion macros query state and owner thread id to validate expected lock ownership.

Persistence and dependencies: No persistent storage is declared here. The state is in caller-owned lock structs and in global arrays such as `osi_baseAtomicCS`. Dependencies are `windows.h`-style `DWORD`, `CRITICAL_SECTION`, `LONG_PTR`, `osi_turnstile_t`, `osi_queue_t`, `thrd_Current`, and `osi_assertx`, so this header is tightly coupled to `osisleep.h`, `osiqueue.h`, `osiltype.h`, and the aggregate `osi.h`.

Integration points: This is the central lock API consumed by OSI tests (`perf.c`, `trylock.c`), the sleep package, the stats lock type (`osistatl.c`), and higher client code using `osi.h`. Dynamic lock types such as `stat` must preserve the field layout assumptions documented here.

Risks: The lock structs expose internal fields, so consumers can corrupt invariants if they mutate them directly. `OSI_RWLOCK_THREADS` is a fixed-size thread-id history and can be incomplete for many readers. The assertion macros depend on accurate owner tracking, which is debug-oriented and may be partial. Cross-header type ordering must remain correct because the header names types declared elsewhere.

Test signals: Useful tests include basic lock obtain/release, reader/writer exclusion, try-lock behavior, sleep-while-unlocked behavior, dynamic lock type dispatch, owner assertion failures, and lock-order validation under nested mutex/rwlock use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.h -->
