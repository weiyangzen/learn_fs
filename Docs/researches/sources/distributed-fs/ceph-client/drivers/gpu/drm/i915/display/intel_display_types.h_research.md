# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_types.h

## Purpose
This is the central display object and atomic-state type contract for i915/Xe display code. It extends DRM framebuffer, connector, encoder, CRTC, plane, DP, HDMI, panel, PSR, PPS, watermark, and atomic state objects with Intel-specific hardware state, cached capability data, function hooks, and typed conversion helpers.

## Important APIs, Types, and Functions
Core types include `intel_fb_view`, `intel_framebuffer`, `intel_encoder`, `intel_panel_bl_funcs`, `intel_pps_delays`, `intel_vbt_panel_data`, `intel_panel`, `intel_hdcp`, `intel_connector`, `intel_digital_connector_state`, `intel_atomic_state`, `intel_plane_state`, `intel_initial_plane_config`, `intel_crtc_scaler_state`, watermark structs for ILK/SKL/VLV/G4X, `intel_crtc_state`, `intel_pipe_crc`, `intel_flipq`, `intel_crtc`, `intel_plane`, `intel_hdmi`, `intel_dp_compliance`, `intel_pps`, `intel_psr`, `intel_dp`, `intel_lspcon`, `intel_digital_port`, `intel_dp_mst_encoder`, and `intel_colorop`. Inline helpers convert DRM base objects to Intel objects, fetch old/new atomic states, identify DP/HDMI/MST encoders, obtain attached DP/HDMI/digital-port structures, and convert many object pointer types to `struct intel_display *`.

## Control Flow
The file is mostly data definitions, but the inline helpers contain small control decisions. Encoder helpers branch on `enum intel_output_type` to determine DP, HDMI, DDI, or MST shape. Atomic helpers call DRM atomic accessors and cast returned states. CRTC helpers map state flags to modeset, fastset, and color-update decisions. The `_Generic` `to_intel_display()` macro selects the correct conversion by pointer type.

## State and Persistence Behavior
These structures hold nearly all display state. Atomic state persists across check/commit/cleanup and includes wakerefs, global objects, DPLL state, watermark flags, and RPS interactivity. CRTC and plane states separate userspace-facing DRM state from actual hardware state for verification and readout. Connectors cache EDID, DPCD/DSC/PSR/panel replay data, HDCP state, and hotplug retry state. DP state stores link rates, lane counts, MST topology, AUX, link-training history, tunneling, compliance, PPS, PSR, ALPM, and quirks. CRTC and plane objects hold runtime hardware resources, events, IRQ flags, watermark state, callbacks, and debug counters.

## Dependencies and Integration Points
The header pulls together DRM atomic/KMS types, DP/HDMI/DSC/HDCP concepts, display limits/enums, power domains, frontbuffer, DPLL, DSB, FBC, TC ports, VBT, panel, PSR, PPS, and PXP-related plane state. It is included by most display subsystems and is a high-coupling contract between modeset checking, hardware programming, state verification, suspend/resume, hotplug, link training, watermarks, color management, and debugfs.

## Risks
This header has a large blast radius. Adding fields to permanent objects can change memory layout and lifetime expectations; adding state to the wrong object can break atomic rollback or hardware verification. State duplication rules matter because many fields use DRM property blob references, VMA pointers, wakerefs, delayed work, and nested locks. Inline type conversions assume exact object embedding. DP/MST/HDCP/PSR fields have subtle synchronization requirements, and watermark/plane state affects underrun risk.

## Test Signals
Signals include all display build targets, atomic modeset and fastset tests, state readout/verification, suspend/resume, hotplug, DP/HDMI/eDP/MST link training, PSR/panel replay/DSC/FEC/VRR/ALPM coverage, HDCP tests, plane format/rotation/scaler tests, watermark underrun tests, and memory/leak checking for property blobs, wakerefs, work items, and VMA references.
