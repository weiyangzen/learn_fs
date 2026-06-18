# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn42/dcn42_dio_stream_encoder.c

## Purpose
Implements the DCN42 stream encoder by reusing DCN401 DP/DVI and common packet behavior while adding DCN42-specific HDMI setup, DP/HDMI audio control through APG, HDMI info packet programming, DSC PPS packet handling, DP packet stop semantics, and audio clock gating.

## Important APIs, Types, And Functions
`dcn42_dio_stream_encoder_construct()` installs `dcn42_str_enc_funcs` and wires context, BIOS, VPG, APG, and register tables. Static functions include `enc42_stream_encoder_hdmi_set_stream_attribute()`, `enc42_stream_encoder_stop_dp_info_packets()`, `enc42_stream_encoder_update_hdmi_info_packets()`, `enc42_dp_set_dsc_pps_info_packet()`, DP/HDMI audio setup/enable/disable helpers, `enc42_se_enable_audio_clock()`, `enc42_audio_mute_control()`, and `enc42_reset_hdmi_stream_attribute()`.

## Control Flow
HDMI setup mirrors DCN401 but writes DCN42 field placement, configures deep color/scrambling/audio info, and sets audio info line through `HDMI_INFOFRAME_CONTROL0`. HDMI info packet update disables double-buffering, enables APG clock, and writes mandatory/optional packets in a fixed slot order. DP DSC PPS enable marks GSP11 as PPS, splits the packed 128-byte PPS across VPG packet slots 11-14, programs PPS/VBID line numbers, and enables GSP11 plus secondary stream; disable clears GSP11/PPS. Audio setup enables APG clock, selects the AZ source, configures DP timestamp/N or HDMI ACR, calls APG setup, then enables APG. Stop/disable paths clear packet bits but preserve `DP_SEC_STREAM_ENABLE` when other secondary packets remain.

## State And Persistence
State is held in registers, the base stream encoder object, and the attached APG pointer. The file persists no heap state. It assumes `enc->apg` is present for audio operations and uses `ASSERT` before APG-dependent flows.

## Dependencies And Integration Points
The implementation includes DCN401 stream encoder helpers and inherited DCN30/DCN32/DCN35 functions. It integrates with VBIOS encoder control, APG audio packet generation, VPG generic info packet updates, `get_audio_clock_info()`, DP/HDMI secondary packet registers, and DCN42 resource construction.

## Risks
APG must be correctly attached; missing APG breaks audio. DSC PPS uses four VPG slots starting at 11, so slot allocation conflicts would corrupt packets. Several inherited DCN401 helpers program register fields that must remain valid for DCN42. HDMI and DP secondary packet control registers are shared with audio/infoframes, making disable logic sensitive to bit preservation. Scrambling and deep-color decisions must match HDMI sink capabilities from higher layers.

## Test Signals
Exercise DP and HDMI audio enable/disable/mute, HDMI infoframe updates, DSC stream enable/disable with PPS packets, DP packet stop with audio still active, HDMI scrambling above 340 MHz, mode-set reuse of DCN401 DP/DVI paths, and build validation that all DCN42 register fields and APG callbacks resolve.
