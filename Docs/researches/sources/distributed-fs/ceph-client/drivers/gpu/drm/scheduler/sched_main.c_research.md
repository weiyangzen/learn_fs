## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_main.c

### Purpose

`sched_main.c` implements the DRM GPU scheduler core: runqueues, priority/FIFO/RR entity selection, credit-based flow control, job initialization/arming/dependency helpers, hardware submission work, finished-job freeing, timeout/TDR handling, reset recovery support, scheduler init/fini, and workqueue pause/resume controls.

### Important APIs, Types, and Functions

Exported APIs include timeout/recovery controls (`drm_sched_tdr_queue_imm()`, `drm_sched_fault()`, `drm_sched_suspend_timeout()`, `drm_sched_resume_timeout()`, `drm_sched_stop()`, `drm_sched_start()`, `drm_sched_resubmit_jobs()`), job APIs (`drm_sched_job_init()`, `drm_sched_job_arm()`, dependency add helpers, `drm_sched_job_has_dependency()`, `drm_sched_job_cleanup()`, `drm_sched_job_is_signaled()`), scheduler APIs (`drm_sched_pick_best()`, `drm_sched_init()`, `drm_sched_fini()`, `drm_sched_increase_karma()`, `drm_sched_wqueue_ready()`, `drm_sched_wqueue_stop()`, `drm_sched_wqueue_start()`, `drm_sched_is_stopped()`), and internal runqueue/work helpers.

### Control Flow

Drivers initialize a scheduler with backend ops, credit limit, timeout, priority count, and workqueues. Jobs are initialized against an entity, assigned nonzero credits, armed to initialize scheduler fences and choose the current scheduler/runqueue, populated with explicit/syncobj/reservation dependencies, and pushed by `sched_entity.c`.

`drm_sched_run_job_work()` selects the highest-priority ready entity using FIFO rb-tree or round-robin list policy. It enforces credit availability, pops one dependency-free job, increments in-flight credits, adds it to `pending_list`, starts the timeout, calls backend `run_job()`, signals the scheduled fence, installs a callback on the returned hardware fence, and requeues itself for more work. Completion callbacks call `drm_sched_job_done()`, which subtracts credits, signals the finished fence, and queues free-job work. `drm_sched_free_job_work()` removes finished jobs from `pending_list`, calls backend `free_job()`, restarts timeout for the next pending job, and wakes submission.

Timeout work removes the oldest pending job, calls backend `timedout_job()`, handles false timeouts by reinserting the job, and restarts timeout unless the device is gone. Reset recovery uses `drm_sched_stop()` to pause workqueues and detach callbacks, driver reset logic, and `drm_sched_start()` to reattach callbacks or finish canceled jobs.

### State and Persistence Behavior

Scheduler state includes backend ops, runqueue array, `pending_list`, `job_list_lock`, ordered submit workqueue, timeout workqueue/delayed work, `ready` and `pause_submit`, credit limit/count, shared or private score, job ID counter, timeout/hang limit, and free-guilty marker. Runqueues maintain an entity list plus FIFO rb-tree keyed by oldest waiting job timestamp. Jobs persist from init through backend `free_job()` and carry credits, priority, scheduler pointer, dependencies xarray, pending-list node, callbacks, and scheduler fence.

### Dependencies and Integration Points

It depends on public DRM scheduler types, DMA fences/reservations, GEM objects, syncobjs, Linux workqueues, wait queues, completions, rbtrees, atomics, module parameters, and tracepoints. DRM drivers integrate by supplying `struct drm_sched_backend_ops` (`run_job`, `free_job`, `timedout_job`, optional `prepare_job`/`cancel_job`) and by wiring scheduler entities to contexts or queues.

### Risks and Edge Cases

Credit accounting must stay balanced across run, done, stop, false-timeout, and restart paths or the scheduler can starve or overrun hardware capacity. Job arm is a point of no return: drivers must push armed jobs and cannot clean them up directly. Timeout recovery has many lifetime races with free-job work and hardware-fence callbacks; `drm_sched_stop()` cancels work before mutating pending jobs for this reason. `drm_sched_resubmit_jobs()` is explicitly deprecated because generic resubmission around DMA fences is unsafe. `drm_sched_job_init()` logs through `job->sched->dev` even before `memset(job, 0)`, so callers need a job object whose scheduler pointer is meaningful in the no-rq error path. Scheduler teardown can leak pending jobs if the backend lacks `cancel_job()`.

### Test Signals

Coverage should include FIFO and RR policy behavior, priority ordering, credit-limit throttling including oversized jobs, dependency deduplication by fence context, syncobj and implicit reservation dependencies, job arm/push/cleanup misuse paths, hardware-fence completion and error propagation, false timeout handling, reset stop/start with guilty job retention, scheduler fini with and without `cancel_job`, workqueue stop/start, and KUnit mock scheduler tests. Real driver tests should run with lockdep, KASAN, and tracing enabled under GPU hang/recovery stress.
