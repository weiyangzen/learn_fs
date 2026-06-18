# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reset.c

## Purpose
This file coordinates display state preservation and restoration around GPU/display reset. It provides the modeset-side reset hooks that stop active CRTCs safely, keep a duplicated atomic state for restoration, reinitialize display hardware when needed, and release the modeset locks acquired during reset preparation.

## Important APIs, Types, and Functions
`intel_display_reset_test()` returns `display->params.force_reset_modeset_test` for test-only reset behavior. `intel_display_reset_prepare()` is the main prepare hook and takes a `modeset_stuck_fn` callback for wedging a stuck modeset. `intel_display_reset_finish()` resumes from the duplicated state, either by committing it directly for test-only reset or by reinitializing display hardware and invoking the full display resume path. It uses `display->restore.reset_ctx`, `display->restore.modeset_state`, and `display->restore.pending_fb_pin`.

## Control Flow
Preparation exits early when `HAS_DISPLAY()` is false. If a framebuffer pin is pending, it calls the supplied stuck callback. It then locks `mode_config.mutex`, initializes a modeset acquire context, repeatedly locks all modeset locks with deadlock backoff, duplicates DRM atomic state, disables all CRTCs, and stores the duplicated state. Finish fetches and clears the saved state, unlocks directly if none exists, commits duplicated state for test-only reset, or runs the full hardware reinit sequence: PPS register unlock workaround, display hardware init, clock-gating init, CX0 PLL power-save workaround, HPD init, display driver resume, and HPD polling disable.

## State and Persistence Behavior
The saved atomic state persists between prepare and finish through `display->restore.modeset_state`; `fetch_and_zero()` prevents double restoration. The modeset acquire context persists across the reset window and must be finalized exactly once. Hardware state is intentionally disabled before reset and either restored directly or reconstructed through hardware reinitialization.

## Dependencies and Integration Points
The code depends on DRM atomic helpers, modeset locking, `intel_display_driver`, `intel_clock_gating`, `intel_cx0_phy`, `intel_hotplug`, `intel_pps`, `intel_display_utils`, and `intel_display_types`. It is called by higher-level reset paths that decide whether display hardware was actually reset.

## Risks
Error paths after lock acquisition still require `intel_display_reset_finish()` to release locks, so callers must honor the boolean return contract. Failed state duplication or disable leaves the reset lane with locks held but no saved state. Deadlock handling depends on the DRM modeset acquire context. Reinitializing hardware in the non-test path must happen before resume, or restored state may program stale power/clock/HPD state.

## Test Signals
Test signals include forced reset modeset tests, GPU reset with active displays, reset with pending framebuffer pin, suspend/resume adjacent to reset, no modeset lock leaks or `-EDEADLK` warnings, successful state restore, working hotplug after reset, and no persistent blank display after display-engine reset.
