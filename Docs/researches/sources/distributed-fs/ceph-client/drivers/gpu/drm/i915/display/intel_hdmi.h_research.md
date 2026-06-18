# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdmi.h

## Purpose

`intel_hdmi.h` declares the display-local HDMI API used by encoder setup, atomic modeset, infoframe handling, scrambling control, DSC calculations, and connector initialization. It keeps the large HDMI implementation private to `intel_hdmi.c` while exposing the operations needed by the rest of i915 display code.

## Important APIs, Types, And Functions

The header forward declares HDMI, DRM, and Intel display types, then declares connector and compute functions (`intel_hdmi_init_connector()`, `intel_hdmi_compute_has_hdmi_sink()`, `intel_hdmi_compute_config()`), lifecycle and sink programming functions (`intel_hdmi_encoder_shutdown()`, `intel_hdmi_handle_sink_scrambling()`, `intel_dp_dual_mode_set_tmds_output()`), infoframe operations (`intel_infoframe_init()`, `intel_hdmi_infoframes_enabled()`, `intel_hdmi_infoframe_enable()`, `intel_hdmi_read_gcp_infoframe()`, `intel_hdmi_fastset_infoframes()`, `intel_read_infoframe()`, `hsw_write_infoframe()`, `hsw_read_infoframe()`), color/clock helpers (`intel_hdmi_limited_color_range()`, `intel_hdmi_bpc_possible()`, `intel_hdmi_tmds_clock()`), DSC helpers, and `intel_hdmi_is_frl()`.

## Control Flow

Other display code calls `intel_hdmi_init_connector()` during digital port setup, `intel_infoframe_init()` to install platform callbacks, `intel_hdmi_compute_has_hdmi_sink()` and `intel_hdmi_compute_config()` during atomic state construction, infoframe functions during enable/fastset/readout, scrambling control before HDMI 2.0 port enable, and DSC helpers when configuring PCON/HDMI DSC paths.

## State And Persistence Behavior

The header stores no state. Its functions read and mutate `struct intel_hdmi`, `struct intel_digital_port`, `struct intel_connector`, and `struct intel_crtc_state` fields in the implementation. Callers are responsible for using the APIs in the proper modeset phase, especially for infoframe programming and SCDC scrambling.

## Dependencies And Integration Points

This header is included by DDI, encoder, connector, and readout code that needs HDMI-specific behavior. It bridges DRM connector state, Intel CRTC state, HDMI infoframe structs, output format enums, and the digital port object.

## Risks And Edge Cases

Header risk is API drift: signature changes affect multiple modeset paths. Misusing the APIs outside their intended enable/disable/readout phase can lead to stale infoframes, bad scrambling state, or inconsistent CRTC state. The direct exposure of HSW read/write infoframe helpers means non-HDMI paths that share DIP registers must preserve expected buffer layout.

## Test Signals

Build coverage, successful HDMI connector bring-up, valid atomic HDMI modes, correct infoframe programming/readback, SCDC scrambling toggles, and DSC helper results all validate this header contract.
