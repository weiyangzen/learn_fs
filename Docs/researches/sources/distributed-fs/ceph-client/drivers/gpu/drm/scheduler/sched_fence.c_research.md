## sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/sched_fence.c

### Purpose

`sched_fence.c` implements `struct drm_sched_fence`, the scheduler's paired DMA-fence abstraction. Each job gets a `scheduled` fence signaled when the job has been submitted to hardware/firmware and a `finished` fence signaled when execution completes or errors.

### Important APIs, Types, and Functions

Exported/internal scheduler functions are `drm_sched_fence_alloc()`, `drm_sched_fence_init()`, `drm_sched_fence_free()`, `drm_sched_fence_scheduled()`, `drm_sched_fence_finished()`, and exported `to_drm_sched_fence()`. Fence operations include driver/timeline name callbacks, release callbacks for scheduled/finished fences, and `drm_sched_fence_set_deadline_finished()` for deadline propagation.

### Control Flow

Module init creates a slab cache for scheduler fences. Job initialization allocates an uninitialized fence object; job arm initializes the scheduled and finished DMA fences with adjacent contexts and the same sequence number. When `run_job()` returns a parent hardware fence, `drm_sched_fence_scheduled()` stores a reference to that parent before signaling the scheduled fence. When the hardware parent signals or an error path completes, `drm_sched_fence_finished()` sets any error and signals the finished fence.

Release is split: the scheduled fence release drops the parent and schedules RCU freeing of the containing `drm_sched_fence`; the finished fence release drops the extra reference held by the scheduled fence. Deadline setting on the finished fence stores the earliest deadline and forwards it to the parent if already known, using acquire/release ordering to handle races with parent installation.

### State and Persistence Behavior

The slab cache persists for the module lifetime. Each scheduler fence persists until both DMA fences and the parent reference are released. Fence state includes owner, DRM client ID for tracing, scheduler pointer, lock, optional parent fence, deadline, and the two embedded DMA fences.

### Dependencies and Integration Points

It depends on Linux DMA fence APIs, RCU, slab caches, module init/exit, and `drm/gpu_scheduler.h`. It is called by `sched_main.c` during job init/arm/run/done and by `sched_entity.c` for dependency classification and killed-job cleanup.

### Risks and Edge Cases

Fence lifetime is subtle because two embedded fences share one allocation. Calling `drm_sched_fence_free()` after initialization is invalid and guarded by `fence->sched`. Parent deadline propagation depends on memory barriers; weakening them can lose deadlines. `to_drm_sched_fence()` checks the ops pointer, so external fences safely return NULL but any ops mismatch breaks scheduler-fence identification. `drm_sched_fence_scheduled()` treats error/NULL parent specially; consumers waiting for parent after scheduled signal must handle no-parent cases.

### Test Signals

Tests should cover allocation failure unwind, unarmed cleanup, armed job completion, error propagation, parent fence callback completion, deadline propagation before and after parent installation, RCU/slab teardown, and `to_drm_sched_fence()` for scheduled, finished, and non-scheduler fences. Lockdep/KASAN help catch release-order issues.
