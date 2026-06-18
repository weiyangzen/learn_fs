# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_gt_pm.c

Purpose: implements GT-level power-management live selftests for CS clock calibration, RC6/RPS suites, suspend/resume restore, and late RC6 context-workaround checks.

Important APIs/functions: entry points are `intel_gt_pm_live_selftests()` and `intel_gt_pm_late_selftests()`. Local helpers include `read_timestamp()`, `measure_clocks()`, `live_gt_clocks()`, and `live_gt_resume()`. The suite delegates to `live_rc6_manual`, multiple `live_rps_*` tests, and `live_rc6_ctx_wa` from included selftest headers.

Control flow: `live_gt_clocks()` skips unknown clock frequencies and pre-Gen4 devices, takes a GT wakeref, forces all uncore domains awake, measures engine timestamp deltas over five 1 ms windows with interrupts disabled, converts between GT clock ticks and nanoseconds, and checks both conversion directions within tolerance. `live_gt_resume()` loops until the IGT timeout, running suspend prepare/late, checking RC6 disabled during suspend, resuming GT, checking RC6 restored when supported, and verifying LLC state restoration. Live and late entry points skip wedged GTs and run ordered subtest arrays.

State and persistence behavior: temporarily holds GT PM and uncore forcewake. Suspend/resume test intentionally transitions GT power state and may call `intel_gt_set_wedged_on_init()` on serious restore failures. Late tests are marked as potentially leaving the system undesirable and are intended to run last.

Dependencies and integration points: depends on engine timestamp registers, GT clock conversion helpers, uncore forcewake, GT suspend/resume, RC6/RPS/LLC selftest modules, and i915 live subtest harness.

Risks: clock tests rely on stable `gt->clock_frequency` and CPU timing; inaccurate calibration can produce false failures. Suspend/resume cycling is invasive and can expose or cause broader GT state issues. Late RC6 tests may leave the system in a bad state, so test ordering matters.

Test signals: clock tests log cycles and nanoseconds per engine and fail if CS ticks diverge from wall time beyond tolerance. Resume tests fail if RC6 state is wrong or LLC verification fails. Subordinate RC6/RPS tests provide their own diagnostics.
