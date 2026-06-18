## sources/distributed-fs/openafs/src/lwp/afs_lock.h

Purpose: Public userspace lock API for Vice/OpenAFS code, supporting read, write, shared, and boosted lock modes over either pthread condition variables or LWP event waits.

Important APIs and types: `struct Lock` contains wait state bits, exclusive lock bits, reader count, waiter count, and pthread mutex/condition variables when `AFS_PTHREAD_ENV` is enabled. Declares `Afs_Lock_Obtain`, release/wakeup helpers, `Lock_Init`, and `Lock_Destroy`. Macros implement `ObtainReadLock`, no-block variants, `ObtainWriteLock`, `ObtainSharedLock`, `BoostSharedLock`, `UnboostSharedLock`, release macros, `ConvertWriteToReadLock`, and lock state queries.

Control flow: Fast-path macros acquire the underlying mutex when applicable, check lock state inline, and call `Afs_Lock_Obtain` only when they must wait. Release macros clear state bits and call wakeup helpers when waiters exist.

State and persistence: Lock state is entirely in `struct Lock`. No persistence.

Dependencies and integration: Non-kernel only; explicitly errors under `KERNEL`. Uses opr mutex/cv wrappers in pthread builds and LWP wait/signal functions in non-pthread builds.

Risks: Counters and state fields are `unsigned char`, so extreme waiter/reader counts can overflow. Macro-heavy API evaluates its `lock` argument multiple times. Correctness depends on callers matching release mode to obtain mode. Shared-to-boost transitions are subtle.

Test signals: Reader concurrency, writer exclusion, shared lock behavior, boost/unboost, no-block paths, conversion write-to-read, waiter wake preferences, pthread and LWP builds, and overflow stress.
