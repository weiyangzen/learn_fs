# sources/distributed-fs/openafs/src/rx/DARWIN/rx_kmutex.h

Purpose: Darwin/macOS Rx kernel mutex/CV abstraction for older BSD locks and Darwin 8+ Mach lock primitives.

Important APIs/types/functions: Darwin 8+ `afs_kmutex_t` containing `meta`, `lock`, `waiters`, and `owner`; older `afs_kmutex_t` containing BSD `lock__bsd__` plus owner; macros `MUTEX_SETUP`, `MUTEX_FINISH`, `MUTEX_INIT`, `MUTEX_ENTER`, `MUTEX_TRYENTER`, `MUTEX_EXIT`, `MUTEX_ASSERT`, `CV_WAIT`, `CV_SIGNAL`, and `CV_BROADCAST`.

Control flow: Darwin 8+ uses a two-mutex scheme to emulate try-enter safely and track owners across `msleep(PDROP)`. `CV_WAIT` temporarily drops the AFS global lock, clears ownership, sleeps, restores global-lock state, then reacquires the Rx mutex.

State/persistence: tracks owner thread and waiter count per mutex; lock objects are allocated from `openafs_lck_grp`.

Dependencies/integration: Darwin kernel locks, sleep/wakeup, current thread/process APIs, and OpenAFS global lock.

Risks: waiter accounting is subtle and can deadlock or falsely fail try-enter; `owner` must be cleared before sleep to avoid kernel panic; older BSD-lock path has different semantics. Test signals are lock try-enter races, CV wait/wakeup, global-lock wait paths, and kext unload.
