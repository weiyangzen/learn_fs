# sources/distributed-fs/ceph-client/include/linux/closure.h

Purpose: This header defines the bcache-style closure abstraction: a reference-counted asynchronous control-flow and wait primitive for operations that need to wait on multiple in-flight tasks and then continue synchronously or on a workqueue.

Important APIs/types/functions: Types include `struct closure_waitlist`, `enum closure_state`, `struct closure`, `struct closure_syncer`, and `closure_fn`. APIs and macros include `closure_get`, `closure_get_not_zero`, `closure_put`, `closure_sub`, `closure_wait`, `closure_wake_up`, `closure_sync`, `closure_sync_timeout`, `closure_init`, `closure_init_stack`, `closure_init_stack_release`, `continue_at`, `continue_at_nobarrier`, `closure_return`, `closure_return_sync`, `closure_return_with_destructor`, `closure_call`, `closure_wait_event`, `closure_wait_event_timeout`, `CLOSURE_CALLBACK`, and `closure_type`. Debug support adds magic values, IP tracking, and create/destroy hooks under `CONFIG_DEBUG_CLOSURES`.

Control flow: A closure starts with a running reference. Users add references for in-flight work with `closure_get` and drop them with `closure_put`. `closure_sync` sleeps until only the running reference remains. `continue_at` sets the next function/workqueue and drops the running reference so the next closure function runs once outstanding references reach zero; callers are expected to return immediately. Wait-list helpers park closures until `closure_wake_up`.

State and persistence behavior: State is held in `atomic_t remaining`, state bits for destructor/waiting/running, parent pointer, next function/workqueue, linked-list node, optional work_struct overlay, debug metadata, and whether `closure_get` happened. Parent closures hold a lifetime reference until child completion. Stack closures use special initialization.

Dependencies and integration points: It includes llist, sched, task stack, and workqueue support and is used by bcache-style asynchronous storage code. It integrates with workqueues, wait lists, atomics, memory barriers, jiffies timeouts, and debugfs through `bcache_debug`.

Risks: The comments emphasize strict ownership: after `continue_at`, the caller no longer owns the closure and must return. Missing `closure_put`, transferring references incorrectly, reusing stack closures after return, or waiting without the required wakeup can deadlock or use-after-free. The 32-bit `remaining` bit layout mixes count and state bits, so arithmetic must use the provided helpers.

Test signals: Concurrency stress with multiple completions, debug closure assertions, timeout paths, parent/child closure completion, wait-list wakeups, workqueue vs direct callback execution, and KCSAN/KASAN/KMSAN runs are the best validation signals.
