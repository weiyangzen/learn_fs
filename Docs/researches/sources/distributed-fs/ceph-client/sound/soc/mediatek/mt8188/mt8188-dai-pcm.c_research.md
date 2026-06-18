# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-pcm.c

Purpose: Implements the MT8188 PCM1 backend DAI, including PCM/I2S/DSP format selection, master/slave clock polarity, sync frequency setup, channel routing widgets, and clock supplies for PCMIF and ASRC blocks.

Important APIs and functions: `mt8188_dai_pcm_register()` registers the PCM DAI group. `mtk_dai_pcm_set_fmt()` decodes ALSA DAI format, inversion, and clock-provider flags into cached `mtk_dai_pcmif_priv` state. `mtk_dai_pcm_prepare()` programs hardware only if playback and capture widgets are inactive. `mtk_dai_pcm_configure()` writes sync frequency, clock domain, PCM mode, format, sync length, bit width, word length, master/slave mode, and clock inversion. `mtk_dai_pcm_mode()` maps supported rates to PCM mode values.

Control flow: Registration allocates `mtk_dai_pcmif_priv` at `dai_priv[PCM]`, exposes one DAI with symmetric rate and sample bits, and installs DAPM widgets/routes. Machine-driver `set_fmt` stores mode before stream prepare. On prepare, the driver avoids reconfiguring if either direction is already active, preserving symmetric full-duplex settings. Runtime rate is converted both through `mt8188_afe_fs_timing()` for sync frequency and `mtk_dai_pcm_mode()` for PCM mode.

State and persistence: Cached state includes `slave_mode`, `lrck_inv`, `bck_inv`, and PCM format. Hardware state persists in `PCM_INTF_CON1/2` and DAPM clock supply state for `aud_asrc11`, `aud_asrc12`, and `aud_pcmif`.

Dependencies and integration: Uses regmap, ASoC DAI ops, PCM params, `mt8188_afe_fs_timing()`, and register macros. Routes connect PCM1 playback from AFE outputs `O000/O001`, capture to `I002/I003`, and external endpoints `PCM1_INPUT`/`PCM1_OUTPUT`.

Risks: Slave-mode ASRC configuration is explicitly marked TODO, so slave mode may be incomplete despite format acceptance. `prepare` skips reconfiguration when either direction is active; a second stream with incompatible assumptions depends on symmetric constraints and machine-driver discipline. `bit_width` is taken from `dai->symmetric_sample_bits`, so format negotiation must set it as expected. Unsupported rates return `-EINVAL`; the rate table includes only 8/16/32/48 and 11.025/22.05/44.1 kHz.

Test signals: Playback and capture should be tested for I2S, DSP_A, and DSP_B formats, all inversion combinations, and master/slave clock-provider settings. Full-duplex tests should validate symmetric constraints and no midstream register churn. Slave-mode tests should specifically verify ASRC behavior because the code marks it incomplete.
