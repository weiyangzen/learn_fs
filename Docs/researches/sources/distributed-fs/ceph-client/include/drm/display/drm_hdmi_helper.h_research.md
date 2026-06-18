# sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_helper.h

Purpose: common HDMI helpers for AVI/HDR infoframe fields, content type, TMDS character clock calculation, and ACR N/CTS audio clock recovery values.

Important APIs/types/functions: `drm_hdmi_avi_infoframe_colorimetry`, `drm_hdmi_avi_infoframe_bars`, `drm_hdmi_infoframe_set_hdr_metadata`, `drm_hdmi_avi_infoframe_content_type`, `drm_hdmi_compute_mode_clock`, and `drm_hdmi_acr_get_n_cts`.

Control flow: HDMI drivers derive infoframes from connector state, compute TMDS character rate from mode/bpc/output format, and derive ACR values for audio sample rates during modeset/audio setup.

State and persistence: no header state. Infoframes are transient packet data and clock helpers are pure calculations.

Dependencies and integration points: Linux HDMI infoframe definitions, DRM connector state, display modes, output color formats, HDMI bridge/encoder implementations, and audio setup.

Risks and test signals: wrong colorimetry/range/content, omitted HDR metadata, TMDS errors for YCbCr 4:2:0/high bpc, and bad ACR values are risks. Test AVI/HDR packets, RGB/YUV formats, 8/10/12 bpc, audio sample rates, and sink compliance.
