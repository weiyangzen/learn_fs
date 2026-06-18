# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_hdmi.c

## Purpose
`evergreen_hdmi.c` programs DCE4 HDMI and DisplayPort audio/video-infoframe hardware for the Radeon display driver. It enables audio pins, writes HDMI ACR values, speaker allocation, ELD/SAD codec descriptors, AVI/VBI/audio infoframes, DTO clock ratios, color depth, mute state, and HDMI/DP secondary stream enables.

## Important APIs, Types, And Functions
Public hooks declared in `evergreen_hdmi.h` are implemented here. Audio enable and packet setup functions include `dce4_audio_enable()`, `dce4_set_audio_packet()`, and `dce4_set_mute()`. HDMI-specific configuration uses `evergreen_hdmi_update_acr()`, `evergreen_set_avi_packet()`, `dce4_hdmi_audio_set_dto()`, `dce4_hdmi_set_color_depth()`, and `evergreen_hdmi_enable()`. DP audio uses `dce4_dp_audio_set_dto()` and `evergreen_dp_enable()`. ELD/audio capability programming is handled by `dce4_afmt_write_latency_fields()`, `dce4_afmt_hdmi_write_speaker_allocation()`, `dce4_afmt_dp_write_speaker_allocation()`, and `evergreen_hdmi_write_sad_regs()`.

## Control Flow
Most functions are direct register-programming routines using `RREG32`, `WREG32`, `WREG32_OR`, `WREG32_AND`, `WREG32_P`, and endpoint codec accessors. `dce4_audio_enable()` updates `AZ_HOT_PLUG_CONTROL` based on an audio-pin enable mask, early-returning for a null pin. `evergreen_hdmi_update_acr()` selects hardware or software CTS behavior based on CRTC bits-per-color and writes 32/44.1/48 kHz CTS/N values.

Speaker allocation routines read the codec pin speaker register, clear the opposite transport mode and allocation mask, set HDMI or DP mode, and write either SADB byte 0 or a stereo fallback. `evergreen_hdmi_write_sad_regs()` maps CEA SAD formats to codec descriptor registers, selects the descriptor with the highest channel count for each type, and separately accumulates PCM stereo frequencies.

DTO setup chooses HDMI DTO0 or DP DTO1, programs source CRTC selection, and writes phase/module ratios. DP adjusts the module for DCE4.1 dentist divider when present. `evergreen_hdmi_enable()` checks the encoder's DIG AFMT block and connector audio capability, then enables AVI/audio infoframes and sample sending as appropriate; disable clears sample sending and infoframe control. `evergreen_dp_enable()` similarly enables DP secondary audio, timestamp, audio infoframe, and stream bits, with DP clock-dependent N-base multiplier programming on pre-DCE6 hardware.

## State And Persistence Behavior
The persistent state is hardware register state plus `dig->afmt->enabled`. The functions do not allocate memory or retain private software state. Register programming persists until mode set, disable, suspend/resume, or another encoder/audio path reprograms the same AFMT block. Connector-derived latency, SAD, and `display_info.has_audio` values are treated as current DRM/EDID state.

## Dependencies And Integration Points
This file integrates DRM encoder/connector/CRTC objects with Radeon private encoder structures (`radeon_encoder`, `radeon_encoder_atom_dig`, `radeon_connector_atom_dig`) and audio helpers from `radeon_audio.h`. It depends on CEA SAD definitions from DRM EDID/HDMI headers and on DCE4 register definitions in `evergreend.h`. The functions are called by Radeon mode-setting and audio setup paths when connectors are enabled, disabled, or reconfigured.

## Risks
Most risk is hardware sequencing and stale connector state rather than memory safety. Wrong AFMT offsets can program the wrong encoder. Enabling audio without valid connector capability can send unwanted packets. DTO ratio mistakes cause audio drift or silence. `evergreen_set_avi_packet()` assumes the supplied infoframe buffer has the expected HDMI header/payload layout; callers must provide a sufficiently sized encoded frame. DP DCE4.1 divider handling depends on correct `radeon_audio_decode_dfs_div()` behavior.

## Test Signals
Test signals include HDMI and DP audio presence in ALSA/ELD, correct speaker allocation for SADB-bearing and stereo-fallback sinks, stable audio at multiple pixel clocks, deep-color behavior at 8/10/12 bpc, mute bit toggling, AVI infoframe correctness, DP secondary stream enablement, and suspend/resume or hotplug reprogramming. Register traces around `HDMI_INFOFRAME_CONTROL0`, `AFMT_AUDIO_PACKET_CONTROL`, DTO registers, and `EVERGREEN_DP_SEC_CNTL` are useful when debugging.
