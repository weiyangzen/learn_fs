<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.h

## Purpose
Declares scheduler-node, dependency, priority-list, and scheduler-engine helper APIs used by i915 request submission backends.

## Important APIs, types, and functions
- Priolist iteration macros: `priolist_for_each_request()` and `priolist_for_each_request_consume()`.
- Node APIs: init, reinit, add dependency, finish, and schedule.
- Priolist APIs: lookup and free helpers.
- Scheduler-engine APIs: create, get, put, empty/reset checks, active tasklet lock/unlock helpers, disabled check, and module init/exit.
- Debug API: `i915_request_show_with_schedule()`.

## Control flow
Most control flow is inline reference counting, empty checks, and tasklet lock discipline. `i915_sched_engine_active_lock_bh()` disables bottom halves and locks the tasklet to prevent local softirq recursion while manipulating active submission state.

## State and persistence
No additional state is stored here beyond the structures declared in `i915_scheduler_types.h`. Refcount helpers control scheduler-engine lifetime through `kref`.

## Dependencies and integration points
Depends on list/bit/kernel helpers, scheduler types, and i915 tasklet wrappers. Included by request code, GT engine backends, and debug paths.

## Risks
Tasklet locking helpers must pair bottom-half disable/enable correctly. Priolist free must avoid freeing the embedded normal-priority list. Backends must honor scheduler-engine lifetime with get/put.

## Test signals
Build coverage, lockdep on tasklet/bottom-half regions, scheduler-engine lifetime tests, and backend queue manipulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scheduler.h -->
