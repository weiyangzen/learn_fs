# sources/distributed-fs/ceph-client/kernel/locking/semaphore.c

## Purpose
Implements generic counting semaphores. Unlike mutexes, semaphores allow multiple acquisitions, `up()` can be called by a different task or interrupt, and `down_trylock()` uses the historical inverted return convention.

## Important APIs, Types, and Functions
- Exports `down()`, `down_interruptible()`, `down_killable()`, `down_trylock()`, `down_timeout()`, `up()`, and `sem_last_holder()`.
- Internal waiters use `struct semaphore_waiter` with list link, task, and `up` flag.
- Slow paths are `__down()`, `__down_interruptible()`, `__down_killable()`, `__down_timeout()`, `__down_common()`, `___down_common()`, and `__up()`.

## Control Flow
All public operations take `sem->lock` with irqsave because trylock/up may run from interrupt context and callers historically use successful `down()` in such contexts. Fast down decrements `count` when positive. Contended down enqueues a stack waiter on the circular wait list, sets task state, drops the spinlock, schedules with optional timeout, and returns when `__up()` marks `waiter.up`. Interruptible and killable variants remove the waiter and return `-EINTR`; timeout returns `-ETIME`. `up()` increments count when no waiters exist or removes the first waiter, marks it up, and wakes it outside the spinlock.

## State and Persistence
`struct semaphore` stores raw spinlock, integer count, and `first_waiter`; optional hung-task `last_holder` records the last acquiring task. State is in-memory only.

## Dependencies and Integration Points
Depends on scheduler sleep APIs, raw spinlocks, wake queues, ftrace/trace lock events, hung-task blocker hooks, and exported semaphore API.

## Risks
Semaphore ownership is intentionally loose, so it cannot provide mutex-style owner debugging. The inverted `down_trylock()` return value is a migration hazard. Waiter lifetime is stack-based and protected by the spinlock plus the `up` flag protocol. `last_holder` is diagnostic only and can be approximate when `up()` comes from a non-holder.

## Test Signals
Semaphore selftests should cover count > 1, interruptible/killable wait interruption, timeout, `up()` from interrupt context, FIFO wake behavior, hung-task holder reporting, and conversion tests that catch inverted trylock handling.
