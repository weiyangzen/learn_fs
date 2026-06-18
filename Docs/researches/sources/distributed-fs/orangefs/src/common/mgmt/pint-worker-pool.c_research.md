<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-pool.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-pool.c

Purpose: placeholder for a thread-pool worker backend. The vtable is exported but all callbacks are `NULL`.

Important object: `PINT_worker_pool_impl` has name `POOL` and no init, destroy, queue, post, or do-work implementation. The manager currently handles `PINT_WORKER_TYPE_POOL` by returning `-PVFS_ENOSYS`, so this vtable is not expected to be used for live posts.

Control flow is absent. There is no runtime state in this file and no persistence.

Dependencies include the pool header, aggregate worker/manager headers, and OrangeFS types. Integration is build-level only unless future code enables the manager path.

Risks: if a caller somehow obtains or registers this vtable despite the manager guard, post attempts would dereference `NULL` callbacks. Tests should verify `PINT_manager_worker_add()` rejects pool workers with `-PVFS_ENOSYS` and that no code bypasses the manager to use `PINT_worker_pool_impl` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-pool.c -->
