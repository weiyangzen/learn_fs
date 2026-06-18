# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_ctx.c

## Purpose
This file manages AMD XDNA AIE2 hardware contexts, DRM scheduler jobs, command submission, resource allocation, firmware context restart, debug-buffer commands, and HMM invalidation recovery.

## Important APIs, Types, And Functions
Public entry points include `aie2_hwctx_init()`, `aie2_hwctx_fini()`, `aie2_hwctx_suspend()`, `aie2_hwctx_resume()`, `aie2_hwctx_config()`, `aie2_hwctx_sync_debug_bo()`, `aie2_cmd_submit()`, and `aie2_hmm_invalidate()`. `struct aie2_ctx_health` packages timeout health for userspace command errors. The scheduler backend uses `aie2_sched_job_run()`, `aie2_sched_job_free()`, and `aie2_sched_job_timedout()`.

## Control Flow
Context initialization pins the client heap, allocates command-list BOs, initializes DRM scheduler/entity state, computes candidate column starts, resumes the device, allocates AIE resources or temporal-only firmware context, maps host heap to firmware, creates a syncobj, and releases PM usage. Command submission obtains a job semaphore, initializes a DRM sched job, locks BO reservations, repopulates invalid HMM mappings if needed, arms the scheduler job, adds reservation fences, assigns a sequence number, pushes the job, and appends the output fence to the context syncobj. Job execution sends driver commands, chain commands, forced command-list single commands, or legacy execbuf messages. Timeout handling queries app health when supported, stops/destroys the firmware context, restarts it, and marks command health.

## State, Dependencies, Integration, Risks, And Tests
Persistent state includes `hwctx->priv`, pinned heap BO, command BO ring, mailbox channel, syncobj, column list, CU config copy, sequence counters, job semaphores, and submitted/free counters. Dependencies include DRM scheduler/syncobj/GEM reservations, dma fences, XRS resource solver, AMD XDNA GEM and mailbox helpers, PM locks, HMM/MMU interval notifiers, and AIE2 firmware message functions. Risks are deadlocks around `dev_lock`, `io_lock`, reservation locks, and notifier locks; lost semaphore/fence references on error paths; restart failure after timeout; HMM retry loops; and stale debug BO ownership. Test signals include context create/destroy under stress, suspend/resume with pending jobs, timeout recovery with app health, HMM invalidation during submit, syncobj sequence waits, command-list and legacy execution paths, and debug BO attach/sync/detach.
