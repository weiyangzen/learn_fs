<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.h

## Purpose
`intel_engine_pm.h` provides inline engine PM wakeref helpers and declares engine PM initialization/reset functions.

## Important APIs, Types, and Functions
Important helpers include `intel_engine_pm_is_awake()`, `__intel_engine_pm_get()`, `intel_engine_pm_get()`, `intel_engine_pm_get_if_awake()`, `intel_engine_pm_might_get()`, `intel_engine_pm_put()`, `intel_engine_pm_put_async()`, `intel_engine_pm_put_delay()`, `intel_engine_pm_flush()`, `intel_engine_pm_might_put()`, and `intel_engine_create_kernel_request()`. Declarations include `intel_engine_init__pm()` and `intel_engine_reset_pinned_contexts()`.

## Control Flow
The inlines delegate to `intel_wakeref` and GT PM helpers. Virtual engines fan out `might_get`/`might_put` to physical sibling wakerefs. `intel_engine_create_kernel_request()` wraps `i915_request_create(engine->kernel_context)` with an explicit engine PM get/put because the kernel context is also used inside the engine-PM barrier.

## State and Persistence
The helpers mutate `engine->wakeref` counts and, for virtual engines, physical sibling wakeref expectations plus GT PM expectations. Kernel request creation persists a request on the engine's perma-pinned kernel context.

## Dependencies and Integration Points
The header depends on driver/request/engine/GT PM and wakeref types. It is used by context code, heartbeat, breadcrumbs, SSEU reconfiguration, request creation, and engine PM implementation.

## Risks and Edge Cases
Kernel context requests outside the PM barrier must take a PM reference or race with park/unpark. Virtual engines require special handling because their PM state maps to several physical engines. `get_if_awake()` callers must tolerate a false result without forcing wake.

## Test Signals
Signals include PM reference balance, virtual-engine wakeref propagation, kernel request creation while engines park/unpark, and flush waiting for delayed wakeref puts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_engine_pm.h -->
