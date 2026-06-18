# sources/distributed-fs/moosefs/mfschunkserver/bgjobs.c

## Purpose
`bgjobs.c` implements the chunkserver background job subsystem. It keeps slow or blocking work out of the main event loop by dispatching disk operations, client read/write service calls, replication, chunk-info queries, and disk moves to worker threads. It also reports load, high-load status, per-task timing counters, and stalled jobs.

## Important Types and APIs
The file defines operation codes (`OP_CHUNKOP`, `OP_SERV_READ`, `OP_SERV_WRITE`, replication modes, `OP_GETINFO`, `OP_CHUNKMOVE`) and task categories (`TASK_READ`, `TASK_WRITE`, `TASK_REPLICATE`, `TASK_CHUNKOP`, `TASK_INFO`, `TASK_MOVE`). Argument structs hold per-operation parameters: `chunk_op_args`, `chunk_rw_args`, `chunk_rp_args`, `chunk_ij_args`, and `chunk_mv_args`.

`job` records the public job id, callback, callback extra pointer, operation arguments, state (`JSTATE_ENABLED`, `DISABLED`, `INPROGRESS`), task type, start timestamp, and debug chunk id. `jobpool` owns a pipe pair for poll-loop wakeups, worker counts and watermarks, mutexes/condition variable, pcqueue job/status queues, a job hash table, and timing counters.

Public entry points include `job_chunkop`, `job_serv_read`, `job_serv_write`, `job_replicate_simple`, `job_replicate_split`, `job_replicate_recover`, `job_replicate_join`, `job_get_chunk_info`, `job_chunk_move`, `job_pool_disable_job`, `job_pool_change_callback`, `job_get_load_and_hlstatus`, and `job_init`.

## Control Flow
`job_init` creates high-priority and low-priority pools, reloads worker limits from config, and registers destruct, can-exit, reload, each-loop, poll, info, periodic counter-shift, and stalled-job callbacks with the common `main` framework. Each pool starts with one worker. `job_new` allocates a `job`, assigns a nonzero id, inserts it into the pool hash, checks queue pressure against `workers_max`, and either queues the job, returns zero for limited-return callers, or emits an immediate error status.

`job_worker` waits on the job queue, marks enabled jobs in progress, may spawn another worker when all workers become busy and the pool is below its max, dispatches to `hdd_chunkop`, `mainserv_read`, `mainserv_write`, `replicate`, `hdd_get_chunk_info`, or `hdd_move`, records timing statistics, then enqueues completion status. The main poll loop watches pool pipes through `job_desc` and calls `job_serve`; `job_pool_check_jobs_in_pool` receives statuses, invokes callbacks, removes hash entries, frees args, and frees jobs.

## State and Persistence
State is in-memory: two global pools, job hash tables, queues, counters, worker counts, high-load status, and pipe readability. No durable state is written. Worker settings come from configuration keys `WORKERS_MAX`, `WORKERS_HLOAD_HIMARK`, `WORKERS_HLOAD_LOMARK`, and `WORKERS_MAX_IDLE`; reload updates both pools.

## Dependencies and Integration Points
This module depends on `pcqueue` for cross-thread queues, `lwthread` and pthread primitives for workers, `main` for event-loop registration, `hddspacemgr` for disk/chunk work, `replicator` for chunk replication, `mainserv` for client I/O serving, `masterconn` for load reporting, `cfg` for tuning, `ionice` for low-priority workers, and `clocks` for monotonic timing.

## Risks
Callbacks run from the main poll context while job execution runs in workers, so callback ownership and lifetime must be clear. Disabled jobs still occupy queue/hash state until completed or drained. `job_new` allocates before checking queue pressure; it carefully removes limited-return jobs, but any future path must preserve that cleanup. `job_pool_disable_job` and `job_pool_change_callback` search both pools by job id, so job ids are not globally unique by construction; a rare id collision across pools could affect both. Worker growth is opportunistic and controlled only by counts/watermarks, so bad config can create resource pressure despite validation warnings.

## Test Signals
Useful tests include queue-full behavior for `JOB_MODE_LIMITED_RETURN` and `JOB_MODE_LIMITED_QUEUE`, cancellation before and during execution, callback replacement, worker high/low watermark transitions and `masterconn_reportload`, stalled-job logging after the 600-second threshold, graceful shutdown waiting for workers, and integration tests where client read/write and replication jobs complete through the poll pipe path.
