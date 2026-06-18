<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.c

## Purpose
`intel_breadcrumbs.c` implements i915 request completion notification. It tracks contexts with requests waiting for breadcrumb signaling, lazily arms engine interrupts, runs bottom-half work through `irq_work`, signals dma fences, and removes completed/canceled waiters.

## Important APIs, Types, and Functions
Public functions include `intel_breadcrumbs_create()`, `intel_breadcrumbs_reset()`, `__intel_breadcrumbs_park()`, `intel_breadcrumbs_free()`, `i915_request_enable_breadcrumb()`, `i915_request_cancel_breadcrumb()`, `intel_context_remove_breadcrumbs()`, and `intel_engine_print_breadcrumbs()`. Important internals include `__intel_breadcrumbs_arm_irq()`, `intel_breadcrumbs_disarm_irq()`, `add_signaling_context()`, `remove_signaling_context()`, `signal_irq_work()`, `irq_signal_request()`, and `insert_breadcrumb()`.

## Control Flow
When a waiter enables a breadcrumb, active incomplete requests are inserted into the context's ordered `signals` list under `ce->signal_lock`; the context is added to the breadcrumb `signalers` RCU list when the first request appears. IRQ work drains already-signaled requests from an llist, walks signaling contexts in RCU read-side critical sections, stops at the first incomplete request per context, removes completed requests, and then signals dma fences outside the context signal lock. Interrupts are armed lazily when signalers exist and disarmed after an interrupt interval with no listeners or when the engine parks.

## State and Persistence
State is stored in `struct intel_breadcrumbs`: reference count, active count, `signalers`, `signaled_requests`, IRQ lock/work state, interrupt enable count, wakeref token, and engine hooks. Requests persist list membership through `rq->signal_link`, `rq->signal_node`, and `I915_FENCE_FLAG_SIGNAL`; contexts are held by reference while they appear in `signalers`.

## Dependencies and Integration Points
The file depends on dma-fence internals, request completion helpers, timeline retirement, engine IRQ enable/disable hooks, GT PM wakerefs, RCU lists, spinlocks, and irq_work. It integrates with request wait paths, engine interrupt handlers via `intel_engine_signal_breadcrumbs()`, context teardown, request retirement, and debug dumping.

## Risks and Edge Cases
Concurrency is the primary risk. The code must avoid signaling callbacks while holding `ce->signal_lock`, keep RCU list removal safe, balance request/context references, and avoid disabling interrupts while a waiter can still appear. Already-completed requests are fast-pathed into `signaled_requests`. Park/free paths must ensure IRQ work is drained and no signalers remain.

## Test Signals
Useful tests cover many waiters on one context, waiters across contexts, request completion racing with enable/cancel, engine park/unpark, interrupt storms, fence callback reentrancy, context removal with completed signals, and debug assertions for empty signaler lists at free time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_breadcrumbs.c -->
