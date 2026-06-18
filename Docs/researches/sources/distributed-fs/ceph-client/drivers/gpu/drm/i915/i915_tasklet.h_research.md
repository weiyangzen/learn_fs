<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_tasklet.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_tasklet.h

## Purpose
Provides small wrappers around Linux tasklet state used by i915 scheduler/submission code.

## Important APIs, types, and functions
- `tasklet_lock()` spins until `tasklet_trylock()` succeeds.
- `tasklet_is_locked()` tests `TASKLET_STATE_RUN`.
- `__tasklet_disable_sync_once()` increments the disable count and waits for a running tasklet only on the first disable.
- `__tasklet_is_enabled()`, `__tasklet_enable()`, and `__tasklet_is_scheduled()` expose count and scheduled-state checks.

## Control flow
The helpers are inline. Locking uses CPU relax in a spin loop. Disable/enable operate on the tasklet count directly and rely on the kernel tasklet state machine.

## State and persistence
No state is owned by this header. It reads and mutates `struct tasklet_struct` state bits and count in caller-owned tasklets.

## Dependencies and integration points
Depends on Linux interrupt/tasklet APIs. Used by i915 scheduler-engine helpers and backend tasklet control.

## Risks
These are low-level wrappers around internal tasklet fields. Mispaired disable/enable or spinning with inappropriate locks held can deadlock or starve softirq progress.

## Test signals
Lockdep, tasklet submission stress, scheduler active-lock tests, and softirq recursion/preemption tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_tasklet.h -->
