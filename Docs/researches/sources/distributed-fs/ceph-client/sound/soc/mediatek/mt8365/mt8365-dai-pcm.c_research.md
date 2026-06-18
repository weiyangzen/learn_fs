# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-pcm.c

Purpose: Implements the MT8365 PCM1 backend DAI, including PCM interface format selection, master/slave mode, clock polarity, sample-rate encoding, bit-width/BCLK ratio programming, DAPM widgets/routes, and private state allocation.

Important APIs and functions: `mt8365_dai_pcm_register()` registers the PCM1 DAI driver plus `PCM1 Out`/`PCM1 In` widgets and routes. Runtime operations are `mt8365_dai_pcm1_startup()`, `mt8365_dai_pcm1_shutdown()`, `mt8365_dai_pcm1_prepare()`, and `mt8365_dai_pcm1_set_fmt()`. Hardware helpers are `mt8365_dai_configure_pcm1()`, `mt8365_dai_enable_pcm1()`, and `mt8365_dai_disable_pcm1()`. `struct mt8365_pcm_intf_data` stores the selected format, polarity, and slave-mode flags.

Control flow: `set_fmt` accepts only `SND_SOC_DAIFMT_I2S`, records normal/inverted BCLK and LRCLK polarity, and maps clock-provider mode to master or slave operation. Startup enables the AFE main clock only when the DAI was not already active. Prepare skips reconfiguration when another stream on the symmetric full-duplex DAI is already active; otherwise it builds `PCM_INTF_CON1_CONFIG_MASK` from master/slave flags, polarity bits, PCM/I2S format, sync length, one of 8/16/32/48 kHz rate encodings, 16-bit/32-BCLK or 24-bit/64-BCLK mode, and `PCM_INTF_CON1_EXT_MODEM`, then enables PCM1. Shutdown disables PCM1 and the main clock once no stream remains active.

State and persistence: The mutable interface mode is held in `afe_priv->dai_priv[MT8365_AFE_IO_PCM1]`. ALSA DAI symmetry flags enforce symmetric rate and sample bits, and runtime active counts prevent conflicting reconfiguration across playback/capture. Register state persists in `PCM_INTF_CON1` until disabled or overwritten.

Dependencies and integration points: Depends on MT8365 AFE clock helpers, `mt8365-reg.h` PCM bit definitions, ALSA SoC DAI callbacks, and DAPM routing between O07/O08 and I09/I22. The PCM1 DAI is a backend consumed by the MT8365 machine driver or device-tree-described links.

Risks: Supported rates are exactly 8, 16, 32, and 48 kHz despite the broader ASoC framework allowing many PCM rates elsewhere. Slave mode has a TODO for ASRC setup, so capture/playback synchronized to an external clock may be incomplete. `dai->symmetric_sample_bits` is used as the configured bit width; this relies on core DPCM negotiation having set it as expected. Only I2S formatting is accepted even though the register field has multiple PCM format values.

Test signals: PCM1 playback and capture at all four supported rates, S16 and S32 formats, master and slave clock-provider settings, all four inversion modes, simultaneous playback/capture to confirm prepare skip behavior, and register traces on `PCM_INTF_CON1`.
