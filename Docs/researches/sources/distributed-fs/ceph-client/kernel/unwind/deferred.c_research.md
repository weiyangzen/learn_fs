<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/deferred.c -->
# sources/distributed-fs/ceph-client/kernel/unwind/deferred.c

Purpose: provides deferred user-space stack unwinding for callers that request a user stack trace from contexts where faulting user memory is not safe. Requests are queued on task work and completed when the task reaches faultable exit-to-user context.

Important APIs and state: `unwind_deferred_init()` registers a callback work item and assigns a bit. `unwind_deferred_request()` schedules a trace for current. `unwind_deferred_cancel()` removes a callback and clears its bit from all tasks. `unwind_user_faultable()` performs or reuses the cached unwind. Task lifecycle hooks are `unwind_task_init()`, `unwind_task_free()`, and `unwind_deferred_task_exit()`. Per-task state lives in `current->unwind_info`; global callback state uses `callback_mutex`, `callbacks`, `unwind_mask`, and `unwind_srcu`.

Control flow: a request validates that current is a userspace task at a user-mode register frame, assigns a per-entry cookie with IRQs disabled, atomically sets the callback bit plus `UNWIND_PENDING`, and adds task work. On task work, `process_unwind_deferred()` clears pending, unwinds once into a per-task cache if needed, then walks registered callbacks under SRCU and invokes matching callbacks with the trace and cookie.

State and persistence: the cache survives within a task until freed or cleared on user return by users of `UNWIND_USED`. Callback bits remain reserved until cancellation. Cookies combine CPU and per-CPU context counters.

Dependencies and integration: depends on task_work, SRCU, user unwind core, task stack registers, mm presence, NMI-safe cmpxchg support, and task iteration for cancellation.

Risks: NMI use is architecture-gated. Atomic bit state must not lose callbacks. Cancellation must synchronize before clearing bits globally. Test signals include duplicate requests returning the same cookie, callback cancellation while tasks hold bits, NMI request behavior on unsupported architectures, task exit with pending unwind, and cache reuse across multiple callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/deferred.c -->
