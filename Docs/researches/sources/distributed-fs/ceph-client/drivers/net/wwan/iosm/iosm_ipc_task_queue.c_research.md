# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_task_queue.c

Purpose: implements a small serialized tasklet-backed queue for IOSM IPC callbacks that need to be invoked outside interrupt or caller context while preserving ordering.

Important APIs/functions: `ipc_task_init()` allocates and initializes the tasklet and queue lock. `ipc_task_queue_send_task()` optionally copies a message payload with `kmemdup(..., GFP_ATOMIC)`, queues a function call, and optionally waits for completion. `ipc_task_queue_add_task()` is the core producer path, filling one `ipc_task_queue_args` slot under `q_lock`, issuing `smp_wmb()`, advancing `q_wpos`, and scheduling the tasklet. `ipc_task_queue_handler()` drains queued entries, calls the function pointer, completes synchronous requests, frees copied payloads, and clears the slot. `ipc_task_deinit()` kills the tasklet and completes/frees queued-but-unprocessed entries through `ipc_task_queue_cleanup()`.

Control flow and state: state is a fixed-size circular queue with volatile read/write positions and per-slot function/message/completion data. Synchronous calls use a stack completion object and read the response from the same queued slot after completion.

Dependencies and integration points: integrates with `struct iosm_imem` and its `ipc_task` member, kernel tasklets, spinlocks, completions, atomic GFP allocations, and IOSM callback functions with signature `int (*)(struct iosm_imem *, int, void *, size_t)`.

Risks and test signals: queue full paths, synchronous wait lifetime, copied message ownership, and deinit races are the main risks. Tests should stress task submission from interrupt-like context, mixed sync/async calls, queue saturation at 256 entries, and teardown while requests are pending.
