# sources/distributed-fs/openafs/src/util/pthread_glock.h

Purpose: Declares the global recursive lock abstraction and no-op fallbacks for non-pthread or kernel builds.

Important APIs and types: Defines `pthread_recursive_mutex_t` with underlying `pthread_mutex_t`, owner, locked flag, and recursion count. Declares/imports `grmutex`, `pthread_recursive_mutex_lock()`, and `pthread_recursive_mutex_unlock()`. Defines `LOCK_GLOBAL_MUTEX` and `UNLOCK_GLOBAL_MUTEX` using `opr_Verify()`.

Control flow and state: Header-only macro layer. Under non-pthread or kernel builds the lock/unlock macros expand to nothing.

Dependencies and integration: Includes pthread and `afs/opr.h` for user-space pthread builds. Windows DLL import/export is controlled by `AFS_GRMUTEX_DECLSPEC`.

Risks and test signals: Macro no-op behavior means callers must not assume locking in non-pthread builds. The exported symbol contract differs on Windows due to declspec. Compile coverage and converted old-code behavior are the main signals.
