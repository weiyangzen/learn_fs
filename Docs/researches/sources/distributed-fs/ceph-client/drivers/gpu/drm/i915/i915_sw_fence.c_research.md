<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.c

## Purpose
Implements i915 software fences: lightweight N:M synchronization points used to gate request submission and other asynchronous driver work before dma-fence signaling.

## Important APIs, types, and functions
- Initialization/lifecycle: `__i915_sw_fence_init()`, `i915_sw_fence_reinit()`, `i915_sw_fence_commit()`, optional `i915_sw_fence_fini()`, and `i915_sw_fence_complete()`.
- Dependency APIs: `i915_sw_fence_await()`, `i915_sw_fence_await_sw_fence()`, `i915_sw_fence_await_sw_fence_gfp()`, `i915_sw_fence_await_dma_fence()`, `__i915_sw_fence_await_dma_fence()`, and `i915_sw_fence_await_reservation()`.
- Internal wake paths include `i915_sw_fence_wake()`, dma-fence callback wakeups, timer timeout wakeups, and optional DAG checking/debug object hooks.

## Control flow
A fence starts with `pending = 1`. Awaiting another software or dma fence increments pending and registers a wait entry/callback. Committing completes the initial pending count; when the count reaches zero, the notifier receives `FENCE_COMPLETE`. If it returns `NOTIFY_DONE`, all waiters are woken without unbounded recursion by moving nested fence waiters into continuation lists. The fence then transitions to done (`pending = -1`), debug state is destroyed, and the notifier receives `FENCE_FREE`.

DMA-fence waits attach callbacks and optionally arm a timer. On dma completion or timeout, the software fence records the dma error or `-ETIMEDOUT` once and completes. Reservation waits iterate all relevant fences under `dma_resv_iter`.

## State and persistence
`struct i915_sw_fence` stores a waitqueue, notifier callback, optional debug flags, atomic pending count, and first error. Dynamically allocated wait entries/callbacks persist until their signaler completes. Timer callbacks hold dma-fence references and release them through irq work.

## Dependencies and integration points
Depends on waitqueues, dma-fence, dma-resv, timers, irq work, debug objects, and i915 selftests. Used heavily by `i915_request` submit/semaphore fences, fenced work, HuC waits, and other internal dependency chains.

## Risks
Correctness depends on pending-count transitions, acyclic software-fence graphs, callback lifetime, and wake continuation handling. Adding awaits after a fence is signaled is rejected. Timeout callbacks and dma callbacks race through `xchg()` to avoid double completion. Error propagation is first-error-wins.

## Test signals
Selftests under `selftests/lib_sw_fence.c` and `selftests/i915_sw_fence.c`, DAG-checking builds, debug-object validation, dma-fence timeout tests, reservation-object wait tests, and request submission dependency stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_sw_fence.c -->
