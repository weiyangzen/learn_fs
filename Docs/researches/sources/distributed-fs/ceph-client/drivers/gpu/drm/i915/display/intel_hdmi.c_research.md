# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdmi.c

## Purpose

`intel_hdmi.c` implements i915 HDMI connector support. It covers HDMI mode validation and atomic configuration, TMDS clock and bits-per-component selection, RGB/YCbCr output format decisions, SCDC scrambling, infoframe packing/programming across platform register generations, EDID/DDC/dual-mode adapter detection, connector registration, CEC notifier setup, HDMI DSC helper calculations, and the HDMI implementation of the HDCP shim used by `intel_hdcp.c`.

## Important APIs, Types, And Functions

Externally used functions include `intel_hdmi_init_connector()`, `intel_hdmi_compute_has_hdmi_sink()`, `intel_hdmi_compute_config()`, `intel_hdmi_encoder_shutdown()`, `intel_hdmi_handle_sink_scrambling()`, `intel_dp_dual_mode_set_tmds_output()`, `intel_infoframe_init()`, `intel_hdmi_infoframes_enabled()`, `intel_hdmi_infoframe_enable()`, `intel_hdmi_read_gcp_infoframe()`, `intel_hdmi_fastset_infoframes()`, `intel_read_infoframe()`, `hsw_write_infoframe()`, `hsw_read_infoframe()`, `intel_hdmi_limited_color_range()`, `intel_hdmi_bpc_possible()`, `intel_hdmi_tmds_clock()`, `intel_hdmi_dsc_get_bpp()`, `intel_hdmi_dsc_get_num_slices()`, `intel_hdmi_dsc_get_slice_height()`, and `intel_hdmi_is_frl()`.

Important internal groups include platform-specific DIP/infoframe functions for G4X, IBX, CPT, VLV/CHV, HSW+ DDI, and LSPCON; HDMI HDCP DDC helpers; mode validation helpers for TMDS limits and color depth; connector funcs/helper funcs; and platform-specific DDC pin mapping.

## Control Flow

Connector setup runs through `intel_hdmi_init_connector()`. It validates port/lane suitability, selects a DDC pin from VBT or platform defaults, initializes the DRM connector with DDC, attaches helper funcs and HDMI properties, attaches the encoder, initializes HDCP when the port supports it, and registers a CEC notifier. `intel_infoframe_init()` separately installs the correct infoframe function pointers on the digital port based on platform generation and LSPCON presence.

Detection uses `intel_hdmi_detect()`: it checks display access, obtains GMBUS power, optionally checks digital port connection on newer platforms, clears old EDID/dual-mode state, reads EDID over DDC with a bit-banging fallback, updates connector display info, detects DP dual-mode adapters, updates CEC physical address, and returns connected only for digital EDID. Forced detection refreshes EDID only when the connector is already connected.

Atomic mode setup enters `intel_hdmi_compute_config()`. The function rejects dblescan and disallowed interlace, sets default RGB output, determines HDMI sink/infoframe/audio state, computes pipe bpp, chooses output format and TMDS clock while first respecting downstream limits and then allowing forced out-of-spec user modes at 8 bpc, handles YCbCr 4:2:0 pfit, computes limited RGB range, aspect ratio, lane count, HDMI 2.0 scrambling/high TMDS ratio, VRR, GCP, AVI, SPD, vendor, and HDR DRM infoframes.

Infoframe programming is split by hardware generation. The common pack path inserts the hardware-specific DIP data hole, then calls the selected `write_infoframe` callback. Set functions assert the HDMI port/transcoder is disabled, clear enable bits, program GCP where available, and write enabled infoframes. `intel_hdmi_fastset_infoframes()` updates HDR DRM infoframes during fastset without full mode programming.

HDCP-over-HDMI is exposed through `intel_hdmi_hdcp_shim`. HDCP 1.4 callbacks read and write DDC registers at `DRM_HDCP_DDC_*`, output Aksv through GMBUS, toggle DDI HDCP signalling, and check Ri matches. HDCP 2.2 callbacks use HDMI message offsets, poll RxStatus for message size/ready state with per-message timeouts, read/write HDCP 2.2 messages, detect reauth/topology-change status, and query sink version capability.

## State And Persistence Behavior

Persistent connector state includes `intel_hdmi->attached_connector`, DP dual-mode adapter type and max TMDS clock, CEC notifier pointer, connector EDID (`detect_edid`), display info, and connector properties. Atomic configuration state is stored in `intel_crtc_state`: `has_hdmi_sink`, `has_infoframe`, `has_audio`, `sink_format`, `output_format`, `port_clock`, `pipe_bpp`, `limited_color_range`, `hdmi_scrambling`, `hdmi_high_tmds_clock_ratio`, and packed infoframe payloads. HDCP state is owned by the generic HDCP core, while this file supplies transport operations through DDC and DDI signalling.

No file-backed persistence exists. Hardware state persists in DIP registers, SCDC sink registers, DDI signalling bits, and connected sink state until changed or reset. EDID and dual-mode data are refreshed on detection and cleared before new reads.

## Dependencies And Integration Points

The file depends on DRM HDMI, EDID, SCDC, HDCP, atomic, CEC, and probe helpers; i915 display register access; DDI, GMBUS, audio, VRR, pfit, LSPCON, panel, PHY, DPLL, and BIOS/VBT helpers. It integrates with the generic HDCP core through `intel_hdcp_init()` and the HDMI shim, with atomic modeset through connector helper funcs and encoder compute hooks, with userspace through connector properties, with sink devices through DDC/SCDC, and with CEC through notifier registration.

## Risks And Edge Cases

Risk is spread across platform differences. Infoframe register layouts differ substantially by generation; writing while ports are enabled or failing to clear enable bits can produce bad packets. TMDS and bpc selection must respect source, sink, dual-mode adapter, VBT, and PLL holes; mistakes reject valid modes or allow unstable modes. YCbCr 4:2:0 fallback and limited RGB range must avoid contradictory color state. SCDC scrambling must be programmed before enabling HDMI 2.0 links or sinks can time out.

HDCP DDC operations are sensitive to I2C errors, sink timing, message size validation, and Kaby Lake signalling workaround timing. Detection relies on EDID being digital and can fall back to bit-banged GMBUS. DDC pin selection must avoid duplicate pin ownership. DSC helper math must obey HDMI 2.1 slice width, throughput, and chunk byte limits.

## Test Signals

Useful signals include mode validation across HDMI 1.4/2.0 limits, RGB and YCbCr 4:2:0 modes, 8/10/12 bpc selection, SCDC scrambling at high TMDS rates, HDR metadata fastset updates, infoframe readback on each platform path, EDID read fallback, DP dual-mode adapter detection and max clock handling, CEC notifier address updates, HDCP 1.4 and 2.2 authentication over HDMI, Kaby Lake HDCP signalling workaround coverage, DDC pin conflict logging, and HDMI DSC slice/bpp helper unit coverage.
