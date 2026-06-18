# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_suspend.c

Purpose: preserves and restores Valleyview Gunit state across runtime/system suspend paths involving D3 and S0ix transitions.

Important APIs/functions: `vlv_suspend_init()` allocates `i915->vlv_s0ix_state` for Valleyview; `vlv_suspend_cleanup()` frees it. `vlv_suspend_complete()` waits for GT wells off, verifies context bits, disables GT wake, saves Gunit state, and releases forced clock. `vlv_resume_prepare()` forces the GFX clock, restores state, re-enables GT wake, clears force clock, checks access errors, and optionally reinitializes clock gating. Internal helpers save/restore many GAM, MBC, GCP, GPM, display CZ, GT SA, and Gunit-display registers.

Control flow and state: `struct vlv_s0ix_state` is the persistent suspend snapshot. Save reads a curated list of registers before the device enters deeper low-power states. Restore writes them back, preserving wake/force-clock bits controlled by the caller via masked RMW. Wake/clock helpers poll hardware status with short timeouts.

Dependencies and integration: depends on i915 uncore register access, GT register definitions, wait utilities, trace hooks, clock-gating init, and VLV/CHV platform checks. It integrates with suspend/resume and runtime-PM sequences.

Risks: register lists are hardware-specific and intentionally broad; missing a required register can cause resume failures, while restoring caller-controlled bits can disrupt the suspend sequence. Timeout handling tries to continue on resume but can leave runtime PM disabled by returning the first error.

Test signals: suspend/resume on VLV/CHV should complete without GT access errors, force-clock timeouts, wake-ack timeouts, or post-resume display/GT instability.
