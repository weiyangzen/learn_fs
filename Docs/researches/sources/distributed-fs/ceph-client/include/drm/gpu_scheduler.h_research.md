# sources/distributed-fs/ceph-client/include/drm/gpu_scheduler.h

## Purpose
`gpu_scheduler.h` declares the DRM GPU scheduler framework used by drivers to queue jobs from entities, resolve dma-fence dependencies, submit work to hardware rings, track completion fences, and recover from timeouts.

## Important APIs, types, and functions
Key types are `enum drm_sched_priority`, `struct drm_sched_entity`, `struct drm_sched_rq`, `struct drm_sched_fence`, `struct drm_sched_job`, `enum drm_gpu_sched_stat`, `struct drm_sched_backend_ops`, `struct drm_gpu_scheduler`, `struct drm_sched_init_args`, and pending-job iterator helpers. Backend ops are `prepare_job`, `run_job`, `timedout_job`, `free_job`, and `cancel_job`. Scheduler APIs include `drm_sched_init/fini`, timeout suspend/resume/queue, workqueue stop/start, scheduler stop/start/resubmit/fault/is_stopped, and `drm_sched_pick_best`. Job APIs include init/arm/push, dependency additions from fences/syncobjs/reservations/GEM objects, cleanup, karma, and signaled checks. Entity APIs include init/flush/fini/destroy, priority change, error query, and scheduler-list modification.

## Control flow
Drivers initialize one scheduler per hardware ring or queue, initialize entities for clients, initialize jobs with credits and owner/client ID, add explicit and implicit dependencies, arm scheduler fences, and push jobs to entity queues. The scheduler picks runnable entities by priority/policy, waits for dependencies, calls `prepare_job` until dependencies are clear, submits through `run_job`, links parent hardware fences to scheduled/finished fences, and calls `free_job` after completion. Timeout work invokes driver recovery through `timedout_job`; stopped schedulers can be inspected with the pending-job iterator.

## State and persistence
Runtime state includes entity queues, runqueue lists/rb-trees, scheduler fence contexts and deadlines, dependency xarrays, pending/done job lists, workqueues, timeout work, credit counters, hang karma, ready/stopped flags, client IDs, and guilty tracking. It is all in-memory scheduling state and is destroyed by entity/scheduler teardown.

## Dependencies and integration points
The header depends on dma-fence, dma-fence-chain via dependencies, xarray, completions, workqueues, reservation objects, GEM objects, DRM files/syncobjs, and the single-producer/single-consumer queue helper. It is a core integration point for GPU command submission drivers.

## Risks and test signals
Risks include unclear entity locking noted by FIXME comments, scheduler-list modification races, incorrect fence reference ownership from `run_job`, dependency cycles or missed implicit dependencies, credit accounting deadlocks, timeout recovery that violates dma-fence rules, resubmission after reset, job cancellation without signaling fences, and use-after-free during entity flush/fini. Test signals include priority scheduling, dependency ordering, syncobj and reservation dependencies, timeout/reset recovery, stop/start/resubmit paths, scheduler fini with queued jobs, pending iterator lock assertions, credit-limit saturation, fence deadline propagation, and multi-scheduler load balancing.
