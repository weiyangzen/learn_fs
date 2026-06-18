# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_selftest.c

## Purpose
This file is the central i915 selftest runner. It expands mock, live, and perf registries into dispatch tables and module parameters, manages global selftest seed/timeout/filter state, runs selected tests, provides subtest setup/teardown helpers, and supplies diagnostics such as timeout checks and hex dumps.

## Important APIs, Types, And Functions
- Global `struct i915_selftest i915_selftest` stores timeout, seed, filter, and lane enable flags.
- `i915_mock_selftests()`, `i915_live_selftests()`, and `i915_perf_selftests()` are lane entry points.
- `__run_selftests()` seeds randomness, computes timeout jiffies, enables all tests when none are explicitly enabled, logs configuration, and invokes table entries.
- `apply_subtest_filter()` parses `st_filter` tokens, including `caller/name` and `!` exclusions.
- Setup/teardown helpers include `__i915_nop_setup`, `__i915_live_setup`, `__i915_live_teardown`, `__intel_gt_live_setup`, and `__intel_gt_live_teardown`.
- `__i915_subtests()` runs individual `struct i915_subtest` entries with filtering and setup/teardown.
- `__igt_timeout()` and `igt_hexdump()` are shared diagnostics.

## Control Flow
The file includes registry headers multiple times with different `selftest` macro definitions to create enum values, arrays, and module parameters. Lane entry points check whether their lane is enabled, wait for required GSC proxy/HuC flows for live/perf, then call `run_selftests()`. Subtest execution checks signals, applies filters, calls setup, runs the subtest, then calls teardown. Live teardown flushes GT state and drains freed GEM objects.

## State And Persistence
Selftest state is module-parameter-backed and persists for the loaded module: `st_random_seed`, `st_timeout`, `st_filter`, and lane flags. Runtime state includes computed `timeout_jiffies`. Live execution temporarily disables render powergating on selected platforms and waits for firmware/component initialization. The runner records failure errnos into lane flags for later module-load behavior.

## Dependencies And Integration Points
It depends on i915 driver, GT PM, firmware proxy/HuC state, reset counters, flush helper, wait utilities, and all registry headers. It is the integration point between kernel module parameters and individual selftest files.

## Risks
Macro inclusion makes registry names/order fragile. Positive errors or `-ENOTTY` from tests conflict with runner magic values and are normalized. Filter parsing assumes allocation succeeds; an allocation failure would make string traversal unsafe only if not handled elsewhere. Live tests assume an idle system and can fail if firmware initialization or power management is still in progress.

## Test Signals
The runner logs seed, timeout, lane name, and each test/subtest name. Failures identify setup, subtest, or teardown stage. `__igt_timeout()` logs optional timeout context and respects pending signals. `igt_hexdump()` compresses repeated rows to keep diagnostic output readable.
