# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_wakeref.h

Purpose: Declares wakeref abstractions for refcounted runtime-PM-backed resource lifetime management and debug tracking.

Important APIs/types: `intel_wakeref_t`, `struct intel_wakeref_ops`, `struct intel_wakeref`, `struct intel_wakeref_lockclass`, `struct intel_wakeref_auto`, `intel_wakeref_init()`, `intel_wakeref_get()`, `__intel_wakeref_get()`, `intel_wakeref_get_if_active()`, `intel_wakeref_put()`, `intel_wakeref_put_async()`, `intel_wakeref_put_delay()`, lock/unlock helpers, `intel_wakeref_is_active()`, `__intel_wakeref_defer_park()`, and ref-tracker helpers.

Control flow: Inline get fast path increments `count` if nonzero; first get delegates to the C implementation. Put fast path decrements unless count is one, in which case the C implementation handles last-release callbacks. Delay flags combine async bit and encoded delay. Lock helpers protect first/last callback execution.

State/persistence: `INTEL_WAKEREF_DEF` is a sentinel ref tracker cookie. Optional `CONFIG_DRM_I915_DEBUG_WAKEREF` tracking stores live holders in `wf->debug`. `intel_wakeref_auto` stores a temporary RPM wakeref until timer expiry or fini.

Dependencies/integration: Includes Linux atomic, lockdep, mutex, refcount, ref_tracker, timer, and workqueue APIs. The type is used by runtime PM and many i915 resource lifetime paths.

Risks: `__intel_wakeref_get()` is only valid when already active. `intel_wakeref_wait_for_idle()` waits for third-party holders too and must be used only when ownership is controlled. `__intel_wakeref_defer_park()` manipulates `count` directly and requires the mutex. Misencoded delay flags can corrupt put behavior.

Test signals: Debug ref tracking and leak reports; `i915_active` and other lifetime selftests indirectly cover callback and wait behavior.
