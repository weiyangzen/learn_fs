# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_runtime_pm.h

Purpose: Declares the runtime PM state object, wakeref counting model, assertion helpers, public get/put API, and scoped `with_intel_runtime_pm*` macros used throughout i915.

Important APIs/types: `struct intel_runtime_pm` holds `wakeref_count`, `kdev`, availability flags, lmem userfault list/lock, `userfault_wakeref`, and optional debug tracker. Counter helpers `intel_rpm_raw_wakeref_count()` and `intel_rpm_wakelock_count()` decode the biased atomic. Assertions include `assert_rpm_device_not_suspended()`, `assert_rpm_raw_wakeref_held()`, and `assert_rpm_wakelock_held()`. Temporary assertion bypass helpers are `disable_rpm_wakeref_asserts()` and `enable_rpm_wakeref_asserts()`.

Control flow: Header macros provide for-loop scoped acquisition/release wrappers for unconditional, in-use, and active-only runtime PM references. In non-debug builds, `intel_runtime_pm_put()` is an inline wrapper around unchecked put; in debug builds it requires the tracked wakeref cookie.

State/persistence: The lower half of `wakeref_count` tracks raw refs while the upper half tracks wakelock refs by adding `INTEL_RPM_WAKELOCK_BIAS`. This allows single-atomic assertions for both "device must be on" and "caller holds a wakelock-class ref." `no_wakeref_tracking` can disable debug tracking without disabling runtime PM itself.

Dependencies/integration: Includes `intel_wakeref.h` and Linux runtime PM. Display code receives `i915_display_rpm_interface` from the implementation file. Any caller that touches hardware must use these APIs or display power-domain equivalents.

Risks: The bypass helpers artificially add/subtract both raw and wakelock counts, so imbalance can hide real missing refs. `get_noresume()` is only valid when an active wakeref is already held. The raw accessors intentionally avoid wakelock assertion coverage and increase misuse risk.

Test signals: Assertions warn on suspended-device access or missing refs. Debug builds can print active ref trackers through `print_intel_runtime_pm_wakeref()`. Suspend/resume selftests and runtime PM paths are the main coverage.
