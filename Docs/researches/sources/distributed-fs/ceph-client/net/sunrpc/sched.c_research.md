# sources/distributed-fs/ceph-client/net/sunrpc/sched.c

## Purpose
`sched.c` implements SUNRPC task scheduling for synchronous and asynchronous RPC calls. It owns RPC wait queues, timeout handling, task wakeups, the task finite-state-machine executor, task and buffer allocation pools, and the `rpciod`/`xprtiod` workqueues.

## Important APIs, Types, And Functions
Important APIs include `rpc_task_gfp_mask()`, `rpc_task_timeout()`, waitqueue init/destroy, `rpc_sleep_on*()`, `rpc_wake_up*()`, `rpc_delay()`, `rpc_exit()`, `rpc_execute()`, `rpc_malloc()`, `rpc_free()`, `rpc_new_task()`, `rpc_put_task()`, `rpc_put_task_async()`, `rpciod_up()`, `rpciod_down()`, `rpc_init_mempool()`, and `rpc_destroy_mempool()`. Central types are `rpc_task`, `rpc_wait_queue`, delayed timer lists, `rpc_buffer`, and `rpc_task_setup`.

## Control Flow
Tasks are initialized with callback ops, credentials, owner, workqueue, optional client/transport references, and an initial prepare action. `rpc_execute()` marks a task active and runnable; synchronous tasks run the FSM in the caller while async tasks are queued to `rpciod`. `__rpc_execute()` repeatedly runs `tk_action` or pending callbacks until the task sleeps or completes. Sleeping puts a task on a protected waitqueue, optionally with a timeout. Waking removes it from the queue and either queues async work or wakes synchronous waiters. Completion releases xprt slots, credentials, clients, calldata, and finally frees or asynchronously frees dynamic task memory.

## State And Persistence
Global state includes the delay queue, task slab, buffer slab, task and buffer mempools, `rpciod_workqueue`, and `xprtiod_workqueue`. Per-task state includes runstate bits, refcount, RPC status, action/callback, timeout, waitqueue pointer, statistics timestamps, retry counters, transport, client, credentials, request pointer, and calldata. Wait queues keep priority buckets, fairness counters, queue length, and delayed timer work.

## Dependencies And Integration Points
The scheduler integrates with RPC clients, transports, credentials, I/O statistics, tracepoints, Linux workqueues, wait-bit APIs, memalloc flags, freezer-aware waits, mempools, and module lifetime. Transport code wakes tasks when slots, connections, or replies are available; client code provides callback operations and count-stat hooks.

## Risks And Edge Cases
Correctness depends on runstate ordering between `RPC_TASK_RUNNING` and `RPC_TASK_QUEUED`; comments call out barriers that prevent lockless executor loops or missed wakeups. Async task memory freeing is deferred through workqueue context to avoid false work item dependency loops. Synchronous tasks receiving signals make one more FSM pass so callbacks can clean up. `PF_MEMALLOC` and `memalloc_nofs` are used for swapper or reclaim-sensitive paths. Mempools protect small task/buffer allocation, but callers must handle `-ENOMEM` without blocking rpciod unsafely.

## Test Signals
Useful coverage includes synchronous and async RPC task lifecycle, waitqueue FIFO and priority fairness, timeout expiry, signal cancellation, delayed tasks, rpcbind/autobind waiters, mempool fallback under allocation failure, task refcount and callback release ordering, workqueue teardown, tracepoint events, and lockdep/KCSAN checks for queued/running state transitions.
