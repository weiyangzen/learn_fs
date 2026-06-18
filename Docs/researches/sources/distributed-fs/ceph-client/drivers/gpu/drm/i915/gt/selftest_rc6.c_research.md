# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rc6.c Research

Purpose: this file tests RC6 low-power residency behavior and a context-info workaround path that reads `GEN8_RC6_CTX_INFO` without causing reset.

Important APIs/types/functions: `rc6_residency()` sums RC6/RC6p/RC6pp residency. `live_rc6_manual()` manually disables RC6, samples residency/power, parks into RC6, verifies residency and power reduction, and unparks. `__live_rc6_ctx()` emits an SRM of `GEN8_RC6_CTX_INFO` into a request HWSP, `randomised_engines()` builds a shuffled engine list, and `live_rc6_ctx_wa()` runs the context-info poke twice per engine.

Control flow: manual RC6 testing skips disabled RC6 and Valleyview/Cherryview PCU-driven RC6. It takes runtime PM, disables RC6, sleeps, validates residency does not rise, optionally measures RAPL power, parks RC6, sleeps again, verifies residency rose, compares RC6 power against RC0 power, then unparks. The context workaround test creates sacrificial contexts per engine, submits a register-store request, waits for GT idle/PM idle, logs the value, and asserts engine reset counters did not change.

State and persistence: the test temporarily changes RC6 state with `__intel_rc6_disable()`, `intel_rc6_park()`, and `intel_rc6_unpark()`, holds runtime PM, reads forcewake-visible registers, samples RAPL energy, creates contexts, and observes reset counters. It should restore RC6 before returning from the normal manual path.

Dependencies/integration: it depends on RC6 residency APIs, RPS frequency reads, librapl, engine PM, ring command emission, timeline HWSP offsets, i915 reset counters, and GT idle waits. It is generation-gated for context-info reads and platform-gated for manual RC6 control.

Risks and test signals: timing and power measurements can be noisy, so power validation only runs when librapl is supported. Pass signals are no residency accumulation while disabled, increasing residency while parked, RC6 power not exceeding half RC0 power, and no reset count increment after context-info reads. Failures taint CI on reset-needed context-info paths.
