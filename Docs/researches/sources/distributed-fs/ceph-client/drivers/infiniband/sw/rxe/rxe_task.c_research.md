# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_task.c

## Purpose

`rxe_task.c` provides RXE's workqueue-backed task scheduler for QP send and receive processing. It coalesces schedules, bounds CPU use, drains tasks for reset/cleanup, and protects QP lifetime.

## Important APIs, Types, and Functions

Core APIs are `rxe_alloc_wq()`, `rxe_destroy_wq()`, `rxe_init_task()`, `rxe_sched_task()`, `rxe_disable_task()`, `rxe_enable_task()`, and `rxe_cleanup_task()`. Internal `do_task()` runs callbacks until idle or iteration limit.

## Control Flow

Scheduling moves IDLE to BUSY, takes a QP reference, and queues work. Scheduling while BUSY marks ARMED so the worker performs another pass. `do_task()` repeatedly calls the callback while it returns zero, reschedules after `RXE_MAX_ITERATIONS`, honors draining states, updates counters, and releases the QP reference.

## State and Persistence Behavior

Global state is `rxe_wq`. Per-task state includes work item, state enum, spinlock, QP pointer, callback, return value, and schedule/done counters. Pending/running work holds an extra QP reference.

## Dependencies and Integration Points

It depends on Linux workqueues, spinlocks, RXE QP references, and `RXE_MAX_ITERATIONS`. QP setup, reset, cleanup, requester, completer, and responder paths all depend on it.

## Risks and Edge Cases

Lost wakeups, running after cleanup, leaked QP references, and unfair long-running tasks are the main risks. Cleanup/disable wait with `cond_resched()` and require process context.

## Test Signals

Stress concurrent scheduling, schedule while busy, QP reset during traffic, cleanup with pending work, max-iteration rescheduling, and module unload after task churn.
