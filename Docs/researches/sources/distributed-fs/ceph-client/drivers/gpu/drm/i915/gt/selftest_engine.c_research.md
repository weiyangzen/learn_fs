# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_engine.c

Purpose: acts as the top-level live engine selftest dispatcher for the i915 GT engine PM tests.

Important APIs/functions: `intel_engine_live_selftests()` iterates a NULL-terminated function table currently containing `live_engine_pm_selftests()`.

Control flow: the entry point obtains the primary GT with `to_gt(i915)`, calls each registered engine-level live selftest function in order, and returns immediately on the first error.

State and persistence behavior: this file owns no persistent state. It only sequences tests that may manipulate GT or engine state internally.

Dependencies and integration points: includes `i915_selftest.h` and `selftest_engine.h`. It is part of the i915 selftest registration surface and bridges drm device-private state to GT-oriented test functions.

Risks: the simple dispatcher means a failure in an early registered suite prevents later suites from running. Adding tests here changes live selftest ordering and may affect CI runtime or state contamination between suites.

Test signals: pass/fail is the return value from `live_engine_pm_selftests()`, with no additional logging in this wrapper.
