# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.c

Purpose: Implements the DCN10 stream encoder: timing/MSA programming, HDMI/DVI setup, DP/HDMI info packets, DP blank/unblank, MST VCP rate, audio packets, stereo sync, AV mute, and DIG-to-OTG routing.

Important APIs/types/functions: `dcn10_stream_encoder_construct()` installs `dcn10_str_enc_funcs`. Major APIs include DP/HDMI/DVI stream attribute setters, generic info packet writer, DP/HDMI packet update/stop helpers, immediate SDP send, DP blank/unblank, audio setup/enable/disable for DP and HDMI, audio clock lookup, and DP pixel format readback.

Control flow: DP attribute setup normalizes interlaced timing, maps pixel encoding/depth/color space into DP registers, and programs MSA timing. HDMI setup calls VBIOS encoder control, configures deep color and scrambling, enables mandatory packets, and clears AV mute. Info packet paths write AFMT generic slots and toggle HDMI or DP secondary-packet enables. DP blank defers disable to vblank, polls stream status, and resets steer FIFO; unblank programs M/N, starts DIG, releases FIFO, delays, and enables stream. Audio setup maps speakers to CEA channels, writes ACR/N/CTS tables or fallback values, and enables DP/HDMI audio packets.

State/persistence: Persistent state is base context, BIOS, engine id, register metadata, and stream encoder instance. Hardware state includes AFMT generic packet memory, DP MSA/timing, HDMI control/infoframe registers, DP secondary-packet enables, audio clock/channel registers, DIG source, and FIFO state.

Dependencies/integration: Depends on DC BIOS encoder control, link service DP trace hooks, fixed-point helpers, DPCD source sequence tracing, and AFMT power hooks.

Risks: Several packet writers cast byte payloads to `uint32_t *` and assume layout/alignment. Fixed waits may hide hardware stalls. DP info packet slot 1 is reserved for PSR firmware, and slot 4 for immediate SDP, so callers must avoid collisions. HDMI audio tables must match spec clocks.

Test signals: DP MSA register programming for RGB/YUV/interlace/colorimetry, HDMI deep-color/scramble behavior, info packet slot enable/disable, DP blank/unblank trace order, MST VCP fixed-point rounding, audio clock table lookup/fallback, speaker channel mapping, and pixel format readback.
