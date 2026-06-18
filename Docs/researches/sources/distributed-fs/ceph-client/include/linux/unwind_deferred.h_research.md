<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_deferred.h -->
# sources/distributed-fs/ceph-client/include/linux/unwind_deferred.h

Purpose: declares deferred user-space stack unwinding hooks and per-task cleanup/reset helpers for builds with `CONFIG_UNWIND_USER`.

Important APIs and types: mask bits `UNWIND_PENDING` and `UNWIND_USED` track whether unwinding has been requested or used. Enabled-build APIs initialize/free per-task unwind state, perform faultable user unwinding, initialize/request/cancel deferred work, and handle task exit. `unwind_reset_info()` clears per-task unwind IDs and cached stack entries after a kernel entry if no pending task work remains. Disabled builds provide no-op or `-ENOSYS` stubs.

Control flow: task setup initializes unwind info; tracing/profiling code requests deferred unwind work; task_work later performs unwinding and invokes the callback. On return-to-user boundaries, `unwind_reset_info()` atomically clears used state unless another pending unwind is queued.

State and persistence: state lives in `current->unwind_info`: atomic mask, unique ID, optional cache, and task_work. It is per-task, transient, and reset across kernel exits or task teardown.

Dependencies and integration points: depends on `task_work`, `unwind_user.h`, `unwind_deferred_types.h`, atomics, and current task state. It integrates with tracing/profiling consumers that need user stack traces without faulting in unsafe contexts.

Risks and test signals: risks include races clearing `unwind_mask`, stale cached stack entries, callbacks after task exit, pending work surviving reset, and config stubs hiding missing feature handling. Test enabled/disabled builds, deferred request/cancel, task exit with pending unwind, signal-return paths, and concurrent trace requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_deferred.h -->
