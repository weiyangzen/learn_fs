# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4_core.c

## Purpose
`hdmi4_core.c` is the OMAP4/TI81xx HDMI core programming library used by the fbdev OMAP DSS HDMI path. It owns the HDMI4 core register block below the wrapper: DDC/EDID reads, video core reset and mode setup, AVI/audio packet programming, audio clock regeneration, I2S/channel-status programming, and debug register dumps.

## Important APIs, types, and functions
External entry points are `hdmi4_read_edid`, `hdmi4_configure`, `hdmi4_core_dump`, `hdmi4_core_init`, `hdmi4_audio_config`, `hdmi4_audio_start`, and `hdmi4_audio_stop`. Internal helpers include `hdmi_core_ddc_init`, `hdmi_core_ddc_edid`, `hdmi_core_init`, reset/powerdown helpers, `hdmi_core_video_config`, `hdmi_core_write_avi_infoframe`, `hdmi_core_av_packet_config`, `hdmi_core_audio_config`, and `hdmi_core_audio_infoframe_cfg`. It uses `struct hdmi_core_data`, `struct hdmi_wp_data`, `struct hdmi_config`, `struct omap_dss_audio`, and HDMI4-specific register symbols from `hdmi4_core.h`.

## Control Flow
EDID reads initialize DDC clocks, abort any in-progress transaction, clear the FIFO, read the base block, validate its checksum, and optionally read one extension block. Video configuration initializes wrapper timing and format first, asserts HDMI core software reset, disables powerdown, programs input bus width/dither/packet mode/DVI-HDMI mode/TMDS clock, releases reset, then writes and repeats AVI/audio packets when HDMI mode is selected. Audio configuration validates IEC/CEA metadata, derives N/CTS with `hdmi_compute_acr`, selects software or hardware CTS mode by SoC feature, configures wrapper DMA/FIFO, programs ACR/I2S/channel status registers, writes the CEA audio infoframe, and start/stop toggles audio mode plus wrapper core request.

## State and Persistence
Software state is limited to `core->base` plus feature decisions from `dss_has_feature`; the larger state is register-resident in DDC, SYS, AV packet, ACR, I2S, and infoframe registers. Audio setup mutates `audio->cea->db1_ct_cc` and `db4_ca` for multi-channel layouts, so caller-owned configuration can be changed.

## Dependencies and Integration Points
The file depends on `hdmi4_core.h`, common HDMI wrapper helpers from `hdmi.h`/`hdmi_wp.c`, ALSA IEC958 and CEA audio structs, Linux HDMI infoframe packing, and DSS feature flags. It is called by the OMAP4 HDMI display driver and shares PLL/PHY/wrapper state with the rest of the HDMI stack.

## Risks
DDC polling and FIFO reads are timeout-driven and can fail on stuck sinks, bus-low, no-ack, or bad checksums. Only one EDID extension is read. Video programming assumes 24-bit RGB/YUV444-style packing and fixed core defaults. Audio behavior depends on SoC feature flags, fixed channel remapping, and in-place CEA infoframe edits.

## Test Signals
Useful signals include base and extension EDID reads, DDC bus-low/no-ack fault tests, HDMI and DVI video modes, AVI infoframe inspection, 2-channel and multi-channel LPCM playback, 16/24-bit IEC word-length cases, ACR N/CTS checks across 32-192 kHz sample rates, audio start/stop around display disable, and debugfs core register dumps while runtime PM is active.
