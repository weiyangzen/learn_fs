# sources/distributed-fs/orangefs/src/common/gen-locks/gen-win-locks.c

Purpose: Implements Win32 generic mutexes and a condition-variable emulation for OrangeFS, modeled after pthreads-win32 semantics.

Important APIs/functions: `gen_win_mutex_init/lock/unlock/trylock/destroy()` wrap Win32 mutex handles with lazy static-initializer support. `gen_win_cond_init/destroy/wait/timedwait/signal/broadcast()` manage a custom `gen_cond_t_` containing waiter counts, semaphores, an unblock mutex, and global linked-list membership. Internal helpers include `cond_check_need_init()`, `cond_timedwait()`, `cond_wait_cleanup()`, and `cond_unblock()`.

Control flow: Waiters increment `nWaitersBlocked`, release the caller mutex, wait on `semBlockQueue`, perform cleanup to adjust waiter counters, then reacquire the caller mutex. Signal/broadcast computes how many waiters to release under `mtxUnblockLock` and posts to the queue semaphore.

State/persistence: Maintains process-global critical sections for lazy initialization and condition-list locking, plus global condition-list head/tail. Mutex and condition objects own Win32 handles until destroyed.

Dependencies/integration: Selected by `gen-locks.h` on Windows. Uses Windows synchronization APIs, `_ftime_s()`, and errno translation via `SET_ERROR`.

Risks: Lazy initialization of global critical sections is itself racy before the lock exists. Several functions return positive errno values while mutex wrappers often return `-1` and set `errno`. `gen_win_thread_self()` returns a pseudo-handle from `GetCurrentThread()`, not a stable numeric ID. Destroy while waiters exist is complex and must be carefully tested.

Test signals: Windows tests should cover static initializer use, simultaneous lazy init, timed wait timeout, signal, broadcast, destroy-with-waiters, abandoned mutex behavior, and invalid handles.
