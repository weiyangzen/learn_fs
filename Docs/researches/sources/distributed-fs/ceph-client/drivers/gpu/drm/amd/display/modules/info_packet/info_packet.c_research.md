# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/info_packet/info_packet.c

Purpose: builds DisplayPort VSC SDPs, HDMI vendor-specific infoframes, and Adaptive Sync SDPs from stream/link/timing/color inputs.

Important APIs: `set_vsc_packet_colorimetry_data()` encodes DP colorimetry, pixel encoding, color depth, range, and content type into VSC payload bytes. `mod_build_vsc_infopacket()` chooses VSC revisions for 3D stereo, PSR, Panel Replay, and colorimetry. `mod_build_hf_vsif_infopacket()` builds HDMI VSIF for 3D and HDMI VIC modes with checksum. `mod_build_adaptive_sync_infopacket()` dispatches to v1/v2 builders.

Control flow: VSC revision starts undefined, then is promoted by stereo, PSR, Replay, colorimetry, and Panel Replay priority. Revision-specific blocks set packet headers/payload length and validity. Adaptive Sync clears the packet, selects DP/eDP/PCON behavior, and writes v1 or v2 SDP headers. VSIF returns early unless 3D or HDMI VIC mode is required.

State and persistence: no owned state; all output is written into caller-provided `struct dc_info_packet`. The code sets `valid` only for generated packets.

Dependencies and integration: depends on DC stream/link/timing structures, color-space and pixel-encoding enums, Replay/PSR settings, and `mod_shared.h` transfer-function definitions. FreeSync and display update paths consume these packets.

Risks: packet byte offsets are spec-bound. `mod_build_vsc_infopacket()` does not fully clear payload for all revisions, so callers should provide clean packet storage. `mod_build_adaptive_sync_infopacket()` sets `valid = false` before `memset`, which is harmless but redundant. Checksum and length errors can cause sinks to ignore HDMI VSIF.

Test signals: VSC revision selection matrix for PSR1, PSR-SU, Replay, Panel Replay, colorimetry, and 3D; DP colorimetry for RGB/YCbCr/BT2020/gamma fallback; VSIF checksum for all 3D formats and HDMI VIC; Adaptive Sync v1/v2 payload bytes.
