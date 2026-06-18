<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-pool.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-pool.h

Purpose: declares the intended state for a future thread-pool worker. The implementation is currently a placeholder and the manager rejects pool worker creation.

Important types: `PINT_worker_pool_attr_t` contains `max_threads`. `struct PINT_worker_pool_s` stores those attributes. No implementation vtable is declared in this header, unlike other worker headers, although `pint-worker-pool.c` defines `PINT_worker_pool_impl`.

Control flow and persistence are absent in the header. It only reserves the attribute/state shape.

Dependencies are `pint-op.h` and aggregate worker inclusion. Integration is incomplete: `pint-worker.h` includes this header and includes `struct PINT_worker_pool_s` in the worker instance union, but manager creation returns `-PVFS_ENOSYS` for pool type.

Risks: incomplete API surface and lack of extern declaration can lead to inconsistent use. Tests should cover that pool is unsupported, and any future implementation should add locking, idle/busy thread queues, bounded posting, completion handling, and a matching extern declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-pool.h -->
