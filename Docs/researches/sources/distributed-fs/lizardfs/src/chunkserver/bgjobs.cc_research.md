# sources/distributed-fs/lizardfs/src/chunkserver/bgjobs.cc

## Purpose
`bgjobs.cc` implements the chunkserver background job pool. It lets event-loop/network code enqueue HDD and replication operations onto worker pthreads, then wake the main loop through a pipe when status callbacks are ready.

## Important APIs, Types, And Functions
- `jobpool` owns the wake pipe, worker threads, locks, job queue, status queue, hash table of live jobs, and the next job id.
- `job` stores job id, callback, callback context, operation-specific arguments, state, and hash-chain link.
- `OP_*` operation constants cover invalid jobs, chunk create/delete/version/truncate/duplicate-style operations, open/close/read/prefetch/write, legacy replication, modern replication, and block-count lookup.
- `job_worker` is the worker-thread loop. It dequeues work, snapshots/disables state under `jobslock`, calls the matching `hddspacemgr`, legacy replicator, or `ChunkReplicator` operation, and sends completion status.
- `job_new` allocates and hashes a job, puts it on the producer/consumer queue, and returns a nonzero job id.
- Public `job_*` functions allocate typed argument structs and enqueue specific operations.
- `job_pool_check_jobs` drains completion statuses, invokes callbacks, removes jobs from the hash table, and frees job/argument memory.
- `job_pool_disable_job`, `job_pool_disable_and_change_callback_all`, and `job_pool_change_callback` provide cancellation/callback retargeting used by higher-level connection teardown.

## Control Flow
`job_pool_new` creates a pipe, initializes queues/locks, starts worker threads, and returns the read descriptor as a wakeup handle. A producer calls a public `job_*` function, which packages arguments and calls `job_new`. A worker blocks on `queue_get`, marks enabled jobs as `JSTATE_INPROGRESS`, dispatches the operation, and calls `job_send_status`. `job_send_status` writes one byte only when the status queue transitions from empty to non-empty, so the event loop can select/poll the pipe. The main thread calls `job_pool_check_jobs`, which drains status records until the queue is empty, reads the wake byte, invokes callbacks, and releases memory.

For reads, optional `performHddOpen` opens the chunk before `hdd_read` and closes it after read errors. Modern replication deserializes `ChunkTypeWithAddress` sources, constructs a `ChunkFileCreator`, and calls global `gReplicator.replicate`; `Exception` status becomes the job status. Legacy replication passes the packed source list directly to `legacy_replicate`.

## State And Persistence
Runtime state is in heap-allocated `jobpool`, worker threads, queues, job hash chains, and malloced argument buffers. No state is persisted to disk by the job layer itself, but enqueued operations mutate chunk files and HDD state through `hddspacemgr` and replication helpers. Job ids wrap around but skip zero.

## Dependencies And Integration Points
The implementation depends on `common/pcqueue`, pthreads, Unix pipes, `hddspacemgr`, `legacy_replicator`, `ChunkReplicator`, `ChunkFileCreator`, `ChunkTypeWithAddress` serialization, LizardFS error/status constants, syslog, and tracing/request-log helpers. It exposes a C-compatible API declared in `bgjobs.h` for other chunkserver modules.

## Risks
- Callback changes and disable operations mostly walk hash chains without holding the lock for the entire lookup, so correctness relies on only the main thread mutating/removing completed jobs while workers only change state under lock.
- Argument structs keep raw pointers for write buffers, read output buffers, and block output pointers; callers must guarantee lifetime until callback completion.
- `job_prefetch` does not honor disabled job state in the worker branch and has no callback, so failures are effectively fire-and-forget.
- The wake-pipe byte represents queue non-emptiness, not per-status count. Bugs in drain logic can desynchronize the event-loop wakeup.
- `job_pool_delete` joins workers after sending `OP_EXIT`, but outstanding completed statuses can still invoke callbacks during deletion.
- The modern replication branch catches `Exception&` but not non-LizardFS exceptions from STL or logic errors.

## Test Signals
No direct unit test is listed for `bgjobs.cc`. Coverage is likely indirect through chunkserver integration tests. Useful tests would exercise cancellation before start, cancellation during in-progress work, callback retargeting, wake-pipe drain behavior, raw pointer lifetime expectations, and replication exception propagation.
