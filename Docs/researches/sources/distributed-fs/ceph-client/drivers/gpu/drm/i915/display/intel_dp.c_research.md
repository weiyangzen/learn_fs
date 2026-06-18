# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp.c

## Purpose

`intel_dp.c` is the main DisplayPort/eDP connector, mode validation, link configuration, capability discovery, hotplug, power, DSC/FEC, MST, PCON, SDP/infoframe, and connector lifecycle implementation for the i915 display driver. It sits above hardware-specific DDI/PPS/AUX helpers and below DRM connector/atomic/MST/DP helper APIs. The file owns the high-level policy for choosing DP link rates and lane counts, deciding whether DSC or pipe joiners are required, reading and caching DPCD/EDID-derived sink capability state, programming sink-side protocol converter and decompression controls over AUX, and deciding whether hotplug pulses can be handled as short service IRQs or require full reprobe.

The file handles both external DP and embedded DisplayPort. eDP paths are special because DPCD, EDID, PPS, panel fixed modes, backlight, PSR/ALPM/DRRS, MSO, and BIOS/VBT data are initialized and cached at connector registration time, while external DP repeats more of this work during detection.

## Important APIs, Types, And Functions

The public API implemented here is declared mostly in `intel_dp.h`. Important exported functions include:

- Link capability and helpers: `intel_dp_is_edp()`, `intel_dp_is_uhbr()`, `intel_dp_link_symbol_size()`, `intel_dp_link_symbol_clock()`, `intel_dp_max_source_lane_count()`, `intel_dp_max_common_rate()`, `intel_dp_max_common_lane_count()`, `intel_dp_max_link_rate()`, `intel_dp_max_lane_count()`, `intel_dp_link_bw_overhead()`, `intel_dp_link_required()`, `intel_dp_effective_data_rate()`, `intel_dp_max_link_data_rate()`, `intel_dp_rate_select()`, `intel_dp_compute_rate()`, `intel_dp_link_params_valid()`, `intel_dp_link_config_get()`, and `intel_dp_link_config_index()`.
- Mode/atomic configuration: `intel_dp_compute_config()`, `intel_dp_compute_config_late()`, `intel_dp_compute_config_limits()`, `intel_dp_audio_compute_config()`, `intel_dp_compute_min_hblank()`, `intel_dp_limited_color_range()`, `intel_dp_config_required_rate()`, `intel_dp_dotclk_valid()`, `intel_dp_joiner_candidate_valid()`, and `intel_dp_max_hdisplay_per_pipe()`.
- DSC/FEC support: `intel_dp_has_dsc()`, `intel_dp_supports_fec()`, `intel_dp_supports_dsc()`, `intel_dp_dsc_reset_config()`, `intel_dp_dsc_compute_config()`, `intel_dp_dsc_compute_max_bpp()`, `intel_dp_dsc_get_slice_count()`, `intel_dp_mode_valid_with_dsc()`, `intel_dp_dsc_valid_compressed_bpp()`, `intel_dp_dsc_bpp_step_x16()`, `intel_dp_needs_8b10b_fec()`, `intel_dp_get_dsc_sink_cap()`, `intel_dp_sink_enable_decompression()`, and `intel_dp_sink_disable_decompression()`.
- Connector, HPD, and lifecycle: `intel_dp_init_connector()`, `intel_dp_connector_sync_state()`, `intel_dp_encoder_flush_work()`, `intel_dp_encoder_suspend()`, `intel_dp_encoder_shutdown()`, `intel_dp_hpd_pulse()`, `intel_dp_link_check()`, `intel_dp_check_link_state()`, `intel_dp_get_active_pipes()`, `intel_dp_flush_connector_commits()`, and `intel_dp_has_connector()`.
- Sink power and protocol converter: `intel_dp_set_power()`, `intel_dp_configure_protocol_converter()`, `intel_dp_check_frl_training()`, `intel_dp_pcon_dsc_configure()`, `intel_dp_invalidate_source_oui()`, and `intel_dp_wait_source_oui()`.
- Secondary data packet handling: `intel_dp_needs_vsc_sdp()`, `intel_dp_set_infoframes()`, `intel_read_dp_sdp()`, `intel_dp_sdp_min_guardband()`, and internal pack/unpack helpers for VSC, Adaptive Sync, and HDR metadata SDPs.
- MST support glue: `intel_dp_mst_suspend()` and `intel_dp_mst_resume()`, plus internal detect/configure/disconnect/status paths.

Key in-file state carriers are `struct intel_dp`, `struct intel_connector`, `struct intel_crtc_state`, `struct drm_connector_state`, `struct link_config_limits`, and several sub-structures embedded in `intel_dp` or `connector->dp`: `link`, `dfp`, `frl`, `mst`, `tunnel`, `psr`, `alpm`, DSC DPCD caches, panel replay caps, and DFP downstream capability caches.

## Control Flow

Connector setup starts in `intel_dp_init_connector()`. It validates lane availability, preserves the current output register, chooses DP vs eDP type using VBT/platform data, initializes default sink rates and max lane count, initializes AUX, registers the DRM connector/helper callbacks, attaches encoder state, and then runs eDP-only initialization via `intel_edp_init_connector()` if needed. After that it builds source rates, common rates, sorted link configurations, reset link parameters, MST encoders, connector properties, optional HDCP, FRL defaults, and PSR.

eDP initialization is front-loaded. `intel_edp_init_connector()` initializes VBT panel data, PPS, HPD detection, ALPM, DPCD, source OUI, ALPM/PSR DPCD, sink rates, sink lane count, DSC caps, EDID/fixed modes, MSO mode fixups, panel/backlight state, panel properties, and late PPS state. Failure paths turn off VDD and clean panel state, because eDP AUX transactions depend on panel power sequencing.

External DP detection flows through `intel_dp_detect()`. It checks display access, flushes pending connector commits, powers VDD, reads live port status, calls `intel_dp_detect_dpcd()` for external connectors, verifies MST DPCD state, resets cached DSC/panel replay state on disconnect, detects tunnels, initializes source OUI, initializes PSR DPCD for non-eDP, reads DSC and SDP caps, resets link params if requested, configures MST, and either enters MST mode with the root connector disconnected or reads EDID and marks the connector connected. The function always restores the DPCD-probe policy and turns VDD off before returning.

Link capability setup combines platform/source tables, VBT limits, sink DPCD, LTTPR caps, DP tunnel bandwidth allocation, Type-C lane limits, and forced debug settings. `intel_dp_set_source_rates()` selects platform-specific source rates and caps them by VBT/platform maximums. `intel_dp_set_dpcd_sink_rates()` and eDP-specific `intel_edp_set_sink_rates()` populate sink rates, including UHBR support from `DP_128B132B_SUPPORTED_LINK_RATES` and eDP supported-link-rate tables. `intel_dp_set_common_rates()` intersects source and sink rates and initializes sorted lane/rate configurations by bandwidth.

Mode validation and compute share the same broad decision tree. `intel_dp_mode_valid()` rejects impossible timings, applies fixed-panel clock for eDP, chooses sink/output formats, checks link bandwidth without DSC, then iterates joiner candidates and tries DSC where needed. `intel_dp_compute_config()` computes the actual CRTC state: fixed panel config, output format, link config with or without downstream TMDS/FRL limits, panel fitter, limited RGB range, enhanced framing or UHBR MST master transcoder, MSO splitter timing transformation, audio, M/N values for 8b/10b, minimum hblank for newer display versions, VRR, Adaptive Sync SDP, PSR, ALPM LOBF, DRRS, VSC SDP, HDR metadata SDP, and DP tunnel stream bandwidth.

The link-configuration core is `intel_dp_compute_link_config()`, which iterates valid joiner counts using `for_each_joiner_candidate`. Each candidate calls `intel_dp_compute_link_for_joined_pipes()`. That function first tries an uncompressed configuration using `intel_dp_compute_config_limits()` and `intel_dp_compute_link_config_wide()`, preferring maximum bpp, then lower clock, then wider lane count. If joiners require DSC, DSC is forced, uncompressed link config fails, dotclock is invalid, or user debug forces DSC, it verifies DSC support and calls `intel_dp_dsc_compute_config()`.

DSC computation derives source/sink input BPC limits, compressed bpp minimum and maximum, sink bpp increments, joiner RAM and bandwidth limits, branch throughput quirks, slice count, slice height, DSC version, line buffer depth, block prediction, and RC parameters. SST chooses link rate/lane count by testing compressed bpp from high to low. eDP uses maximum link params and maximum compressed bpp. MST has already selected its link allocation elsewhere and only fills DSC params.

Hotplug handling starts at `intel_dp_hpd_pulse()`. eDP HPD pulses are ignored in cases that would create VDD-on/VDD-off loops. Long HPD pulses set DPCD probing, do a dummy DPRX caps read for DP tunnel coordination, request link parameter reset, invalidate source OUI, and return `IRQ_NONE` to schedule full detection. Short pulses either service MST status through `intel_dp_check_mst_status()` or SST status through `intel_dp_short_pulse()`. Short-pulse handling reads and ACKs ESI vectors, handles automated test/HDCP/sink IRQs, checks sink count changes, forces link-status checks, handles CEC, downstream-port changes, PSR short pulses, ALPM errors, and DP compliance test state. Link retraining is queued via `intel_dp_check_link_state()` and executed under modeset locks by `intel_dp_link_check()` / `intel_dp_retrain_link()`.

PCON and downstream converter flow is split between capability discovery and modeset programming. `intel_dp_update_dfp()` caches downstream max BPC, dotclock, TMDS clock limits, PCON FRL bandwidth, and PCON DSC caps. `intel_dp_check_frl_training()` tries HDMI 2.1 FRL training when source-control PCON and HDMI 2.1 sink conditions hold, falling back to TMDS mode. `intel_dp_configure_protocol_converter()` programs HDMI/DVI mode and RGB/YCbCr conversion DPCD controls based on the chosen sink and output formats. `intel_dp_pcon_dsc_configure()` computes and sends PCON DSC PPS override parameters for HDMI 2.1 DSC paths.

## State And Persistence Behavior

`struct intel_dp` caches long-lived per-port state: DPCD, eDP DPCD, DPRX descriptor and quirks, downstream port bytes, sink count, source/sink/common rates, sorted link configs, current link rate/lane count, link training state, forced/debug link settings, MST state, tunnel state, FRL training state, DSC PCON DPCD, DFP converter caps, OUI validity and last write time, colorimetry/AS-SDP support, MSO link count/overlap, reset-link flag, and flags used by PSR/ALPM/panel replay. This state is refreshed on detection, eDP init, HPD long pulses, resume sync, and disconnect paths. Disconnect clears sensitive cached caps such as DSC and panel replay and disconnects MST/tunnel state.

`struct intel_connector` carries EDID-derived `display_info`, fixed panel modes, VBT panel data, detected EDID pointer, DSC DPCD and branch caps, FEC capability, decompression AUX pointer, decompression enable ref state, panel replay caps, and connector properties. EDID state is explicitly replaced by `intel_dp_set_edid()` and cleared by `intel_dp_unset_edid()`.

`struct intel_crtc_state` is the per-atomic-commit output of compute paths. This file mutates link rate, lane count, pipe bpp, output/sink formats, DSC config, FEC enable, joiner pipes, splitter/MSO timing, limited color range, M/N values, min hblank, audio, SDP infoframes, PSR/ALPM/DRRS/VRR flags, and tunnel bandwidth.

Persistent hardware/sink side effects happen over AUX/DPCD and display registers: DP_SET_POWER, source OUI, DSC decompression/passthrough, PCON HDMI mode and conversion controls, FRL training, PCON DSC PPS override, CEC attach, and infoframe DIP register programming. These side effects are guarded by VDD/PPS/power-domain handling in lower-level helpers and by connector/modeset locks where needed.

## Dependencies And Integration Points

The file depends heavily on DRM DP helpers (`drm_dp_*`), DRM EDID/modeset/atomic helpers, DRM DSC helpers, HDMI helper code, and i915 display subsystems:

- AUX transactions are provided by `intel_dp_aux.c` through `intel_dp->aux`.
- DDI/encoder hardware setup is in `intel_ddi`, `g4x_dp`, `intel_encoder`, and per-platform register helpers.
- Link training and LTTPR handling come from `intel_dp_link_training.h` and related code.
- MST uses DRM MST topology manager plus i915 stream encoder setup in `intel_dp_mst`.
- DP tunneling integrates through `intel_dp_tunnel` and DRM DP tunnel helpers.
- PPS/backlight/panel power use `intel_pps`, `intel_backlight`, and `intel_panel`.
- PSR, Panel Replay, ALPM, DRRS, VRR, VDSC, audio, HDCP, LSPCON, Type-C, DPLL, PCH, FIFO underrun, and VBT helpers all feed either capability decisions or computed CRTC state.
- Connector callbacks are registered with DRM core via `drm_connector_init_with_ddc()` and helper funcs for detect/get_modes/mode_valid/atomic_check.

## Risks And Edge Cases

This file sits on many hardware and sink interoperability boundaries. High-risk areas are:

- Link bandwidth math for UHBR vs 8b/10b, FEC overhead, DP tunnel allocation, MST, DSC, and joiner combinations. A small mismatch can cause modes to validate but underrun or fail link training.
- DSC bpp and slice selection. The code contains several TODOs and quirk paths around branch throughput, bpp increments, joiner RAM, source/sink version selection, and MST tiled displays.
- eDP power sequencing. DPCD/EDID reads require VDD or panel power, and HPD pulses can create loops if handled while VDD is off.
- Cached DPCD/EDID/DFP state can become stale across disconnect, long HPD, MST mode changes, or tunnel events. The file explicitly clears some caches on disconnect, but comments note that moving resets may be needed to avoid compute failures after disconnect.
- MST short IRQ servicing must distinguish real service events from reprobe-triggering errors. Failure to ACK or process ESI correctly can lose MST sideband messages or link-status changes.
- Type-C and tunnel paths depend on live port ownership, glitch handling, and timely DPRX reads during long HPD.
- PCON FRL/DSC configuration is sink- and converter-dependent; failures fall back to TMDS where possible, but bad DFP caps can still constrain mode selection.
- Fastset/readout gaps remain for DSC; `intel_dp_initial_fastset_check()` forces full modeset when DSC is active because full DSC state comparison is not implemented.

## Test Signals

Useful validation signals include:

- Kernel build coverage for i915 display code and sparse/compiler warnings around duplicated declarations, enum cases, fixed-point bpp arithmetic, and register macros.
- DRM/i915 display selftests and IGT DP/eDP suites covering `kms_dp_aux_dev`, `kms_dp_dsc`, `kms_psr`, `kms_vrr`, `kms_hdr`, `kms_atomic`, `kms_flip`, `kms_pipe_crc_basic`, MST hotplug tests, HDCP tests, and DP compliance test hooks.
- Runtime logs under `drm.debug=0x1e` or KMS debug showing source/sink/common rates, link config decisions, DSC bpp/slice computation, DPCD/ESI reads, HPD pulse handling, link retrain attempts, FRL training, and PCON conversion state.
- Hardware matrix testing across eDP panels, fixed-mode panels, MSO panels, DP SST monitors, MST hubs, LTTPR links, Type-C/TBT docks, DP-to-HDMI PCONs, DSC monitors, HDR/VRR displays, and UHBR-capable sinks.
- Suspend/resume and module unload checks should verify MST manager suspend/resume, VDD off, AUX cleanup, PPS power-cycle waits, link parameter sync, and no use-after-free of connector EDID/AUX state.
