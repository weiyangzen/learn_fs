# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5_core.c

## Purpose
`hdmi5_core.c` programs the OMAP5/DRA7 HDMI core IP beneath the wrapper. It implements DesignWare-style I2C-master EDID reads, frame composer timing, packetizer/sampler setup, CSC/range conversion, AVI infoframe fields, core interrupt masks, GPA audio setup, ACR N/CTS programming, audio infoframe registers, debug dumps, and core resource mapping.

## Important APIs, types, and functions
External functions are `hdmi5_read_edid`, `hdmi5_core_dump`, `hdmi5_configure`, `hdmi5_audio_config`, and `hdmi5_core_init`. Internal helpers include `hdmi_core_ddc_init`, `hdmi_core_ddc_uninit`, `hdmi_core_ddc_edid`, `hdmi_core_init`, `hdmi_core_video_config`, packetizer/CSC/sampler helpers, `hdmi_core_write_avi_infoframe`, `hdmi_core_csc_config`, interrupt mask/unmask helpers, `hdmi5_core_audio_config`, and `hdmi5_core_audio_infoframe_cfg`.

## Control Flow
EDID read initializes the I2C master timing counters, reads the base block one byte at a time, clamps extension count to the caller buffer, then reads extensions and masks I2C interrupts. Video configure masks core interrupts, derives wrapper and frame-composer timing from `struct hdmi_config`, writes wrapper timing/format/interface registers, programs limited-range CSC, sets the infoframe quantization range, configures frame composer, packetizer, CSC, sampler, optionally writes AVI infoframe, enables the video path, and unmutes core interrupts. Audio config validates pointers and 16-bit LPCM word length, maps IEC sample frequency, computes ACR, chooses 2/6/8-channel layout from CEA channel count, configures wrapper DMA/FIFO, then programs core audio and infoframe registers.

## State and Persistence
Software state is only `core->base`; all operational state is in core and wrapper registers. `hdmi5_configure` mutates `cfg->infoframe.quantization_range` to limited. Audio configuration is not cached here; `hdmi5.c` caches it for restore after display enable.

## Dependencies and Integration Points
The file depends on `hdmi5_core.h`, shared `hdmi.h` helpers/macros, `hdmi_wp.c`, Linux HDMI AVI packing, DRM EDID length constants, ALSA IEC958/CEA audio definitions, and shared `hdmi_compute_acr`.

## Risks
DDC polling can spend significant time per byte on bad sinks and has no interrupt-driven recovery. Only 16-bit LPCM samples are accepted. CSC/range handling is fixed to 24-bit limited-range behavior. Frame timing subtracts one from horizontal sync and has limited interlace handling, while `hdmi5.c` rejects interlace.

## Test Signals
Validate EDID base and multiple extension blocks, DDC timeout/error paths, frame composer values for representative CEA/VESA modes, HDMI versus DVI infoframe behavior, quantization range on sinks, audio configs for 2/6/8 channels at 32-192 kHz, rejection of unsupported word lengths, and debugfs register dumps.
