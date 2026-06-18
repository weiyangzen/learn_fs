# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/intel_uncore.c

Purpose: provides i915 uncore selftests for forcewake range tables, shadow-register ranges, and selected live forcewake behavior. It validates that static MMIO/forcewake metadata is ordered, valid, and watertight where newer platforms require contiguous coverage.

Important APIs/functions: `intel_fw_table_check()` checks `intel_forcewake_range` arrays for ascending order, positive length, and optional watertightness. `intel_shadow_table_check()` validates `i915_mmio_range` lists for Gen8, Gen11, Gen12, DG2, MTL, and XeLPM+ shadowed registers. `intel_uncore_mock_selftests()` runs pure table validation. `live_fw_table()` validates the runtime GT forcewake table. `live_forcewake_ops()` is a disabled-by-default broken selftest that probes forcewaked engine registers. `intel_uncore_live_selftests()` registers the live subtests.

Control flow and state: mock tests iterate over compile-time arrays and return immediately on the first malformed range. Live tests run through `intel_gt_live_subtests()`, take a runtime-PM wakeref, manually flush forcewake release timers, read a chosen engine register while forcewake is held, then expect the raw MMIO value to drop to zero once forcewake is released. The live forcewake test skips Valleyview/Cherryview and is gated behind `CONFIG_DRM_I915_SELFTEST_BROKEN`.

Dependencies and integration: depends on i915 selftest harness, `intel_gt`, uncore forcewake internals, runtime PM, engine iteration, hrtimer release, and MMIO helpers. It protects core uncore tables used by normal register access paths.

Risks: forcewake behavior is hardware- and platform-sensitive; the live test documents unreliability and external powerwell interference. Table validation can catch regressions early, but a false watertight flag or missing platform table will fail broad test runs.

Test signals: `intel_uncore_mock_selftests()` should pass without hardware. Live signals include nonzero register reads under forcewake, zero after forcewake release, and valid runtime forcewake table ordering.
