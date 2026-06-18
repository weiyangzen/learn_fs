<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_deferred_types.h -->
# sources/distributed-fs/ceph-client/include/linux/unwind_deferred_types.h

Purpose: defines the data structures used by deferred user-space unwinding.

Important APIs and types: `struct unwind_cache` stores completion state, entry count, and a flexible array of stack entries. `union unwind_task_id` combines CPU number and per-CPU counter into a nonzero 64-bit ID. `struct unwind_task_info` holds an atomic mask, cache pointer, task_work callback head, and current ID. `unwind_callback_t` is the deferred callback signature. `struct unwind_work` links queued work, stores the callback, and records a bit index.

Control flow: unwind users allocate or embed `unwind_work`, initialize it with a callback, queue requests that assign or reuse a task ID, and receive a stacktrace/cookie when deferred processing runs.

State and persistence: all state is per-task or per-work in memory. Cache entries are reusable within a task's kernel-entry window and are cleared by reset/exit paths.

Dependencies and integration points: depends on `types.h`, `atomic.h`, `list_head`, `callback_head`, and `struct unwind_stacktrace` from the generic unwind types. It is consumed by `unwind_deferred.h` and implementation code.

Risks and test signals: risks include flexible-array sizing mistakes, ID wrap or zero generation, list lifetime errors, cache reuse after free, and missing synchronization around the atomic mask. Test allocation sizes, repeated request IDs, cache reset, and task exit teardown under tracing load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_deferred_types.h -->
