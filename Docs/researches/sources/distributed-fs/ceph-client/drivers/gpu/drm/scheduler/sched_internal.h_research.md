## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_internal.h

### Purpose

`sched_internal.h` is the private interface shared by the DRM scheduler implementation files. It declares the global scheduling policy, runqueue/entity helpers, scheduler-fence helpers, and tiny queue helpers that are not part of the public DRM scheduler header.

### Important APIs, Types, and Functions

It declares `drm_sched_policy` plus `DRM_SCHED_POLICY_RR` and `DRM_SCHED_POLICY_FIFO`; runqueue helpers `drm_sched_rq_add_entity()`, `drm_sched_rq_remove_entity()`, `drm_sched_rq_update_fifo_locked()`, and `drm_sched_wakeup()`; entity helpers `drm_sched_entity_select_rq()` and `drm_sched_entity_pop_job()`; fence helpers `drm_sched_fence_alloc()`, `drm_sched_fence_init()`, `drm_sched_fence_free()`, `drm_sched_fence_scheduled()`, and `drm_sched_fence_finished()`. Inline helpers pop/peek SPSC queue nodes and test entity readiness.

### Control Flow

There is no standalone runtime flow. `sched_main.c`, `sched_entity.c`, and `sched_fence.c` include this header to call across compilation units without exposing those helpers to drivers.

### State and Persistence Behavior

The header owns no storage except the external declaration of `drm_sched_policy`, which is defined and module-param-controlled in `sched_main.c`. Inline queue helpers operate on entity job queues but do not allocate or persist state.

### Dependencies and Integration Points

It depends on public scheduler types, SPSC queue primitives, DMA fences, and runqueue structures from `drm/gpu_scheduler.h`. It is an internal contract between the scheduler's core files and should evolve with them.

### Risks and Edge Cases

The inline `drm_sched_entity_is_ready()` only checks queue count and current dependency; callers must separately handle credit limits and stopped schedulers. Queue pop/peek assume the node belongs to `struct drm_sched_job`. Changing policy constants affects module parameter semantics and runqueue selection behavior.

### Test Signals

Compile coverage of all scheduler objects validates declarations. Runtime coverage comes indirectly from queue selection, dependency blocking, FIFO/RR policy switching, and fence lifecycle tests.
