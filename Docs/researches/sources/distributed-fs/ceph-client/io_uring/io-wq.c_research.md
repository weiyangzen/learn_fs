# sources/distributed-fs/ceph-client/io_uring/io-wq.c

## Purpose
`io-wq.c` implements io_uring’s asynchronous worker pool. It creates per-task worker pools, separates bounded and unbounded work, serializes hashed work, handles cancellation, CPU hotplug/affinity, idle exit, and orderly teardown.

## Important APIs, Types, And Functions
- `struct io_wq` stores shared hash state, worker refs, CPU hotplug node, owner task, bounded/unbounded accounts, hash wait entry, hash tails, and CPU mask.
- `struct io_worker` tracks each worker task, refcount, current work, free/all list nodes, creation retry state, and exit state.
- `struct io_wq_acct` tracks per-class worker limits, running count, free/all lists, work list, locks, and stalled flag.
- Public APIs include `io_wq_create`, `io_wq_enqueue`, `io_wq_hash_work`, `io_wq_cancel_cb`, `io_wq_exit_start`, `io_wq_put_and_exit`, `io_wq_set_exit_on_idle`, `io_wq_cpu_affinity`, `io_wq_max_workers`, and worker scheduler hooks.

## Control Flow
`io_wq_create()` initializes the pool, refs shared hash state, copies the owner task’s cpuset mask, sets bounded/unbounded worker limits, and registers CPU hotplug state. `io_wq_enqueue()` inserts work into the appropriate account queue, preserving hash chains, wakes an idle worker, or creates a worker if concurrency/running-state requires it. If the pool is exiting or the work is pre-canceled, it runs cancellation immediately.

Worker threads run `io_wq_worker()`: they repeatedly acquire runnable work, mark themselves busy, submit work (including linked chains), free completed work, clear hash bits and wake stalled workers, then go idle with a timeout. Idle workers can exit after timeout, affinity mismatch, or exit-on-idle. Worker creation can occur immediately, via task_work, or delayed retry after temporary thread creation errors.

Cancellation first removes pending work from account queues, then marks running workers’ `cur_work` with cancel and signals worker tasks. Teardown sets exit, cancels pending worker-creation task_work, wakes workers, waits for `worker_done`, removes CPU hotplug state, cancels remaining pending work, drops hash/cpumask/task refs, and frees the pool.

## State And Persistence
Persistent pool state includes worker lists, free lists, account work queues, `nr_workers`, `nr_running`, shared hash map/wait queue, hash-tail array, CPU mask, and exit bits. Each worker stores `cur_work` under its own raw spinlock so cancellation can find running work. Hashed work uses upper work-flag bits and shared `hash->map` to prevent concurrent execution for the same key.

## Dependencies And Integration Points
The file depends on io_uring work submission/free callbacks (`io_wq_submit_work`, `io_wq_free_work`), task_work, PF_IO_WORKER scheduler hooks, cpuset/cpuhotplug, RCU nulls lists, raw spinlocks, delayed work, task limits, and generic cancellation via `io_wq_cancel_cb()`. `cancel.c`, eventfd async policy, and worker sleep/running hooks consume this interface.

## Risks And Edge Cases
This is a high-concurrency state machine. Risks include worker creation races with exit, losing work between pending queue and `cur_work`, hash stalls not waking, refcount imbalance during task_work cancellation, and teardown waits under heavy long-running work. The code uses worker refs, `create_state`, `worker_refs`, RCU lists, and hash wait queues to manage these hazards. Unbounded worker limits are clamped by `RLIMIT_NPROC`.

## Test Signals
Signals include io_uring async operation stress, hashed write serialization tests, cancellation of pending and running work, task exit/exec teardown, CPU hotplug affinity tests, worker max update tests, exit-on-idle behavior, and lockdep/KCSAN/KASAN under high concurrency.
