# sources/distributed-fs/ceph-client/io_uring/statx.c

Purpose: implements io_uring `statx` using delayed pathname resolution and forced async execution.

Important APIs/types/functions: `struct io_statx` stores dfd, mask, flags, delayed filename, and userspace statx buffer. Entry points are `io_statx_prep()`, `io_statx()`, and `io_statx_cleanup()`.

Control flow: prep validates unused SQE fields and rejects fixed-file mode, copies dfd/mask/path/buffer/flags, calls `delayed_getname_uflags()`, marks cleanup, and forces async. Issue completes the delayed filename and calls `do_statx()`. Cleanup dismisses the delayed filename if the request is canceled before issue.

State and persistence: only delayed filename request state is held. External state is a userspace statx result copy and filesystem metadata lookup effects.

Dependencies/integration: depends on VFS `do_statx()`, delayed filename helpers from fs internals, and io_uring cleanup flags.

Risks/test signals: risks include path cleanup on failure, invalid fixed-file use, user buffer faults, and lookup flag propagation. Test regular path, empty path/AT flags, invalid flags, cancellation before issue, and faulted statx buffer.
