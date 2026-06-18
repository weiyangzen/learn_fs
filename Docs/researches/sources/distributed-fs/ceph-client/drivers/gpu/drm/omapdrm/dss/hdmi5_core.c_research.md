# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5_core.c

Purpose: Provides the OMAP5 HDMI core programming library for DDC, video frame composer, packetizer/sampler, CSC range conversion, AVI infoframe emission, interrupt masking, and audio core/audio infoframe configuration.

Important APIs/functions: `hdmi5_core_ddc_init()`, `hdmi5_core_ddc_read()`, and `hdmi5_core_ddc_uninit()` configure the DesignWare HDMI I2C master and poll EDID bytes. `hdmi5_configure()` is the main video setup entry: masks interrupts, chooses quantization range, initializes core timing state, configures wrapper timing/format/interface, programs CSC, frame composer, packetizer, sampler, optional AVI infoframe, and unmasks interrupts. `hdmi5_audio_config()` validates IEC/CEA audio metadata, computes ACR N/CTS via `hdmi_compute_acr()`, configures wrapper DMA/FIFO format, core audio registers, and CEA audio infoframe. `hdmi5_core_init()` maps the `core` resource.

Control flow: Video configuration starts from `struct hdmi_config`, adjusts timing for interlace and double-clock, programs wrapper-facing timing first, then programs core frame composer registers and CSC. HDMI mode emits AVI infoframes; DVI mode leaves infoframes disabled. DDC read clears DONE/ERROR bits, issues a segment-aware read operation per byte, polls status with retries, and returns `-EIO` on error/timeout.

State and persistence: The code stores no persistent data beyond register state and the mapped `core->base`. Temporary config structs are stack-local. Audio configuration copies no state; callers cache audio settings in `hdmi5.c`.

Dependencies/integration: Uses `hdmi5_core.h` register definitions, `hdmi.h` common structures, HDMI wrapper configuration helpers, DRM HDMI AVI helpers, ALSA IEC958/CEA definitions, and shared ACR calculation.

Risks and test signals: DDC polling is synchronous and may block roughly one byte times retry sleep on bad sinks. Only 16-bit LPCM word length is accepted. Quantization range policy treats VIC 1 as full and other CEA VICs as limited. CSC is always enabled for range mapping. Validate EDID segment reads, HDMI/DVI range behavior, double-clock/interlaced timing fields, 2/6/8 channel LPCM, invalid sample widths/rates, and debugfs register dumps.
