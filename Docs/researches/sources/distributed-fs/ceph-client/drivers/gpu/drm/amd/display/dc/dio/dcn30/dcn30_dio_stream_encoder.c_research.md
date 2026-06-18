# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c

## Purpose
This file implements the baseline DCN30 DIO stream encoder. It programs HDMI and DP info packets, DSC PPS secondary data packets, HDMI/DVI stream attributes, audio packet setup, and the DCN30 `stream_encoder_funcs` table used by display mode set paths.

## Important APIs and Functions
`enc3_update_hdmi_info_packet` writes a VPG generic packet and maps hardware packet indices 0-14 to HDMI generic packet control and line registers. `enc3_stream_encoder_update_hdmi_info_packets` enables HDMI DB/audio clocking and programs AVI, HF-VSIF, gamut, vendor, SPD, HDR static metadata, and VTEM packets. `enc3_stream_encoder_stop_hdmi_info_packets` clears all generic HDMI packet slots.

`enc3_stream_encoder_update_dp_info_packets` writes VSC, SPD, HDR, and adaptive-sync SDPs through VPG and enables `DP_SEC_GSP*` bits plus master `DP_SEC_STREAM_ENABLE`; it also preserves stream enable when dynamic metadata is already active. `enc3_stream_encoder_update_dp_info_packets_sdp_line_num` moves adaptive-sync SDP to an OTG-referenced line when valid. `enc3_dp_set_dsc_config`, `enc3_dp_set_dsc_pps_info_packet`, and `enc3_read_state` handle DSC mode, PPS packet fragments in GSP11-14, VBID6 timing, and DSC debug readback.

HDMI/DVI setup functions either call VBIOS `encoder_control` or directly set DIG clock pattern and reset DIG FIFO through `DIG_START` when BIOS execution is avoided. HDMI setup configures deep color, scrambling for 340 MHz and above, general-control/null/audio packets, audio infoframe line, and AVMUTE. Audio helpers delegate to AFMT and program DP/HDMI audio registers, ACR/N/CTS values, and DP timestamps.

## Control Flow
The function table wires base DCN2 DP stream attributes and dynamic metadata to DCN30-specific HDMI packet, DP packet, DSC, and audio handlers. Constructor initialization is simple pointer assignment: context, BIOS, engine id, VPG, AFMT, register tables, shift/mask tables, and stream encoder instance.

## State and Persistence
Persistent state is entirely hardware-facing: HDMI generic packet controls, VPG packet RAM, DP secondary-packet enables, DSC mode/PPS/VBID registers, AFMT audio state, HDMI ACR registers, DIG reset state, and base object pointers. There is no heap allocation or software cache besides the initialized object.

## Dependencies and Integration Points
The file integrates with VPG (`update_generic_info_packet`), AFMT audio callbacks, DC BIOS encoder control, DC debug flags, `reg_helper` register macros, DCN1/DCN2 helper functions, audio clock calculation, DP trace/metadata infrastructure, and the public `stream_encoder` function table used by link/programming code.

## Risks and Test Signals
Risks include incorrect packet-index mapping, duplicate VSC writes at DP packet index 1, stale TODO behavior for PSR-SU VSC packets, HDMI scrambling/deep-color mismatches, DSC PPS line ordering relative to VBID6, and reliance on VBIOS unless `avoid_vbios_exec_table` is set. Test signals should include HDMI infoframe presence/stop, DP VSC/HDR/adaptive-sync SDP capture, DSC PPS packet capture, HDMI audio ACR validation at common pixel clocks, DP audio enable, DVI RGB/8bpc assertions, and register readback through `enc_read_state`.
