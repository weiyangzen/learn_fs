<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hdmi.h -->
# sources/distributed-fs/ceph-client/include/linux/hdmi.h

Purpose: This header defines common HDMI InfoFrame, HDR metadata, and packet helper interfaces used by DRM/display drivers and related display code.

Important APIs/types/functions: It enumerates HDMI packet/infoframe types, colorspaces, scan modes, colorimetry, aspect ratios, quantization ranges, content types, HDR EOTF/metadata types, audio coding/sample sizes/rates, 3D structures, and SPD source device info. Structures include `hdmi_any_infoframe`, `hdmi_avi_infoframe`, `hdmi_drm_infoframe`, `hdmi_spd_infoframe`, `hdmi_audio_infoframe`, `hdmi_vendor_infoframe`, `hdr_static_metadata`, `hdr_sink_metadata`, `union hdmi_vendor_any_infoframe`, and `union hdmi_infoframe`. APIs initialize, check, pack, pack-only, unpack, log, and DP-pack audio infoframes.

Control flow, state, and persistence: Callers fill a typed infoframe, run init/check helpers, then pack it into the HDMI wire buffer with header/checksum. `pack()` variants may validate/update frame state; `pack_only()` assumes validation requirements are met. The union pack/unpack path dispatches based on the common `type` header.

Dependencies/integration: It depends on Linux device/types and `struct dp_sdp` for DisplayPort audio SDP packing. It mirrors CTA/CEA/HDMI field definitions and is used by display bridge/encoder drivers.

Risks and test signals: Buffer sizing must account for header plus payload. Enum values must match standards. HDR and vendor infoframes require correct OUI and length. Tests should include golden byte encodings for AVI/SPD/audio/vendor/DRM frames, invalid enum rejection, short buffer handling, checksum validation, unpack round trips, and DP audio conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hdmi.h -->
