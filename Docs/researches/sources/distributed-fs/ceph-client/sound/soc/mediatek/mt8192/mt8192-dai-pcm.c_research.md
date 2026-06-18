# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-dai-pcm.c

This file implements the two modem PCM backend DAIs, `PCM 1` and `PCM 2`, plus their DAPM routing to/from DL, ADDA, I2S, and modem endpoints. It defines PCM-specific register values for left-channel repeat, VBT mode, modem selection, sync type, Bluetooth mic mode, AFIFO/ASRC selection, clock mode, word length, PCM mode, format, BCLK inversion, and enable state.

`mtk_dai_pcm_driver[]` exposes two full-duplex DAIs with 8/16/32/48-kHz rates and 16/24/32-bit formats. `mt8192_dai_pcm_register()` registers DAI drivers, widgets, and routes. `mtk_dai_pcm_hw_params()` translates the requested rate, skips reprogramming if playback or capture is already active, and writes PCM1 or PCM2 interface configuration.

State is entirely in AFE registers and ASoC DAPM widget active counts; there is no private per-DAI data. PCM1 is configured as slave, PCM mode B, one-BCLK sync, AFIFO, dual-mic TX, and no BCLK inversion. PCM2 uses PCM mode B, 32-BCLK word length, AFIFO, and rate encoding in `PCM2_INTF_CON`.

Dependencies are `mt8192-afe-common.h`, `mt8192-interconnection.h`, regmap, and ASoC DAPM/DAI helpers. Risks include stale hardware parameters when a second stream opens while the first keeps the widget active; symmetric rate/sample-bit settings reduce this but should be verified. Test signals are PCM1/PCM2 playback/capture, full-duplex same-rate operation, unsupported-rate rejection, modem loopback paths, and suspend/resume with PCM routes active.
