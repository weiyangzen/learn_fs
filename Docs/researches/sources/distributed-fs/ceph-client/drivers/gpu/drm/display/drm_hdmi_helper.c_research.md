# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_helper.c

Purpose: provides HDMI specification helper routines for HDR DRM infoframe construction, AVI infoframe colorimetry/bar/content-type fields, TMDS character-rate calculation, and HDMI audio clock regeneration N/CTS values.

Important APIs/types/functions: exports `drm_hdmi_infoframe_set_hdr_metadata`, `drm_hdmi_avi_infoframe_colorimetry`, `drm_hdmi_avi_infoframe_bars`, `drm_hdmi_avi_infoframe_content_type`, `drm_hdmi_compute_mode_clock`, and `drm_hdmi_acr_get_n_cts`. Internal data includes DRM-to-HDMI colorimetry encoding tables and a table of standard TMDS clocks with N/CTS values for 32 kHz, 44.1 kHz, and 48 kHz families.

Control flow: HDR metadata setup validates frame/state/blob/connector pointers, warns when the requested EOTF is not advertised by the sink, initializes the HDMI DRM infoframe, and copies type-1 metadata fields. AVI helpers translate DRM connector state fields directly into HDMI infoframe fields. `drm_hdmi_compute_mode_clock` starts from pixel clock in Hz, rejects non-8bpc VIC 1, normalizes YCbCr 4:2:2 to 8 bpc with a 12 bpc cap, halves the rate for YCbCr 4:2:0, doubles for double-clocked modes, and scales by `bpc / 8`. `drm_hdmi_acr_get_n_cts` rounds TMDS to kHz, finds an exact standard table entry or the "other" entry, chooses the sample-rate family in 48/44.1/32 kHz priority order, multiplies N for higher rates, and computes CTS when the table leaves it zero.

State and persistence: all state is caller-owned. Static const tables persist for lookup only. Infoframe structures are filled in memory supplied by callers and later packed/written by HDMI state helpers or drivers.

Dependencies and integration: relies on Linux HDMI infoframe helpers, DRM connector state, EDID/display info, CEA mode matching, and DRM mode flags. HDMI state helpers use TMDS and infoframe helpers during atomic checks; audio drivers use ACR helpers for hardware programming.

Risks: spec corner cases are important: VIC 1 deep color rejection, YCbCr 4:2:2 deep-color semantics, double-clock modes, 4:2:0 half-rate behavior, and sample rates divisible by multiple base families. HDR EOTF mismatch is only debug-logged, not rejected. Unsupported colorimetry indexes become "No Data".

Test signals: `drivers/gpu/drm/tests/drm_connector_test.c` covers TMDS clock calculations across RGB, YUV420, YUV422, deep color, double clock, and VIC 1 cases. Additional useful signals are N/CTS golden values, HDR infoframe validation, invalid metadata blobs, and AVI colorimetry/content type mapping.
