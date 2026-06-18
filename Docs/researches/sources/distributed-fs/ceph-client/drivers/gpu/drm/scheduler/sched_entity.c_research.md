## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_entity.c

### Purpose

`sched_entity.c` implements DRM scheduler entities: per-context software queues that own ordered jobs before the scheduler moves them to hardware. It handles entity initialization, scheduler selection, job push/pop, dependency blocking, priority updates, flush/fini/destroy, killed-process cleanup, and guilty-context cancellation.

### Important APIs, Types, and Functions

Exported APIs are `drm_sched_entity_init()`, `drm_sched_entity_modify_sched()`, `drm_sched_entity_error()`, `drm_sched_entity_flush()`, `drm_sched_entity_fini()`, `drm_sched_entity_destroy()`, `drm_sched_entity_set_priority()`, and `drm_sched_entity_push_job()`. Internal helpers include `drm_sched_entity_is_idle()`, `drm_sched_entity_kill()`, `drm_sched_entity_kill_jobs_work()`, `drm_sched_entity_wakeup()`, `drm_sched_entity_add_dependency_cb()`, `drm_sched_job_dependency()`, `drm_sched_entity_pop_job()`, and `drm_sched_entity_select_rq()`.

### Control Flow

Drivers initialize an entity with one or more schedulers and a priority. Jobs are initialized/armed in `sched_main.c`, then `drm_sched_entity_push_job()` timestamps and queues them in the SPSC queue. The first job adds the entity to its runqueue and wakes the scheduler. When `sched_main.c` selects the entity, `drm_sched_entity_pop_job()` checks explicit xarray dependencies and backend `prepare_job()` dependencies. Unsatisfied dependencies install a DMA fence callback and make the entity temporarily not ready; the callback clears `entity->dependency` and wakes the scheduler.

Scheduler selection for multi-engine entities happens only when the entity queue is empty and the last scheduled fence is signaled. This keeps an entity's ordered jobs on the same engine while prior work is outstanding. Flush waits for the queue to drain or, on SIGKILL process exit, kills remaining queued jobs after dependencies finish to avoid data corruption.

### State and Persistence Behavior

Persistent entity state includes `rq`, scheduler list, priority, SPSC job queue, fence context pair, sequence counter, last scheduled finished fence under RCU, dependency fence/callback, last user task, idle completion, stopped flag, guilty pointer, and FIFO rb-tree node timestamp. Jobs are popped from the entity queue before hardware submission and then have `job->entity` nulled because entity and job lifetimes diverge.

### Dependencies and Integration Points

This file depends on `drm/gpu_scheduler.h`, `sched_internal.h`, DMA fences, xarrays, completions, RCU, SPSC queues, scheduler tracepoints, and runqueue helpers implemented in `sched_main.c`. Backends provide optional `prepare_job()` and mandatory free paths used during kill cleanup.

### Risks and Edge Cases

Ordering relies on the documented common lock around `drm_sched_job_arm()` and `drm_sched_entity_push_job()`. Dependency callbacks race with entity teardown, so `fini()` must remove callbacks and drop references carefully. Same-entity fences are ignored to avoid self-deadlock; changing fence contexts can break that logic. Killed-job cleanup deliberately waits for dependencies, which can delay teardown but prevents memory corruption. Priority changes update only `entity->priority`; callers must understand when runqueue placement changes. Pushing to a stopped entity logs an error after the job was queued, so driver lifetime ordering matters.

### Test Signals

Important tests cover entity init with invalid scheduler lists, multi-scheduler selection, FIFO and RR queue ordering, dependency callback wakeups, same-entity dependency elision, priority changes, guilty entity cancellation, SIGKILL flush cleanup, entity destroy with pending dependencies, and lockdep around entity/rq locks. KUnit scheduler tests and real driver workloads with syncobj/reservation dependencies are the strongest signals.
