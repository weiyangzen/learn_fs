# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_helper.h

Purpose: main DRM DisplayPort helper interface for link-status parsing, training delays, AUX/DPCD access, DSC/FEC/backlight/quirk logic, downstream introspection, LTTPR, CEC-over-AUX, PHY compliance, PCON, and bandwidth calculations.

Important APIs/types/functions: `struct drm_dp_vsc_sdp`, `struct drm_dp_as_sdp`, `struct drm_dp_aux_msg`, `struct drm_dp_aux_cec`, `struct drm_dp_aux`, `struct drm_dp_dpcd_ident`, `struct drm_dp_desc`, `enum drm_dp_quirk`, `struct drm_edp_backlight_info`, `struct drm_dp_phy_test_params`, DPCD read/write wrappers, AUX init/register/unregister, link helpers, DSC helpers, downstream helpers, LTTPR helpers, CRC, backlight, CEC hooks/stubs, PCON FRL/DSC helpers, and `drm_dp_vsc_sdp_pack`.

Control flow: drivers initialize `drm_dp_aux` with a hardware `transfer` callback, register I2C-over-AUX, read DPCD caps, train links, query downstream devices and quirks, configure DSC/FEC/PCON/backlight, and unregister during teardown. Inline data helpers convert short transfers to `-EPROTO` and fall back to byte reads for known buggy hubs.

State and persistence: `struct drm_dp_aux` stores DDC adapter, owning devices, CRTC, mutex, CRC work/count, CEC state, remote/powered/probe flags, and I2C NACK/defer counters. Sink DPCD state is external runtime hardware state.

Dependencies and integration points: delay, I2C, DRM connectors, DP constants, CEC, EDID, backlight, panels, seq_file/debug output, GPU DP drivers, eDP panels, MST, PCONs, HDCP/CEC, and compliance tooling.

Risks and test signals: transfer callback contract violations, powered-down endpoints, short-transfer bugs, stale DPCD, Kconfig stub assumptions, PCON misconfiguration, and backlight mode errors are risks. Test AUX NACK/defer/short paths, DPCD parsing, training, downstream adapters, LTTPR, CEC enabled/disabled, backlight, and PHY compliance patterns.
