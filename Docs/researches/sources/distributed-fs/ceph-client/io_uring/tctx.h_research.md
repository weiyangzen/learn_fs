# sources/distributed-fs/ceph-client/io_uring/tctx.h

Purpose: declares per-task io_uring context helpers and defines the ring-to-task node structure.

Important APIs/types/functions: `struct io_tctx_node` links a task and ring through the ring's `tctx_list` and the task xarray. Prototypes cover task context allocation, node add/delete/clean, registered ring fd register/unregister, and `io_uring_unreg_ringfd()`. Inline `io_uring_add_tctx_node()` fast-paths when `current->io_uring->last == ctx`.

Control flow: inline fast path returns immediately for repeated submissions to the same ring; otherwise it calls the full submit-time add path.

State and persistence: defines link state between task and ring plus the cached last-ring behavior.

Dependencies/integration: used by submit, register, SQPOLL, task exit, and cancellation paths.

Risks/test signals: stale `last` or missed node install would break cancellation/accounting. Multi-ring submit and task-exit tests cover it.
