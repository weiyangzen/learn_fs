# sources/distributed-fs/ceph-client/include/linux/semaphore.h

Purpose: `semaphore.h` declares the classic sleeping semaphore primitive. It provides initialization macros, dynamic init, blocking acquire variants, trylock/timeout, release, and optional last-holder tracking for hung task diagnostics.

Important APIs/types/functions: `struct semaphore` contains a raw spinlock, count, first waiter pointer, and optional `last_holder`. Macros include `__SEMAPHORE_INITIALIZER()` and `DEFINE_SEMAPHORE()`. APIs are `sema_init()`, `down()`, `down_interruptible()`, `down_killable()`, `down_trylock()`, `down_timeout()`, `up()`, and `sem_last_holder()`.

Control flow: `down*()` decrements count or queues the caller on the semaphore wait list and sleeps according to interruptibility/timeout mode. `up()` increments count or wakes a waiter. `down_trylock()` and `up()` are documented as safe from interrupt context, unlike blocking `down()` variants.

State and persistence behavior: Semaphore state is entirely in the `struct semaphore`: count, waiters, lock, and optional last holder. It persists for the object lifetime and is initialized statically or by `sema_init()`.

Dependencies and integration points: It depends on raw spinlocks, lockdep, wait-list implementation in `kernel/locking/semaphore.c`, and hung-task diagnostics. It integrates with legacy synchronization sites where ownership tracking is not required.

Risks: Semaphores have no owner, so they are easier to misuse than mutexes for mutual exclusion. Blocking variants must not run in atomic context. Direct member access is discouraged because waiter internals and diagnostics may change.

Test signals: Static and dynamic initialization, blocking/wakeup ordering, interruptible and killable signal handling, timeout behavior, trylock from interrupt context, hung-task last-holder reporting, and lockdep class initialization.
