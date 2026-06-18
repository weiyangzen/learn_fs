# sources/distributed-fs/ceph-client/io_uring/tctx.c

Purpose: manages per-task io_uring context, io-wq offload creation, task-to-ring mappings, registered ring fds, task restrictions, and fork cleanup/clone behavior.

Important APIs/types/functions: `io_uring_alloc_task_context()`, `__io_uring_free()`, `__io_uring_add_tctx_node()`, `__io_uring_add_tctx_node_from_submit()`, `io_uring_del_tctx_node()`, `io_uring_clean_tctx()`, `io_uring_unreg_ringfd()`, `io_ringfd_register()`, `io_ringfd_unregister()`, and `__io_uring_fork()`.

Control flow: allocation creates `io_uring_task`, inflight counter, io-wq with a per-ring hash map, waitqueue, task llist, and task_work callback. Adding a context ensures single-issuer rules, applies io-wq worker limits, installs a node in the task xarray and ring tctx list, and caches `last` for fast submit. Cleanup removes all nodes, exits io-wq, drops registered ring files, and frees task restrictions. Ring-fd registration ensures a task context, validates io_uring fds, fills requested or free slots, and copies assigned offsets back to userspace.

State and persistence: per-task state includes `current->io_uring`, xarray of ring nodes, io-wq, inflight counters, task_work list, registered ring fd references, `last` ring shortcut, and `io_uring_restrict` filters. It persists for task lifetime.

Dependencies/integration: integrates with io-wq, xarray, ring tctx lists, BPF/restriction clone, registered-ring syscall fast paths, fork handling, and cancellation.

Risks/test signals: risks include xarray/list mismatch, io-wq lifetime races, registered ring fd leaks, single-issuer violations, and fork restriction clone failure. Test multi-ring tasks, ring close/task exit, registered ring fd register/unregister, io-wq limits propagation, fork with restrictions, and fault injection in node allocation.
