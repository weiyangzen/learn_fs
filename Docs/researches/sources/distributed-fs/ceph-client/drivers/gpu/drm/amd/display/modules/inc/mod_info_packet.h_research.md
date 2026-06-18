# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_info_packet.h

Purpose: declares helpers for building DisplayPort/HDMI secondary-data and info-frame packets used for VSC colorimetry, HDMI Forum VSIF, and Adaptive Sync signaling.

Important APIs/types: functions include `set_vsc_packet_colorimetry_data`, `mod_build_vsc_infopacket`, `mod_build_hf_vsif_infopacket`, `mod_build_adaptive_sync_infopacket`, and version-specific Adaptive Sync builders. `enum adaptive_sync_type` distinguishes none, DP, PCON whitelisted/non-whitelisted FreeSync, and eDP. `enum adaptive_sync_sdp_version`, `struct frame_duration_op`, and `struct AS_Df_params` describe Adaptive Sync SDP payload details.

Control flow role: callers supply stream timing/color state and receive a populated `dc_info_packet`. The implementation chooses the packet revision and payload based on stream/link capabilities.

State and persistence: no owned module state; packets are filled into caller-provided buffers and marked valid/invalid.

Dependencies and integration: includes `dm_services.h` and `mod_shared.h`, forward-declares DC stream/info-packet/VRR types, and is consumed by display update code and FreeSync/VRR packet generation.

Risks: packet byte positions and enum values are spec-bound. Null stream handling differs by packet type; Adaptive Sync dispatch guards some but not all fields in the implementation.

Test signals: VSC colorimetry for RGB/YCbCr/color-depth/range combinations, PSR/Replay packet revisions, HDMI 3D and HDMI VIC VSIF checksums, Adaptive Sync v1/v2 headers, and null/unsupported type behavior.
