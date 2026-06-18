# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_stream_encoder.c

Purpose: Extends the DCN10 stream encoder for DCN20 features: expanded HDMI generic packet control, DSC PPS/config, dynamic metadata, SDP line selection, ODM combine, adjusted DP unblank sequencing, and FIFO diagnostics.

Important APIs/types/functions: `dcn20_stream_encoder_construct()` installs `dcn20_str_enc_funcs`. DCN20-specific handlers include HDMI packet update/stop, `enc2_dp_set_dsc_config()`, `enc2_dp_set_dsc_pps_info_packet()`, `enc2_set_dynamic_metadata()`, `enc2_stream_encoder_update_dp_info_packets_sdp_line_num()`, `enc2_stream_encoder_dp_unblank()`, `enc2_dp_set_odm_combine()`, and `enc2_get_fifo_cal_average_level()`.

Control flow: HDMI packet programming separates continuous/send bits from line registers and adds VTEM on packet 6. DSC PPS writes a 128-byte PPS SDP into GSP slots 7-10, configures PPS mode, line numbers, VBID6 update line, and enables GSP7. Dynamic metadata selects DP or HDMI/Dolby Vision packet paths, sets HUBP requestor and stream type, then enables or disables DME and packet transmission. DP unblank computes M/N with two-pixel-container and OPP-count handling, forces stream disabled, waits for status, toggles DIG start and steer FIFO reset, delays, then enables video. DP stream attributes reuse DCN10 and add `DP_SST_SDP_SPLITTING`.

State/persistence: Software state is inherited DCN10 stream encoder metadata. Hardware state includes DSC mode/slice/bytes-per-pixel, PPS GSP memory, VBID6 and GSP7 line controls, metadata engine and packet controls, ODM combine, SDP splitting, FIFO state, and inherited HDMI/DP/audio registers.

Dependencies/integration: Reuses many DCN10 helpers and depends on DSC packed PPS data, dynamic metadata modes, link service tracing, and Linux delays.

Risks: PPS writer assumes `hb1` is PPS and writes four generic packet slots from a 128-byte buffer; invalid buffers would corrupt SDP contents. Dynamic metadata changes require OTG master update lock by contract but this function does not enforce it. DP unblank waits up to 5000 iterations and may hide persistent stream-status failures.

Test signals: DSC enable/disable and PPS content/line programming, dynamic metadata for DP/HDMI/Dolby Vision, VTEM HDMI packet slot, adaptive-sync SDP line override, two-pixel-container M/N behavior, FIFO reset sequencing, ODM combine bit, and DSC state readback.
