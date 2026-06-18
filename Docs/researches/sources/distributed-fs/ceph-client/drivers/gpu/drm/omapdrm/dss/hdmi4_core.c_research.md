<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.c

## Purpose
`hdmi4_core.c` programs the OMAP4 HDMI core register block. It handles DDC/EDID reads, core video mode setup, AVI infoframe transmission, audio core and infoframe programming, audio start/stop, HDMI core debug dumps, and SoC-specific HDMI4 audio clock feature selection.

## Important APIs, types, and functions
External display functions include `hdmi4_core_ddc_init()`, `hdmi4_core_ddc_read()`, `hdmi4_core_powerdown_disable()`, `hdmi4_configure()`, `hdmi4_core_dump()`, and `hdmi4_core_init()`. Audio functions are `hdmi4_audio_config()`, `hdmi4_audio_start()`, and `hdmi4_audio_stop()`. Internal helpers include `hdmi_core_init()`, software reset assert/release helpers, `hdmi_core_video_config()`, `hdmi_core_write_avi_infoframe()`, `hdmi_core_av_packet_config()`, `hdmi_core_audio_config()`, and `hdmi_core_audio_infoframe_cfg()`.

## Control flow
DDC init enables DDC clocks, aborts any in-progress transaction, clocks SCL devices, and clears the DDC FIFO. DDC read waits for readiness, programs segment, slave address, offset, byte count, and command, checks bus-low and no-ack bits, then reads FIFO bytes with a timeout.

Video configuration initializes wrapper timing and format through common HDMI wrapper helpers, asserts core software reset, configures input bus width, dither/truncation, packet mode, HDMI/DVI mode, TMDS clock selection, releases reset, writes AVI infoframe data when in HDMI mode, and enables repeated AVI/audio packets as needed.

Audio configuration validates IEC/CEA inputs, derives word length and sample frequency, computes ACR N/CTS, chooses software or hardware CTS mode from SoC features, configures I2S, channel layout, DMA/FIFO formatting, IEC channel-status registers, audio infoframe bytes and checksum, and packet generation. Audio start/stop toggles core audio mode and wrapper audio core requests.

## State and persistence
Persistent software state is small: `core->base`, `core->cts_swmode`, `core->audio_use_mclk`, `core->wp`, and `core->adap` from related code. Hardware state is extensive in core system and AV registers: DDC transaction registers, video mode registers, packet control, AVI infoframe bytes, ACR, I2S, IEC channel status, audio layout, audio infoframe, and CEC-visible core state. Values persist until reconfigured, core reset, or power down.

## Dependencies and integration points
The file depends on HDMI4 register definitions from `hdmi4_core.h`, common HDMI wrapper functions from `hdmi.h`, ALSA IEC/CEA structures, DRM HDMI infoframe packing, SoC device matching, and platform resource mapping. `hdmi4.c` calls these routines during EDID reads, bridge enable, and audio callbacks.

## Risks
DDC polling is timeout based and can fail on stuck I2C lines or incomplete aborts. Video configuration assumes RGB/YUV444 24-bit packing and fixed core defaults; unsupported color/deep-color modes are not generalized. Audio mutates the supplied CEA infoframe for multi-channel operation and uses fixed channel mapping. SoC feature matching controls CTS and MCLK behavior; wrong match data can break audio clock recovery. The debug dump reads many registers and must run only while runtime PM keeps the block accessible.

## Test signals
Useful signals include reliable EDID reads for base and extension blocks, no DDC bus-low/no-ack errors with known-good sinks, HDMI and DVI video output, correct AVI infoframes, two-channel and multi-channel LPCM audio, valid ACR N/CTS for 32/44.1/48/96/192 kHz rates, audio start/stop without FIFO faults, debugfs core dumps, and SoC-specific audio behavior on OMAP4430 ES1, ES2, and later OMAP4 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.c -->
