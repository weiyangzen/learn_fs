# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_sched.c

## Purpose

`v3d_sched.c` implements the Broadcom V3D driver's DRM GPU scheduler backends. It translates scheduler jobs into hardware register programming for binning, rendering, TFU, CSD, cache-clean, and CPU-side pseudo-jobs; maintains per-client and global queue runtime statistics; switches perfmons around hardware jobs; and performs scheduler-wide GPU reset handling on timeouts.

## Important APIs, Types, and Functions

- `v3d_stats_alloc`, `v3d_stats_release`, `v3d_job_start_stats`, and `v3d_job_update_stats`: allocate and update queue statistics protected by a `seqcount`.
- `v3d_bin_job_run`, `v3d_render_job_run`, `v3d_tfu_job_run`, and `v3d_csd_job_run`: scheduler `run_job` callbacks that create IRQ fences, record active jobs, emit tracepoints, update stats, optionally switch perfmon state, and kick hardware by writing queue registers.
- CPU job handlers: `v3d_rewrite_csd_job_wg_counts_from_indirect`, `v3d_timestamp_query`, `v3d_reset_timestamp_queries`, `v3d_copy_query_results`, `v3d_reset_performance_queries`, and `v3d_copy_performance_query` perform synchronous memory/query operations behind the scheduler.
- `v3d_gpu_reset_for_timeout`, `v3d_cl_job_timedout`, and queue-specific timeout callbacks coordinate `drm_sched_stop`, `v3d_reset`, karma accounting, job resubmission, and scheduler restart.
- `v3d_sched_init` and `v3d_sched_fini` initialize/finalize one `drm_gpu_scheduler` per enabled V3D queue with a credit limit of one and a 500 ms timeout.

## Control Flow

Initialization calls `v3d_queue_sched_init` for bin, render, TFU, CPU, and, when supported, CSD and cache-clean queues. Each scheduler entity later invokes the relevant `run_job` callback. Hardware jobs first check whether the finished fence already has an error, install themselves as `queue->active_job`, create an IRQ fence with `v3d_fence_create`, attach it to `job->irq_fence`, trace submission, start stats, and program registers. For CL queues, writing CT0/CT1 queue end addresses starts execution; for TFU, `ICFG` starts; for CSD, CFG0 starts.

CPU and cache-clean jobs are synchronous. They start stats, run local memory or perfmon work, update stats, and return `NULL` because no hardware fence is needed. Indirect CSD CPU jobs rewrite compute workgroup counts and uniform values before the dependent CSD job runs.

Timeout handling first tries to detect forward progress for CL and CSD queues by comparing current address/return address or batch counters. If progress occurred, it returns `DRM_GPU_SCHED_STAT_NO_HANG`; otherwise it locks `reset_lock`, stops all schedulers, resets the GPU, increments global and client reset counters, resubmits jobs, and restarts all schedulers.

## State and Persistence Behavior

Persistent state lives in `struct v3d_dev`: queue schedulers, `active_job` pointers, stats refs, active/global perfmons, reset counters, and reset/scheduler locks. Per-job state includes IRQ and done fences, BO references, perfmon refs, query arrays, and queue-specific arguments. Stats are updated with local-clock timestamps under seqcount while preemption is disabled, allowing sysfs/debug readers to sample them safely. CPU query jobs persist results by writing into mapped BO memory and by replacing syncobj fences.

## Dependencies and Integration Points

This file integrates with DRM GPU scheduler, DMA fences, DRM syncobjs, V3D register macros, perfmon helpers, cache maintenance helpers, BO vmap helpers, reset code, and tracepoints from `v3d_trace.h`. It is fed by `v3d_submit.c`, and completion is driven by IRQ/fence code elsewhere in the V3D driver.

## Risks and Edge Cases

- CPU job handlers assume submit-time validation guaranteed BO counts, offsets, and query array sizes; bad validation can become out-of-bounds BO writes.
- Indirect CSD workgroup multiplication can overflow before assignment to CFG4; only the all-ones result is warned.
- `v3d_switch_perfmon` stops the previous active perfmon and starts the new one around jobs; bad lifetime/ref handling in submit paths could lead to stale perfmon use.
- Timeout progress heuristics can defer reset for workloads that keep changing command pointers while still effectively hung.
- `drm_sched_init` failure after earlier queues requires `v3d_sched_fini`; the cleanup path relies on `sched.ready`.

## Test Signals

Useful signals include IGT submit/timeout/reset tests, perfmon switching tests across mixed queues, CPU query tests validating timestamp/performance BO writes and syncobj replacement, indirect CSD tests for uniform rewrite and CFG4 generation, sysfs stats monotonicity checks, and lockdep coverage for `reset_lock`, queue locks, and BO vmap lifetimes.
