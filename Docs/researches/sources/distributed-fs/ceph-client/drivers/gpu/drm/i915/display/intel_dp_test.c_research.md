# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_test.c

## Purpose
Implements DisplayPort compliance test handling for i915. It reads DP CTS requests from DPCD, stores requested test parameters, adjusts modeset link limits and pipe bpp for tests, programs PHY test patterns, handles short-pulse follow-up behavior, and exposes debugfs files for test state.

## Important APIs, types, and functions
- Exported APIs: `intel_dp_test_reset()`, `intel_dp_test_compute_config()`, `intel_dp_test_request()`, `intel_dp_test_phy()`, `intel_dp_test_short_pulse()`, `intel_dp_test_debugfs_register()`.
- Request handlers: `intel_dp_autotest_link_training()`, `intel_dp_autotest_video_pattern()`, `intel_dp_autotest_edid()`, `intel_dp_autotest_phy_pattern()`.
- PHY programming: `intel_dp_process_phy_request()`, `intel_dp_phy_pattern_update()`, `intel_dp_prep_phy_test()`, `intel_dp_do_phy_test()`.
- Debugfs files: `i915_dp_test_data`, `i915_dp_test_type`, and `i915_dp_test_active`.

## Control flow
Short-pulse handling in DP core calls `intel_dp_test_request()` when DPCD indicates a test request. The function reads `DP_TEST_REQUEST`, dispatches to the matching autotest handler, stores parsed parameters in `intel_dp->compliance`, sets `test_active` for tests that need userspace not to interfere, records `test_type` only on ACK, and writes `DP_TEST_RESPONSE`.

During modeset computation, `intel_dp_test_compute_config()` clamps pipe bpp for video-pattern tests and clamps link rate/lane count for link-training tests if the requested params remain valid after fallback limits. For PHY pattern tests, `intel_dp_test_phy()` acquires modeset locks with EDEADLK backoff, finds active DP pipes for the port, uses only the MST master transcoder on display version 12 and newer, reads sink link status, applies requested signal levels, writes DDI PHY pattern registers, updates DPCD lane training set, and calls DRM helper code to set the sink PHY test pattern.

Debugfs active writes iterate connected SST DisplayPort connectors, parse a decimal value, and only value `1` activates compliance testing. Debugfs data/type show the currently stored request data for the connected SST DP connector.

## State and persistence
All test state lives in `intel_dp->compliance`: `test_active`, `test_type`, requested link rate/lane count, video dimensions, bpc, EDID result, and PHY test parameters. PHY pattern programming persists in DDI test-pattern registers and sink DPCD until disabled or reprogrammed. `intel_dp_test_reset()` clears the compliance struct so later requests can be captured cleanly.

## Dependencies and integration points
Depends on DP DPCD test registers, DRM DP PHY test helpers, EDID state, i915 link training helpers, DDI register programming, modeset locking, MST master-transcoder helpers, hotplug events, and debugfs. DP core invokes request/short-pulse handling; mode compute invokes test config adjustment.

## Risks
Compliance code intentionally overrides normal mode/link decisions, so stale `test_active` or `test_type` can disturb regular operation. PHY tests use ad hoc modeset locking and direct register programming, with a FIXME noting they should be integrated into normal modesets. Debugfs iterates only SST DisplayPort connectors and skips MST encoders. The EDID path uses raw EDID access and reports checksum of the last extension block. Hardcoded custom and HBR2 compliance patterns are compatibility workarounds.

## Test signals
CTS equipment should observe ACK/NAK in `DP_TEST_RESPONSE`, correct checksum writes, requested link rate/lane count in subsequent modesets, correct color ramp/video bpc behavior, and expected PHY patterns. Kernel debug logs announce each request type and errors. Debugfs files expose active/type/data state for manual verification.
