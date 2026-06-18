# sources/distributed-fs/orangefs/src/client/usrint/aiocommon.c
## sources/distributed-fs/orangefs/src/client/usrint/aiocommon.c

**Purpose:** Implements the internal asynchronous I/O scheduler/progress engine for OrangeFS user-interface AIO wrappers.

**APIs and control flow:** `aiocommon_init()` allocates waiting/running/finished quicklists. `aiocommon_lio_listio()` initializes sysint, validates inputs/lists, submits up to `PVFS_AIO_MAX_RUNNING` requests immediately via `aiocommon_readorwrite()`, queues overflow on the waiting list, and starts a progress thread if needed. `aiocommon_readorwrite()` validates descriptors, builds file/memory PVFS requests, maps opcode to read/write/NOP, calls `PVFS_isys_io`, and sets aiocb error/return fields for failure/immediate/deferred cases. `aiocommon_progress()` refills running slots from waiting, calls `PVFS_sys_testsome`, moves completed requests to finished, maps PVFS errors to errno, updates running op arrays, and exits when no work remains. `aiocommon_remove_cb()` removes a finished CB and frees PVFS requests.

**State and dependencies:** Global quicklists, mutexes, progress thread state, running op array, and running count. Depends on sysint async I/O, descriptor table, request conversion, qlist, pthreads, errno mapping, and gossip.

**Risks and tests:** The global lifecycle lacks finalize cleanup. `progress_running` and `num_aiocbs_running` are shared under mixed mutexes. `temp_running_ops` is not cleared before each removal. Request conversion buffers need ownership clarity. Tests should cover concurrency, queue overflow, immediate completions, failures, NOP, descriptor invalidation, progress thread exit/restart, and cleanup after `aio_return`.
