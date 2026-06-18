# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-i2s-audio.c

Purpose: implements the ASoC HDMI-codec bridge for the DesignWare HDMI I2S audio input. It configures DW-HDMI audio registers through parent-provided read/write callbacks and exposes codec operations for SoC audio graphs.

Important APIs/types/functions: `dw_hdmi_i2s_hw_params()` validates codec clock-provider roles, resets I2S FIFOs, enables I2S lanes by channel count, selects sample width and I2S/left/right-justified/DSP format, then programs DW-HDMI sample rate, channel status, count, allocation, and audio registers. Startup/shutdown enable/disable HDMI audio. `dw_hdmi_i2s_get_eld()` returns parent ELD. `dw_hdmi_i2s_get_dai_id()` maps OF graph port 2 to DAI id 0. Probe registers an `HDMI_CODEC_DRV_NAME` platform device with I2S support and max 8 channels.

Control flow: parent creates this child with `dw_hdmi_i2s_audio_data`. Probe wraps it in hdmi-codec pdata. On stream startup the codec enables HDMI audio; hw_params applies register configuration; shutdown disables audio. OF DAI lookup lets sound-card graph bindings identify the HDMI audio port.

State and persistence: no substantial local state after registering the codec pdev. Hardware audio format state persists in DW-HDMI registers until changed or reset.

Dependencies and integration: depends on ASoC HDMI codec, DRM bridge DW-HDMI headers for register constants, OF graph endpoint parsing, DMA mask setup for the codec pdev, and parent callbacks from `dw-hdmi-audio.h`.

Risks: uses bitwise OR in the clock-provider check; this works for booleans/bit values but is less idiomatic than logical OR. Unsupported sample widths leave `conf1` width bits at zero rather than failing unless format is unsupported. Lane enable depends on channel count constraints from upper layers. DAI id is hard-coded to OF port 2.

Test signals: ASoC card binding through port 2, hw_params for 2/4/6/8 channels, I2S/left/right/DSP formats, 16/24/32-bit samples, ELD propagation, plug callback, and startup/shutdown around display hotplug.
