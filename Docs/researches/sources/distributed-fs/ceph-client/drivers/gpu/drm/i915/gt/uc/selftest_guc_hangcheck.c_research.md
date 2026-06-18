# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc_hangcheck.c

Purpose: live selftest that verifies a hung or reset GuC is detected by engine heartbeat and causes a recorded GPU reset, after which simple work still completes.

Important APIs/types/functions: `nop_request()` creates a kernel no-op request. `intel_hang_guc()` is the subtest and `intel_guc_hang_check()` registers it. It uses `kernel_context()`, `intel_engine_set_heartbeat()`, `igt_spinner`, `intel_reset_guc()`, `GUC_STATUS`, `GS_MIA_IN_RESET`, `i915_reset_count()`, and `intel_selftest_wait_for_rq()`.

Control flow: the test creates a kernel context and an engine context, saves the current reset count and heartbeat interval, sets a short heartbeat, starts a spinner request, explicitly resets the GuC, checks the GuC reset status bit, waits for heartbeat-driven recovery, and verifies the global reset count changed. It then submits a no-op request to prove the engine can still execute.

State and persistence: transient state includes the heartbeat interval, spinner request, context references, runtime PM wakeref, and reset count snapshot. Cleanup ends the spinner, restores heartbeat, releases requests/context, closes the kernel context, and drops the wakeref.

Dependencies and risks: depends on GuC submission, engine heartbeat, reset machinery, GT uncore reads, and selftest scheduler helpers. Risks include heartbeat timing sensitivity, false negatives when no engine is present, and cleanup ordering after reset failures. Test signals are skipped execution on wedged or non-GuC systems, reset-count increment, and successful post-reset no-op completion.
