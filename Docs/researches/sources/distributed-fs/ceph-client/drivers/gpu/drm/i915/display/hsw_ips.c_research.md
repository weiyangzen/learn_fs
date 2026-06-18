# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/hsw_ips.c

## Purpose
`hsw_ips.c` manages Intermediate Pixel Storage (IPS) power-saving behavior on Haswell/Broadwell ULT systems, where IPS is tied to pipe A. It decides when IPS can be enabled, handles atomic pre/post update transitions, applies Haswell versus Broadwell programming paths, exposes debugfs controls, and contributes minimum CDCLK requirements.

## Important APIs, Types, and Functions
`hsw_ips_enable()` programs `IPS_CTL` or the Broadwell PCODE mailbox (`DISPLAY_IPS_CONTROL`) if `crtc_state->ips_enabled` is true, optionally adding `IPS_FALSE_COLOR`. `hsw_ips_disable()` clears IPS and returns whether callers must wait for vblank before disabling a plane. `hsw_ips_need_disable()` and `hsw_ips_need_enable()` compare old/new atomic CRTC state to handle modesets, IPS flag changes, inherited Broadwell state, and the Haswell split-gamma palette workaround. `hsw_ips_pre_update()` and `hsw_ips_post_update()` are the public atomic sequencing hooks.

Capability and config functions include `hsw_crtc_supports_ips()` for pipe/platform filtering, `hsw_crtc_state_ips_capable()` for pipe BPP restrictions, `_hsw_ips_min_cdclk()` and `hsw_ips_min_cdclk()` for Broadwell CDCLK constraints, `hsw_ips_compute_config()` for enabling IPS only when policy, CRC, active planes, and CDCLK allow it, and `hsw_ips_get_config()` for hardware readout. Debugfs helpers expose `i915_ips_false_color` and `i915_ips_status`.

## Control Flow and State
Atomic check first clears and conditionally sets `crtc_state->ips_enabled`. During commits, pre-update may disable IPS before modesets, color LUT updates, or transitions away from IPS; post-update may re-enable it after plane updates and a vblank wait. Persistent software state is in `display->ips.false_color`, module/display params (`enable_ips`), and atomic CRTC state. Hardware state is in `IPS_CTL` on Haswell and mediated through PCODE on Broadwell, where readout is not reliable and inherited state is handled conservatively.

## Dependencies and Integration Points
The file depends on debugfs, DRM logging, PCODE registers, color registers, display RPM, parent PCODE access, and core display atomic state. `intel_display.c` calls IPS disable/pre/post/get/compute hooks during modeset and update flows. `intel_cdclk.c` incorporates `hsw_ips_min_cdclk()`, and `intel_display_debugfs.c` registers the debugfs files.

## Risks and Test Signals
Risks include vblank ordering around plane enable/disable, Broadwell PCODE timeout behavior, unreliable Broadwell state readout, interaction with CRC capture, and Haswell split-gamma palette hazards. Test signals include atomic modesets with IPS enabled/disabled, color LUT updates in split gamma mode, CRC tests confirming IPS is disabled when CRC is active, Broadwell PCODE timeout logs, debugfs false-color behavior, and CDCLK selection when IPS would require more than the max clock.
