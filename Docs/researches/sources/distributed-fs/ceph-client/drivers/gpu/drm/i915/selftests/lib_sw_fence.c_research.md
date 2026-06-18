# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/lib_sw_fence.c

Purpose: implements small software-fence helpers used by i915 selftests to create on-stack, timer-backed, and heap-backed `i915_sw_fence` objects.

Important APIs/functions: `__onstack_fence_init()` initializes a stack fence waitqueue, pending count, error field, and no-op notify callback. `onstack_fence_fini()` commits and finalizes an initialized on-stack fence. `timed_fence_init()` creates an on-stack timer and either schedules a wake at `expires` or commits immediately. `timed_fence_fini()` cancels/destroys the timer and finalizes the fence. `heap_fence_create()` allocates a heap fence with a kref-backed lifetime and `heap_fence_put()` releases references through `heap_fence_release()`.

Control flow and state: on-stack fences are explicitly initialized and finalized by the caller. Timed fences transition to committed state from the timer callback `timed_fence_wake()` or synchronously if the expiration is in the past. Heap fences hold two references: one for the creator and one released when the fence free notification arrives. Final memory release uses `kfree_rcu()`.

Dependencies and integration: integrates with `../i915_sw_fence.h`, Linux timers, krefs, RCU freeing, and lockdep waitqueue classes through the header macro.

Risks: timer-backed fences require `timed_fence_fini()` to avoid on-stack timer lifetime bugs. Heap fences rely on the notify callback receiving `FENCE_FREE`; mismatched ref ownership can leak or prematurely free test fences.

Test signals: expected behavior is that selftests can create delayed dependencies, wait on them, and finalize without lockdep, timer, or refcount warnings.
