# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_taskq.c

## Scope

FreeBSD SPL taskq compatibility implementation. It maps illumos-style `taskq_t` APIs onto FreeBSD `taskqueue(9)`, with global system queues, delayed dispatch, cancellation by task id, synced taskqueue creation, wait/drain helpers, and thread-local taskq tracking.

## Main Interfaces

- Initializes `system_taskq` and `system_delay_taskq` at `SYSINIT`; destroys them at `SYSUNINIT`.
- Creates taskqueues via `taskq_create()`, `taskq_create_proc()`, and `taskq_create_synced()`.
- Dispatches normal and delayed work through `taskq_dispatch()` and `taskq_dispatch_delay()`.
- Supports explicit `taskq_ent_t` storage through `taskq_init_ent()`, `taskq_dispatch_ent()`, and `taskq_empty_ent()`.
- Supports cancellation and waiting through `taskq_cancel_id()`, `taskq_wait()`, `taskq_wait_id()`, and `taskq_wait_outstanding()`.
- Exposes membership/current-taskq helpers: `taskq_member()` and `taskq_of_curthread()`.

## State And Control Flow

A UMA zone stores dynamically allocated `taskq_ent_t` objects. Each dispatched task gets a nonzero `taskqid_t` from an atomic counter and is inserted into a global hash table protected by striped `sx` locks. `taskq_lookup()` acquires a refcounted handle so cancellation and wait paths can safely refer to entries while the task may concurrently run.

Normal tasks use `TASK_INIT`; delayed tasks use `TIMEOUT_TASK_INIT`. Both execute through `taskq_run()`, call the requested function, then remove themselves from the id hash and drop their final reference. Cancellation removes pending tasks manually because they will not run and self-free.

`taskq_create_synced()` dispatches one synchronization task per worker, waits for each worker to record its `curthread`, resumes them, drains the queue, and returns the worker-thread array to the caller.

## Dependencies

Depends on FreeBSD `taskqueue`, `uma`, `sx`, `tsd`, atomics/refcounts, SPL `kmem`, and FreeBSD FPU kernel-thread setup on supported architectures.

## Correctness Notes

The id hash/refcount scheme is the central lifetime mechanism; any new task type must follow the same lookup/free rules. `taskq_cancel_id()` returns `EBUSY` only when a task is running and the caller did not wait; otherwise it reports successful cancellation or `ENOENT`. The TSD init callback also enables kernel FPU context for taskq threads on x86/aarch64, which matters for OpenZFS checksum/compression/crypto work.
