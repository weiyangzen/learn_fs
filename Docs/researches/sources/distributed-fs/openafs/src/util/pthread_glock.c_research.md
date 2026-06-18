# sources/distributed-fs/openafs/src/util/pthread_glock.c

Purpose: Implements a process-global recursive mutex used to port older LWP-style code to pthreads.

Important APIs and state: Defines global `pthread_recursive_mutex_t grmutex` under pthread builds. Implements `pthread_recursive_mutex_lock()` and `pthread_recursive_mutex_unlock()`. Static `pthread_once_t glock_init_once` initializes `grmutex` lazily.

Control flow: Locking initializes the global lock on first use. If the mutex is already locked by the current thread, it increments `times_inside` and returns. Otherwise it blocks on the underlying pthread mutex and records owner/locked/count state. Unlocking decrements recursion count for the owning thread and releases the underlying mutex when the count reaches zero.

Dependencies and integration: Includes `afs/pthread_glock.h`, pthreads, roken, and OpenAFS platform config. Consumers use `LOCK_GLOBAL_MUTEX` and `UNLOCK_GLOBAL_MUTEX` macros.

Risks and test signals: The implementation is a custom recursive mutex rather than using pthread recursive attributes; owner/locked/count fields are volatile but not independently synchronized outside the underlying mutex, making correctness dependent on simple usage patterns. Unlock by a non-owner returns `-1`. Tests are indirect via pthread builds of converted code.
