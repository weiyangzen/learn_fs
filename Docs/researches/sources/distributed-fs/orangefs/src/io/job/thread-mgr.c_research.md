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
