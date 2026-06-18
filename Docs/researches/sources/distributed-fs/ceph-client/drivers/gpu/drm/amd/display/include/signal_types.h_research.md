# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/signal_types.h

Purpose: Defines display signal-type bit constants and inline predicates for classifying HDMI, DP, eDP, LVDS, DVI, analog RGB, TMDS, audio-capable, embedded, and virtual signals.

Important APIs and types: `enum signal_type`, `TMDS_MIN_PIXEL_CLOCK`, `TMDS_MAX_PIXEL_CLOCK`, `signal_type_to_string`, `dc_is_hdmi_tmds_signal`, `dc_is_hdmi_signal`, `dc_is_dp_sst_signal`, `dc_is_dp_signal`, `dc_is_embedded_signal`, `dc_is_lvds_signal`, `dc_is_dvi_signal`, `dc_is_rgb_signal`, `dc_is_tmds_signal`, `dc_is_dvi_single_link_signal`, `dc_is_dual_link_signal`, `dc_is_audio_capable_signal`, and `dc_is_virtual_signal`.

Control flow: Callers use predicates to branch into link-specific programming paths, choose packet formats, determine audio support, map HDCP operation modes, and validate TMDS clocks. `signal_type_to_string` supports diagnostics.

State and persistence: Stateless inline classification. The enum values are bit flags, but most predicates test equality rather than bit membership, so combined signal values are generally not supported.

Dependencies and integration points: Used by FreeSync info packet construction, HDCP signal-to-mode mapping, link service code, encoder setup, and audio decisions.

Risks: Because predicates use equality, callers passing masks or combined flags will get false negatives. `dc_is_hdmi_tmds_signal` currently aliases HDMI only, while `dc_is_tmds_signal` includes DVI and HDMI; callers must choose the intended semantic. Pixel clock constants apply to TMDS and should not be reused for DP.

Test signals: Predicate matrix tests for every enum value, string coverage, HDCP mode mapping, FreeSync packet selection for HDMI vs DP, and audio-capable classification.
