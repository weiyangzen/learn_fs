# sources/distributed-fs/ceph-client/include/linux/io_uring.h

Purpose: This header exposes small task and file lifecycle hooks for the io_uring core to the rest of the kernel.

Important APIs, types, and functions: With `CONFIG_IO_URING`, it declares `__io_uring_cancel`, `__io_uring_free`, `io_uring_unreg_ringfd`, `io_uring_get_opcode`, `io_is_uring_fops`, and `__io_uring_fork`. Inline wrappers are `io_uring_files_cancel`, `io_uring_task_cancel`, `io_uring_free`, and `io_uring_fork`. Disabled builds provide no-op or safe default stubs.

Control flow: File cancellation cancels the current task's io_uring work without forcing all cancellations; task cancellation requests broader cancellation. Freeing only enters core cleanup if the task has io_uring state or restrictions. Fork handling only calls the core when restrictions need inheritance processing.

State and persistence: State lives in `task_struct` fields such as `io_uring` and `io_uring_restrict`; the header itself owns no storage.

Dependencies and integration points: Depends on scheduler/task state, xarray declarations, and UAPI opcode definitions. Integrates with task exit, fork, file table teardown, and file-operation identification.

Risks: Callers must use the inline guards to avoid touching absent io_uring state. Disabled builds silently no-op, so code must not depend on cancellation side effects unless io_uring is enabled. Fork restriction failures must be propagated.

Test signals: Test task exit, file table teardown, restricted ring fork, disabled-config stubs, opcode name lookup, and file operation identification for io_uring ring files.
