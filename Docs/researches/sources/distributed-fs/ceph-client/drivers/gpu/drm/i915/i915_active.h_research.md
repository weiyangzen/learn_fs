<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.h

### Purpose
`i915_active.h` is the public interface for i915 active fence and composite active tracking. It documents why i915 treats requests as synchronization fences and exposes helpers to set, get, wait on, await, acquire, release, and allocate active trackers.

### Important APIs, Types, And Functions
The header defines `__i915_active_fence_init()`, `INIT_ACTIVE_FENCE`, `i915_active_fence_get()`, `i915_active_fence_isset()`, the `i915_active_init()` lock-class wrapper, `i915_active_wait()`, `__i915_active_acquire()`, `i915_active_is_idle()`, and `__i915_request_await_exclusive()`. It declares all implemented APIs in `i915_active.c` and flags `I915_ACTIVE_AWAIT_EXCL`, `I915_ACTIVE_AWAIT_ACTIVE`, and `I915_ACTIVE_AWAIT_BARRIER`.

### Control Flow
Consumers initialize embedded trackers, acquire an active phase before associating GPU requests, add timeline or exclusive fences, and release when their update is complete. Waiters either block until idle or attach request/software-fence waits to the currently tracked fences. Inline getters use RCU to safely reference the current fence.

### State, Persistence, And Dependencies
The header includes `i915_active_types.h` and `i915_request.h`, and forward-declares request, engine, and timeline types. The persistent state is the `struct i915_active` or `struct i915_active_fence` embedded by callers.

### Integration Points
This is included by GEM, VMA, request, scheduler, and resource lifetime code that needs implicit GPU activity synchronization. `__i915_request_await_exclusive()` is a small convenience used when a request must wait for a resource's exclusive active fence.

### Risks
The documentation highlights a common naming trap: these are dma-fence synchronization objects, not i915 hardware fence registers. `i915_active_fence_isset()` can report stale idle fences because retirement is lazy. Callers using `__i915_active_acquire()` must already hold an active reference.

### Test Signals
Compile coverage across i915 users, lockdep class separation from `i915_active_init()`, RCU fence getter tests, and request await ordering tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_active.h -->
