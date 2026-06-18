# sources/distributed-fs/orangefs/src/io/job/job.c

## Purpose
`job.c` implements the OrangeFS/PVFS2 job interface: a common asynchronous facade over BMI networking, TROVE storage, request scheduling, flow I/O, the client device channel, null jobs, and server precreate-pool handling. Callers post operations through `job_*()` functions, receive either immediate completion or a `job_id_t`, and later use `job_test()`, `job_testsome()`, or `job_testcontext()` to collect completion status.

## Important APIs, types, and functions
The file is centered on `struct job_desc` from `job-desc-queue.h`; every asynchronous post allocates a descriptor, registers it with the safe id generator, stores caller context and callbacks, and eventually deallocates it after completion collection. Lifecycle APIs are `job_initialize()`, `job_finalize()`, `job_open_context()`, `job_close_context()`, and `job_reset_timeout()`.

Network APIs include `job_bmi_send()`, `job_bmi_send_list()`, `job_bmi_recv()`, `job_bmi_recv_list()`, `job_bmi_unexp()`, `job_bmi_unexp_cancel()`, and `job_bmi_cancel()`. Storage wrappers include bytestream, keyval, dataspace, collection, and eattr operations such as `job_trove_bstream_read_list()`, `job_trove_keyval_write_list()`, `job_trove_dspace_create_list()`, `job_trove_dspace_verify()`, and `job_trove_fs_geteattr()`. Other front doors are `job_req_sched_post()`, `job_req_sched_release()`, `job_flow()`, `job_dev_unexp()`, `job_dev_write()`, `job_null()`, and the precreate-pool family.

Internal completion functions are `bmi_thread_mgr_callback()`, `trove_thread_mgr_callback()`, `flow_callback()`, unexpected-message handlers, `do_one_test_cycle_req_sched()`, `completion_query_some()`, `completion_query_context()`, and `fill_status()`.

## Control flow
Initialization creates unexpected-message queues, starts the BMI, device, and TROVE thread managers as configured, stores their global contexts, initializes id generation, and flips the `initialized` flag. A typical post path allocates a descriptor, installs a lower-layer callback, calls the lower API, then follows the common tri-state convention: negative return fills `out_status_p` and returns `1` as immediate error completion, `1` fills immediate success status and frees the descriptor, and `0` returns a job id and relies on later callback completion.

Callbacks check `initialized`, lock completion state, populate descriptor-specific result fields, set `completed_flag`, enqueue on `completion_queue_array[context_id]`, and signal `completion_cond` in threaded builds. `job_testsome()` requires every requested id to be complete before returning any of them; `job_testcontext()` drains any completed jobs from one context. Threaded builds wait on a condition variable. Non-threaded builds call `do_one_work_cycle_all()` to push BMI, device, and TROVE progress manually.

Request scheduler jobs are special: successful post descriptors are retained after completion because `job_req_sched_release()` needs the original scheduler id. Precreate-pool jobs are also special: they fan out multiple TROVE keyval operations and complete the parent descriptor after all child operations finish or when a waiting pool condition changes.

## State and persistence behavior
Process-local state includes global BMI/TROVE contexts, per-context completion queues, unexpected BMI/device queues, pending counters, `initialized`, and precreate-pool lists keyed by file-system id. Persistent effects are delegated to TROVE: bytestream data, keyvals, dataspace attributes, collection attributes, and precreated handles stored in pool keyvals. The in-memory precreate `pool_count` mirrors storage but can drift if TROVE writes fail; the code warns that fsck may be needed for stranded handles.

## Dependencies and integration points
This file integrates `thread-mgr.c`, `job-desc-queue`, `job-time-mgr`, `id-generator`, BMI, TROVE, the flow subsystem, the server request scheduler, `pint-dev`, quicklists, mutex abstractions, and `gossip` logging. It is the primary API consumed by OrangeFS state machines that need a uniform asynchronous completion model across network, disk, scheduler, and client-device work.

## Risks
Several public APIs are stubs returning `-PVFS_ENOSYS`: bytestream validate, keyval validate, and file-system remove. Some functions assume valid `context_id` and valid lookup results; for example `job_bmi_unexp_cancel()` dereferences the lookup result without a null guard. Closing a context cleans queued descriptors but does not visibly cancel lower-layer operations. Pending counters are intentionally not always updated in threaded paths, which makes them unsuitable for general correctness checks. In `precreate_pool_get_handles_try_post()`, the low-pool waiter path enqueues `jd_checker` but sets `jd->completed_flag`, which appears to mark the wrong descriptor. Precreate get callbacks preserve the first error while children run, but the all-done branch sets the parent error to zero, which may hide earlier child errors.

## Test signals
Useful tests should cover immediate and asynchronous BMI/TROVE completions, timeout reset for BMI/flow only, context draining order, request-scheduler post/release descriptor retention, cancellation races around already-completed operations, non-threaded progress loops, unexpected BMI/device delivery ordering, and precreate-pool low-water, empty-pool sleep, specific-server lookup, and storage-failure paths.
