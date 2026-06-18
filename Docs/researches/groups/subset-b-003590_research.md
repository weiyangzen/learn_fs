# subset-b-003590 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp.h

## Purpose

`intel_dp.h` is the public interface for the i915 DisplayPort/eDP policy layer implemented primarily by `intel_dp.c`. It exposes connector lifecycle hooks, mode compute and validation helpers, link bandwidth/rate helpers, DSC/FEC helpers, sink power/control functions, SDP infoframe helpers, MST suspend/resume entry points, and small inline utilities used by adjacent i915 display modules.

The header is intentionally forward-declaration heavy. It avoids pulling large DRM/i915 structure definitions into every user, while still letting other display modules call into DP-specific functionality.

## Important APIs, Types, And Functions

The only type defined in the header is `struct link_config_limits`. It carries the candidate bounds used by DP mode computation:

- `min_rate` / `max_rate`: allowed link-rate range.
- `min_lane_count` / `max_lane_count`: allowed lane-count range.
- `pipe.min_bpp` / `pipe.max_bpp`: uncompressed DSC input or link output bpp in integer bpp units.
- `link.min_bpp_x16` / `link.max_bpp_x16`: compressed or uncompressed link bpp in 1/16 bpp fixed-point units.

Major function groups declared here:

- Connector and encoder lifecycle: `intel_dp_init_connector()`, `intel_dp_connector_sync_state()`, `intel_dp_encoder_flush_work()`, `intel_dp_encoder_suspend()`, `intel_dp_encoder_shutdown()`, `intel_dp_sync_state()`, and `intel_dp_initial_fastset_check()`.
- HPD/link state: `intel_dp_hpd_pulse()`, `intel_dp_link_check()`, `intel_dp_check_link_state()`, `intel_dp_get_active_pipes()`, `intel_dp_flush_connector_commits()`, `intel_digital_port_lock()`, `intel_digital_port_unlock()`, `intel_digital_port_connected()`, and `intel_digital_port_connected_locked()`.
- Mode compute: `intel_dp_compute_config()`, `intel_dp_compute_config_late()`, `intel_dp_audio_compute_config()`, `intel_dp_compute_config_limits()`, `intel_dp_compute_min_hblank()`, `intel_dp_sdp_min_guardband()`, and `intel_dp_limited_color_range()`.
- Link math and capabilities: `intel_dp_min_bpp()`, `intel_dp_output_format_link_bpp_x16()`, `intel_dp_link_bw_overhead()`, `intel_dp_link_required()`, `intel_dp_effective_data_rate()`, `intel_dp_max_link_data_rate()`, `intel_dp_config_required_rate()`, `intel_dp_link_symbol_size()`, `intel_dp_link_symbol_clock()`, `intel_dp_max_source_lane_count()`, `intel_dp_max_link_rate()`, `intel_dp_max_lane_count()`, `intel_dp_max_common_rate()`, `intel_dp_max_common_lane_count()`, `intel_dp_common_rate()`, `intel_dp_rate_index()`, `intel_dp_rate_select()`, `intel_dp_compute_rate()`, `intel_dp_link_config_index()`, `intel_dp_link_config_get()`, `intel_dp_link_params_valid()`, `intel_dp_set_link_params()`, and `intel_dp_reset_link_params()`.
- DSC/FEC and joiners: `intel_dp_has_dsc()`, `intel_dp_supports_fec()`, `intel_dp_supports_dsc()`, `intel_dp_mode_to_fec_clock()`, `intel_dp_bw_fec_overhead()`, `intel_dp_dsc_reset_config()`, `intel_dp_dsc_compute_config()`, `intel_dp_needs_8b10b_fec()`, `intel_dp_dsc_compute_max_bpp()`, `intel_dp_compute_min_compressed_bpp_x16()`, `intel_dp_mode_valid_with_dsc()`, `intel_dp_dsc_valid_compressed_bpp()`, `intel_dp_dsc_get_slice_count()`, `intel_dp_dsc_max_src_input_bpc()`, `intel_dp_dsc_min_src_input_bpc()`, `intel_dp_dsc_min_src_compressed_bpp()`, `intel_dp_dsc_bpp_step_x16()`, `intel_dp_has_joiner()`, `intel_dp_joiner_needs_dsc()`, `intel_dp_max_hdisplay_per_pipe()`, `intel_dp_dotclk_valid()`, `intel_dp_joiner_candidate_valid()`, and `for_each_joiner_candidate`.
- Sink controls: `intel_dp_set_power()`, `intel_dp_configure_protocol_converter()`, `intel_dp_sink_enable_decompression()`, `intel_dp_sink_disable_decompression()`, `intel_dp_get_dsc_sink_cap()`, `intel_dp_check_frl_training()`, `intel_dp_pcon_dsc_configure()`, `intel_dp_update_sink_caps()`, `intel_dp_dpcd_set_probe()`, `intel_dp_invalidate_source_oui()`, and `intel_dp_wait_source_oui()`.
- SDP/infoframes and display metadata: `intel_dp_needs_vsc_sdp()`, `intel_dp_set_infoframes()`, `intel_read_dp_sdp()`, `intel_dp_in_hdr_mode()`, `intel_dp_has_gamut_metadata_dip()`, and eDP backlight helpers.

`intel_dp_unused_lane_mask()` is the only inline helper. It returns a four-lane mask with active lanes cleared, useful when programming unused lane bits.

## Control Flow And Integration

The header defines the boundary other modules use to call DP functionality without needing the whole implementation. `intel_ddi`, encoder setup, MST, link training, PSR, HDCP, audio, VDSC, panel/backlight, and hotplug code all rely on these declarations.

The mode-set path typically flows from connector atomic checks into `intel_dp_compute_config()`, with other display modules then using computed CRTC state to program DDI, transcoders, audio, DSC PPS, and infoframes. HPD flows enter through `intel_dp_hpd_pulse()` and may call link retraining, MST handlers, or full detection. Sink power and decompression APIs are called from enable/disable sequences around modeset commits.

The `for_each_joiner_candidate` macro is a notable control helper: it iterates candidate joined-pipe counts from one through `I915_MAX_PIPES` and filters through `intel_dp_joiner_candidate_valid()`. Callers use it to evaluate normal, bigjoiner, and ultrajoiner modes without duplicating platform checks.

## State And Persistence Behavior

The header does not store state itself. Its API contracts mutate state owned by `struct intel_dp`, `struct intel_connector`, and `struct intel_crtc_state`. The comments in `struct link_config_limits` are important because they encode the units expected by compute helpers. Confusing integer bpp with Q4 fixed-point bpp would directly corrupt mode bandwidth decisions.

Duplicate declarations of `intel_edp_fixup_vbt_bpp()` and `intel_dp_supports_fec()` appear in the header. They are harmless for C compilation but are maintenance noise and can mislead readers scanning for API ownership.

## Dependencies

The header includes only `<linux/types.h>` and forward declares all DRM/i915 types it references. It uses `enum irqreturn` in a prototype without including the defining interrupt header in this file, relying on transitive includes from users or build context. The function signatures depend on DRM connector/encoder state, i915 atomic/CRTC/connector/encoder types, DP descriptor types, and i915 output-format/port/pipe enums.

## Risks And Test Signals

Risks are mostly API contract risks:

- Unit mismatches in `link_config_limits` can cause incorrect link validation or DSC bpp decisions.
- Callers must pass states that already have relevant connector/CRTC ownership and modeset locks where required by implementation.
- The broad header surface means changes in `intel_dp.c` prototypes can ripple through many i915 display modules.
- Duplicate prototypes should be cleaned carefully only if no generated/header-order dependencies exist.

Test signals include a full i915 build, allmodconfig-style include hygiene, compiler warnings for duplicate or missing declarations, and targeted rebuilds of users including DP, DDI, MST, PSR, HDCP, audio, and VDSC modules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux.c

## Purpose

`intel_dp_aux.c` implements the i915 hardware-backed DisplayPort AUX channel transport. It provides byte packing/unpacking, AUX register selection for multiple platform generations, AUX clock-divider and send-control programming, the DRM `drm_dp_aux.transfer` callback, AUX power/locking/VDD integration, AUX channel selection, init/fini, and the IRQ wakeup handler. Higher-level DP code uses this file indirectly through `intel_dp->aux` for DPCD, EDID-over-I2C, CEC, HDCP, MST, PCON, PSR, ALPM, and other AUX transactions.

## Important APIs, Types, And Functions

Public functions:

- `intel_dp_aux_pack()`: packs up to four bytes into the big-endian register format expected by DP AUX data registers.
- `intel_dp_aux_fw_sync_len()`: returns the fast-wake sync pulse length, including a DPCD quirk adjustment for a known panel/laptop combination.
- `intel_dp_aux_init()`: selects platform register accessors and timing callbacks, initializes `struct drm_dp_aux`, names it, installs the transfer callback, creates the CPU latency QoS request, and initializes DPCD probe policy.
- `intel_dp_aux_fini()`: removes the QoS request and frees the AUX name.
- `intel_dp_aux_ch()`: chooses and validates the AUX channel from VBT or platform defaults, preventing duplicate use by another digital encoder.
- `intel_dp_aux_irq_handler()`: wakes the shared GMBUS/AUX wait queue when hardware signals AUX completion.

Internal helpers:

- `intel_dp_aux_unpack()` mirrors `intel_dp_aux_pack()` for receive data.
- `intel_dp_aux_wait_done()` waits up to 10 ms for `DP_AUX_CH_CTL_SEND_BUSY` to clear and returns the final status register.
- `g4x_get_aux_clock_divider()`, `ilk_get_aux_clock_divider()`, `hsw_get_aux_clock_divider()`, and `skl_get_aux_clock_divider()` calculate platform-specific AUX clock divisors.
- `g4x_get_aux_send_ctl()` and `skl_get_aux_send_ctl()` build hardware send-control words, including message size, timeout, error bits, precharge/sync pulse lengths, Thunderbolt I/O bit, and XeLPDP power-request preservation.
- `intel_dp_aux_xfer()` performs the low-level hardware transaction.
- `intel_dp_aux_transfer()` adapts DRM AUX messages into i915 hardware transactions and decodes replies.
- Register selector families `vlv_*`, `g4x_*`, `ilk_*`, `skl_*`, `tgl_*`, and `xelpdp_*` map `enum aux_ch` and data index to the correct i915 register.

## Control Flow

Initialization starts with `intel_dp_aux_ch()` during encoder setup to choose `dig_port->aux_ch`. `intel_dp_aux_init()` then installs register-selector callbacks based on display generation and platform: XeLPDP-style for display version 14+, TGL-style for 12+, SKL-style for 9+, ILK/PCH split, VLV/CHV, or G4x. It similarly chooses the clock-divider and send-control callbacks, initializes the DRM AUX object, assigns the human-readable AUX name, sets `aux.transfer = intel_dp_aux_transfer`, adds a QoS latency request, and configures DPCD probe behavior.

A DRM AUX request enters `intel_dp_aux_transfer()`. The function builds the AUX native/I2C header, decides transmit and receive sizes from request type, copies write payloads, applies the HDCP Aksv hardware flag when needed, calls `intel_dp_aux_xfer()`, then fills `msg->reply` and returns either payload bytes transferred or an errno. Native/I2C reads expect one reply byte plus payload; writes expect one or two reply bytes and support short-write byte counts.

`intel_dp_aux_xfer()` is the critical transaction path. It locks the digital port, rejects external AUX transfers if the port is disconnected, gets the AUX power domain, optionally locks PPS for eDP or VLV/CHV, records whether VDD was already on, requests low CPU wake latency, checks panel power, waits for any previous SEND_BUSY to clear, validates the 20-byte hardware FIFO limit, then tries each clock divider and up to five transmit attempts per divider. Each attempt writes up to five data registers, starts the send, waits for completion via `intel_dp_aux_wait_done()`, clears DONE/error bits, retries on timeout or receive error with required delay, and finally reads response bytes from data registers.

Cleanup in `intel_dp_aux_xfer()` restores CPU latency QoS, turns off VDD only if this function turned it on, unlocks PPS, drops the display power reference asynchronously, and unlocks the digital port. This cleanup path is shared for normal completion and errors.

IRQ completion is minimal: `intel_dp_aux_irq_handler()` wakes the wait queue used by `intel_dp_aux_wait_done()`. The wait condition still polls the hardware register, so a missed IRQ can be covered by timeout, while an IRQ reduces latency.

## State And Persistence Behavior

The file mutates several persistent fields in `struct intel_dp`:

- Function pointers: `aux_ch_ctl_reg`, `aux_ch_data_reg`, `get_aux_clock_divider`, and `get_aux_send_ctl`.
- `intel_dp->aux`: DRM AUX device fields, transfer callback, name, DRM device, Linux device after connector registration, and I2C retry counters maintained by DRM helpers.
- `intel_dp->pm_qos`: CPU latency QoS request active for the AUX object lifetime and set to zero only during a transaction.
- `intel_dp->aux_busy_last_status`: suppresses repeated busy warnings with identical status.

It also consumes `dig_port->aux_ch`, `dig_port->base.connected`, Type-C/TBT alt-mode state, PPS/VDD state, platform generation data, and display power domains. Hardware state persists in AUX control/data registers, which are written for every transaction and cleared for DONE/error bits after each send.

## Dependencies And Integration Points

This file integrates with:

- DRM DP AUX core through `drm_dp_aux_init()` and `struct drm_dp_aux.transfer`.
- i915 register access through `intel_de_read/write`, no-trace reads, register macros from `intel_dp_aux_regs.h`, and trace helpers.
- i915 digital-port locking via `intel_digital_port_lock()` / `intel_digital_port_unlock()` implemented in `intel_dp.c`.
- Display power domains and runtime PM through `intel_display_power_get()` and `intel_display_power_put_async()`.
- eDP PPS/VDD through `intel_pps_lock()`, `intel_pps_vdd_on_unlocked()`, `intel_pps_vdd_off_unlocked()`, and `intel_pps_check_power_unlocked()`.
- Type-C/TBT state through `intel_tc_port_in_tbt_alt_mode()` and live connection callbacks.
- DPCD quirks through `intel_has_dpcd_quirk()`.

## Risks And Edge Cases

The highest-risk behavior is in transaction ordering and cleanup:

- AUX has a strict 20-byte hardware limit; callers must go through DRM helpers that segment larger transfers.
- External disconnected ports return `-ENXIO` before power setup to avoid long timeouts and satisfy DP CTS behavior.
- eDP transfers need PPS/VDD coordination. Incorrect VDD ownership handling could power off a panel-needed AUX rail or leak VDD.
- The code requests zero CPU latency during transactions because AUX is sensitive to IRQ latency; forgetting to restore QoS would affect system power.
- Some platforms require multiple clock dividers or workarounds, such as HSW non-ULT AUX divider values and XeLPDP power-request preservation.
- Timeout and receive-error retry timing is spec-sensitive. Changing retry counts or delays can break marginal sinks or compliance tests.
- `intel_dp_aux_wait_done()` uses a shared display GMBUS wait queue; wakeups are broad, so the condition must always re-read the target AUX control register.

## Test Signals

Test signals include:

- DPCD read/write success during connector detection, eDP init, MST topology probing, DSC/PSR/ALPM capability reads, and PCON controls.
- EDID-over-AUX I2C behavior, including expected NACK/defer counters for DP compliance tests.
- `kms_dp_aux_dev` and raw AUX userspace access through `/dev/drm_dp_aux*`.
- Hotplug and disconnect tests verifying `-ENXIO` avoids long AUX hangs on unplugged external ports.
- Suspend/resume and runtime PM tests verifying power domains, PPS locks, and VDD are balanced.
- Platform matrix coverage for G4x, ILK/PCH split, VLV/CHV, SKL+, TGL USB-C AUX names/registers, XeLPDP registers, and Thunderbolt alt-mode transactions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux.h

## Purpose

`intel_dp_aux.h` declares the small public interface for the i915 DP AUX transport implemented by `intel_dp_aux.c`. It is used by DP connector setup, register/power code, IRQ code, and higher-level DP logic that needs AUX initialization, cleanup, channel selection, packing helpers, or fast-wake sync timing.

## Important APIs

The header declares:

- `intel_dp_aux_init(struct intel_dp *intel_dp)`: initialize the DRM AUX object and platform-specific hardware callbacks.
- `intel_dp_aux_fini(struct intel_dp *intel_dp)`: release AUX lifetime resources.
- `intel_dp_aux_ch(struct intel_encoder *encoder)`: choose an AUX channel from VBT or platform defaults and reject duplicate claims.
- `intel_dp_aux_irq_handler(struct intel_display *display)`: wake AUX waiters from the display IRQ path.
- `intel_dp_aux_pack(const u8 *src, int src_bytes)`: pack up to four AUX payload bytes into a 32-bit register word.
- `intel_dp_aux_fw_sync_len(struct intel_dp *intel_dp)`: compute fast-wake AUX sync length, including quirk handling.

It forward declares `enum aux_ch`, `struct intel_display`, `struct intel_dp`, and `struct intel_encoder`, and includes `<linux/types.h>` for `u32` and fixed-width integer types.

## Control Flow And Integration

Typical setup flow is: encoder setup calls `intel_dp_aux_ch()` to choose `dig_port->aux_ch`; `intel_dp_init_connector()` calls `intel_dp_aux_init()` after default DP sink state is initialized; connector registration later registers the already initialized `drm_dp_aux`; IRQ setup calls `intel_dp_aux_irq_handler()` on AUX completion interrupts; encoder cleanup calls `intel_dp_aux_fini()`.

`intel_dp_aux_pack()` is exported because some DP paths or tests may need the same register packing format as the transfer implementation. `intel_dp_aux_fw_sync_len()` is exposed so other platform code can use the same fast-wake timing policy as AUX send-control programming.

## State And Persistence Behavior

The header has no state of its own. Its functions mutate `struct intel_dp` lifetime fields such as the DRM AUX object, AUX register callbacks, QoS request, and name allocation. Callers are expected to pair init/fini and ensure IRQ handler calls only target initialized display state.

## Dependencies And Risks

The API is tightly coupled to `struct intel_dp` and `struct intel_encoder` internals even though those structures are forward declared. Risks include init/fini imbalance, calling channel selection before encoder VBT/devdata is available, and using the pack helper with more than four bytes while assuming all bytes are included. The implementation clamps packing to four bytes, matching AUX data register width.

## Test Signals

Build coverage should catch missing type includes or signature drift. Runtime validation should show AUX devices registering/unregistering correctly, AUX IRQs waking transactions, DPCD/EDID reads succeeding after `intel_dp_aux_init()`, and no leaks or stale callbacks after `intel_dp_aux_fini()`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux.h -->
