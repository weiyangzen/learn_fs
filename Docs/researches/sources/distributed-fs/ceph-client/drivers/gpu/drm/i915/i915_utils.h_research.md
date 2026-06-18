<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.h

## Purpose
Declares common i915 utility macros and helpers used across the driver.

## Important APIs, types, and functions
- Diagnostic/logging helpers: `MISSING_CASE()`, `i915_probe_error()`, `add_taint_for_CI()`, and `__add_taint_for_CI()`.
- Generic helpers: `fetch_and_zero()`, `check_user_mbz()`, `__mask_next_bit()`, and `is_power_of_2_u64()`.
- Environment/platform helpers: `i915_run_as_guest()`, `i915_vtd_active()`, and `i915_direct_stolen_access()`.

## Control flow
Most helpers are macros/inlines. `check_user_mbz()` safely reads a user field and requires zero. `i915_run_as_guest()` uses x86 hypervisor detection when available and returns false on unsupported architectures.

## State and persistence
No local state is stored. Some helpers mutate pointed-to variables (`fetch_and_zero`, `__mask_next_bit`) or global kernel taint state.

## Dependencies and integration points
Depends on Linux overflow, scheduler, string, workqueue, sched clock, user access through callers, optional x86 hypervisor APIs, and DRM/i915 private declarations. Included broadly across i915.

## Risks
Macros evaluate pointer arguments in ways callers must understand. `fetch_and_zero()` is not atomic. `check_user_mbz()` must only be used with user pointers. Guest detection fallback can be conservative only on x86.

## Test signals
Build coverage, sparse/user-pointer checking, ioctl reserved-field tests, taint-state tests, and platform/guest detection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_utils.h -->
