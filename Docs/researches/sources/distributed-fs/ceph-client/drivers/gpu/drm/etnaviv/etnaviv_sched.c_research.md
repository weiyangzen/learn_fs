## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_sched.c

### Purpose
`etnaviv_sched.c` adapts Etnaviv submits to the DRM GPU scheduler. It runs jobs on hardware, allocates userspace-visible fence ids, detects hangs, captures dumps, recovers the GPU, resubmits jobs, and frees submit references when scheduler jobs retire.

### Important APIs, Types, And Functions
Public APIs are `etnaviv_sched_init()`, `etnaviv_sched_fini()`, and `etnaviv_sched_push_job()`. Scheduler backend callbacks are `etnaviv_sched_run_job()`, `etnaviv_sched_timedout_job()`, and `etnaviv_sched_free_job()`. Module parameters `job_hang_limit` and `hw_job_limit` tune DRM scheduler behavior.

### Control Flow
Push holds `gpu->sched_lock`, allocates a cyclic xarray fence id, arms the DRM scheduler job, stores the scheduler finished fence in both the submit and user-fence xarray, takes a submit reference for scheduler ownership, and pushes the job to its entity. Run-job skips jobs whose scheduler fence already has an error, otherwise calls `etnaviv_gpu_submit()`. Timeout checks for spurious already-signaled fences, then compares FE DMA address, completed fence, and 3D primitive id to detect forward progress. A real hang stops the scheduler, increases karma, dumps state, resets the GPU, resubmits jobs, and restarts scheduling.

### State, Persistence, And Dependencies
Scheduler state is in `gpu->sched`, `gpu->sched_lock`, submit `sched_job`, user-fence xarray entries, and hangcheck fields in `struct etnaviv_gpu`. Dependencies include DRM scheduler APIs, DMA fences, generated profile registers, Etnaviv dump, GPU submit/recover, and GEM submit refcounting.

### Integration Points
`etnaviv_gem_submit.c` calls `etnaviv_sched_push_job()`. `etnaviv_gpu.c` provides hardware submission and recovery. User fence waits look up xarray ids allocated here.

### Risks
Fence id allocation and scheduler fence sequence ordering require `sched_lock`. If hardware submission returns `NULL`, scheduler behavior depends on DRM handling of run-job failure. Hangcheck must avoid false positives while FE or primitive id advances. Timeout sampling of profile registers must coordinate with perfmon.

### Test Signals
Tests should cover push failure paths, cyclic fence-id allocation, bad dependency skipping, timeout when fence already signaled, forward-progress deferral, real hang reset and resubmit, scheduler fini with queued jobs, and module parameter boundary values.
