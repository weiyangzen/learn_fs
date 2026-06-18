<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_selftest.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_selftest.h

## Purpose
Defines the i915 selftest configuration, declarations, and conditional macros used to compile mock, live, and performance selftests into the driver.

## Important APIs, types, and functions
- `struct i915_selftest` stores timeout, random seed, filter, and mock/live/perf switches.
- When enabled, declares `i915_mock_selftests()`, `i915_live_selftests()`, `i915_perf_selftests()`, generated test functions from selftest headers, `struct i915_subtest`, setup/teardown helpers, and `__i915_subtests()`.
- Macros include `i915_subtests()`, `i915_live_subtests()`, `intel_gt_live_subtests()`, `SUBTEST()`, `I915_SELFTEST_DECLARE()`, `I915_SELFTEST_ONLY()`, `I915_SELFTEST_EXPORT`, `IGT_TIMEOUT()`, and `igt_timeout()`.
- Always declares `__igt_timeout()` and `igt_hexdump()`.

## Control flow
With selftests enabled, included lists of selftest declarations expand through a temporary `selftest(name, func)` macro. Live test wrappers clear GuC scheduler disable delay before invoking the common subtest runner. Without selftests, public entry points become no-op inline stubs and selftest-only declarations disappear.

## State and persistence
Global `i915_selftest` persists module-wide when configured. Timeout values, filters, and flags control test execution. `I915_SELFTEST_DECLARE()` conditionally adds fields to production structures only in selftest builds.

## Dependencies and integration points
Depends on kernel fault injection when enabled, PCI/DRM i915 private types, selftest declaration headers, and intel-gpu-tools conventions. Included broadly by i915 modules that expose selftest-only state or compile local selftest C files.

## Risks
Selftest-only fields must not leak into production ABI assumptions. Generated declarations depend on included selftest headers matching the expected function signatures. Live tests manipulate hardware and need robust setup/teardown to avoid leaving the device wedged.

## Test signals
Running mock/live/perf selftests through the i915 test runner, timeout handling through `igt_timeout()`, filter selection, fault-injection tests, and production builds with selftests disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_selftest.h -->
