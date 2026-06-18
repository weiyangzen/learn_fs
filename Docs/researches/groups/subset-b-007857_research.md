# subset-b-007857 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/job.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/job.h -->
# sources/distributed-fs/orangefs/src/io/job/job.h

## Purpose
`job.h` declares the public OrangeFS job API. It gives server and client code a single asynchronous operation contract for network, storage, flow, scheduler, device, null, and precreate-pool work.

## Important APIs and types
`job_id_t` is an id-generator-backed operation id, and `job_context_id` identifies one completion queue slot. `JOB_MAX_CONTEXTS` limits concurrent job contexts to 16. `job_status_s` is the common completion payload: it always carries `status_user_tag` and `error_code`, and conditionally carries actual byte count, vtag, iterator position, created handle, verified type, collection id, and item count.

Management APIs are `job_initialize()`, `job_finalize()`, `job_open_context()`, `job_close_context()`, and `job_reset_timeout()`. Posting APIs are grouped by subsystem: BMI send/receive/unexpected/cancel, client device unexpected/write, request scheduler post/mode/timer/release, `job_flow()`, a large TROVE storage set, `job_null()`, and precreate-pool helpers. Completion APIs are `job_test()`, `job_testsome()`, and `job_testcontext()`.

## Control flow and contract
Post functions follow the same contract documented by implementation comments: return `1` when the job completed immediately and `out_status_p` is valid, return `0` when the caller must later test the returned id, and return negative errors for some unsupported or setup failures. The completion APIs populate arrays of returned user pointers and statuses, with `job_test()` acting as a single-id wrapper around `job_testsome()`.

## State and persistence behavior
This header does not hold state, but its API exposes the stateful parts of the implementation: contexts, job ids, timeout-managed operations, and status fields that reflect lower-layer persistent TROVE operations. The precreate-pool functions expose a server-side cache/allocation layer over stored handle pools.

## Dependencies and integration points
The header includes flow descriptors, BMI types, PVFS core types, `pvfs2-storage.h`, request protocol and scheduler types, and `pint-dev`. That makes it a high-fan-in interface between state machines and lower I/O subsystems.

## Risks
The API is broad and relies on callers knowing which `job_status_s` fields apply to which operation. The return convention can be easy to misuse because negative returns and immediate error completions are both possible depending on function/build path. `JOB_MAX_CONTEXTS` is fixed, and there is no type-level separation between job ids from different subsystems.

## Test signals
Header-level compatibility tests should compile representative callers for every declared family, assert expected status fields for each operation type, and check that unsupported build configurations still expose declarations while returning the documented runtime error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/job/module.mk.in

## Purpose
This makefile fragment registers the job subsystem sources with the OrangeFS build.

## Important entries
It sets `DIR := src/io/job` and appends `job.c`, `job-desc-queue.c`, `thread-mgr.c`, and `job-time-mgr.c` to both `LIBSRC` and `SERVERSRC`.

## Control flow and build behavior
The fragment has no runtime control flow. Build inclusion is simple and duplicated: the same job implementation is compiled into the general library source set and into server source builds.

## State, persistence, and dependencies
No state or persistence is defined here. The dependency signal is architectural: the job subsystem is both client/library-facing and server-facing, so changes to its ABI or build guards can affect both deployment shapes.

## Risks
Because the fragment lists the same files in two source variables, any new job subsystem file must be added consistently to both unless it is intentionally server-only or library-only. Formatting uses backslash continuations without spaces after some filenames, so mechanical edits should preserve make syntax carefully.

## Test signals
Build tests should confirm both library and server targets still compile after any source-list change, especially with `__PVFS2_JOB_THREADED__`, `__PVFS2_CLIENT__`, and TROVE support variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/thread-mgr.c -->
# sources/distributed-fs/orangefs/src/io/job/thread-mgr.c

## Purpose
`thread-mgr.c` drives completion progress for lower-level BMI, TROVE, and client device operations. In threaded builds it owns worker threads that poll test contexts and invoke job callbacks. In non-threaded builds the same polling functions are called through explicit `PINT_thread_mgr_*_push()` hooks.

## Important APIs, types, and functions
The public functions implement the declarations in `thread-mgr.h`: start/stop/getcontext/cancel for BMI and TROVE, start/stop and unexpected-handler registration for the device path, unexpected handler registration for BMI, and manual push hooks. Internal functions are `bmi_thread_function()`, `trove_thread_function()`, and `dev_thread_function()`. Callback carrier structs come from `thread-mgr.h`: `PINT_thread_mgr_bmi_callback` and `PINT_thread_mgr_trove_callback`.

## Control flow
Startup functions are ref-counted. The first BMI start opens a BMI context and, in threaded builds, creates a BMI thread; later starts only increment the ref count. TROVE startup opens a TROVE context using the file-local `HACK_fs_id` and creates a TROVE thread when enabled. Device startup creates a device unexpected polling thread only in client builds.

The BMI loop first services unexpected-message demand with `BMI_testunexpected()`, then calls `BMI_testcontext()` with fixed-size arrays and invokes each returned callback with actual size and error code. TROVE uses `trove_dspace_testcontext()` and invokes callback/error pairs. Device polling waits until unexpected demand exists and calls `PINT_dev_test_unexpected()`. Stop functions decrement ref counts, flip running flags, join threads when present, and close contexts.

Cancellation waits until the corresponding testcontext call is not active, scans already-returned completion arrays to avoid canceling an operation that is effectively done, then calls `BMI_cancel()` or `trove_dspace_cancel()`. Manual push functions temporarily set the polling timeout and run the same loop bodies once.

## State and persistence behavior
The file stores global BMI/TROVE contexts, ref counts, running flags, fixed result arrays of size `THREAD_MGR_TEST_COUNT`, unexpected-message counts and handlers, and mutex/condition variables around test and cancellation windows. It does not persist data itself; it exposes progress for subsystems that may persist data, chiefly TROVE.

## Dependencies and integration points
Dependencies include BMI, TROVE, `pint-dev`, `gen-locks`, pthreads under `__PVFS2_JOB_THREADED__`, `pint-event`, and `gossip`. The job layer passes callback structs as lower-layer `user_ptr` values, and this manager casts those pointers back and invokes their functions.

## Risks
Batching is capped at five completions per test call, so high-throughput workloads depend on repeated polling. The TROVE context uses a hard-coded `HACK_fs_id = 9`, marked as a TODO. Cancellation synchronization is subtle: it relies on flags and condition variables to avoid racing with active testcontext calls. Device polling exits the process with `-PVFS_ENODEV` on critical device failure. Handler registration rejects a different handler while unexpected demand is outstanding, but the counters are also demand counters, so mismatched registration/unregistration patterns would be dangerous.

## Test signals
Tests should exercise threaded and non-threaded builds, repeated start/stop reference counting, context retrieval before and after start, cancellation while testcontext is active, unexpected BMI/device handler dispatch, fixed-batch completion draining, and critical-error handling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/thread-mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/thread-mgr.h -->
# sources/distributed-fs/orangefs/src/io/job/thread-mgr.h

## Purpose
`thread-mgr.h` declares the progress manager used by `job.c` to bridge asynchronous lower-layer operations into job completions.

## Important APIs and types
`struct PINT_thread_mgr_bmi_callback` stores a BMI completion callback accepting caller data, actual size, and error code. `struct PINT_thread_mgr_trove_callback` stores a TROVE callback accepting caller data and error code. The BMI API covers cancel, start, stop, context retrieval, and unexpected-handler registration. The TROVE API covers start, stop, context retrieval, and cancel. The device API covers start, stop, and unexpected-handler registration. The three `PINT_thread_mgr_*_push()` functions expose progress driving for non-threaded operation.

## Control flow and integration
The header does not implement control flow, but it establishes the callback contract used by `job.c`: job descriptors embed these callback structs and pass them as lower-layer user pointers; `thread-mgr.c` receives completed lower-layer events and calls back into `job.c`.

## State and persistence behavior
State is private to the implementation. This header exposes only context retrieval and cancellation entry points, so callers do not own the underlying BMI/TROVE contexts directly.

## Dependencies
It depends on PVFS internal/types headers, BMI, and `pint-dev` because callback signatures and contexts use those types.

## Risks
The callback data is untyped `void *`, so lifetime correctness depends on job descriptors staying alive until the manager has invoked or skipped the callback. The header exposes no explicit shutdown drain contract; callers must rely on `job_finalize()` and the implementation's ref-counted stop behavior.

## Test signals
Compile-time tests should verify callback signatures against BMI/TROVE call sites. Runtime tests should ensure cancel and push functions are available and behave consistently in threaded and non-threaded configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/job/thread-mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/trove/module.mk.in

## Purpose
This makefile fragment registers the core TROVE storage subsystem sources for server builds.

## Important entries
It sets `DIR := src/io/trove` and appends `trove-mgmt.c`, `trove-error.c`, and `trove.c` to `SERVERSRC`. A commented section documents that autogenerated `trove-autogen.c` generation from `trove-proto.h` via `maint/trove-autogen.pl` has been disabled.

## Control flow and build behavior
There is no runtime control flow. Build behavior is server-only in this fragment, unlike the job fragment that feeds both `LIBSRC` and `SERVERSRC`.

## State, persistence, and dependencies
No runtime state is held here. The fragment identifies the TROVE management/error/core implementation as server build inputs and records historical generated-code machinery that is currently inactive.

## Risks
Because autogenerated code is disabled, any build logic or source references that still expect `trove-autogen.c` would fail unless handled elsewhere. New TROVE source files must be added to `SERVERSRC` explicitly. Re-enabling the generator would need care around release builds and `TROVE_AUTOGEN_FILES`.

## Test signals
Server build tests should verify the TROVE source list is sufficient without generated code. Dist/release packaging checks should confirm disabled autogen files are not required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/pvfs2-storage.h -->
# sources/distributed-fs/orangefs/src/io/trove/pvfs2-storage.h

## Purpose
`pvfs2-storage.h` defines storage-facing PVFS/TROVE attribute types and conversion macros used by the job and TROVE layers.

## Important APIs, types, and macros
`PVFS_coll_getinfo_options` currently defines `PVFS_COLLECTION_STATFS`. `PVFS_vtag` is an opaque version tag placeholder, with a dummy field on Windows. `PVFS_ds_attributes` is the storage-layer dataspace attribute format: common type, fs id, handle, uid, gid, mode, ctime, mtime, atime, plus a union for metafile, datafile, or dirdata-specific attributes.

Macros include `PVFS_ds_init_time()` for initializing all three times to `time(NULL)`, `PVFS_ds_attr_to_object_attr()` for copying storage attributes into user/server object attributes, `PVFS_object_attr_to_ds_attr()` for the reverse direction, and `PVFS_object_attr_overwrite_setable()` for applying settable object-attribute mask fields.

## Control flow
The file has no functions, but macro control flow matters. `PVFS_object_attr_overwrite_setable()` conditionally updates owner, group, permissions, atime, mtime, ctime, object type, and metafile distribution fields according to mask bits; unset explicit atime/mtime values are replaced with current time/versioned current time.

## State and persistence behavior
`PVFS_ds_attributes` describes the form TROVE stores for dataspaces, distinct from wire/user-facing `PVFS_object_attr`. Comments note historical storage format differences that would require migration utilities when layouts change. Time macros call `time(NULL)`, so repeated macro arguments should not be expressions with side effects.

## Dependencies and integration points
The header depends on PVFS internal/types headers and `<time.h>`. It is included by `job.h` so job status and TROVE wrappers can refer to storage attributes and vtags. TROVE code uses these structures to persist and translate object metadata.

## Risks
The conversion macros assume metafile union fields when copying distribution data, so callers must use them with compatible object types and masks. Macro arguments are evaluated many times, which is risky for nontrivial expressions. Adding fields to storage or object attributes requires updating both conversion directions and considering on-disk migration.

## Test signals
Tests should cover round-trip conversion for metadata attributes, selective overwrite masks for uid/gid/perms/time/type/dist/dfiles, time-setting behavior for explicit and implicit atime/mtime, and ABI/layout expectations for stored `PVFS_ds_attributes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/trove/pvfs2-storage.h -->
