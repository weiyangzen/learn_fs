# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-card.c

## Purpose
Generic Freescale/NXP i.MX ASoC machine driver for device-tree-described cards. It supports plain CPU-codec links, ASRC DPCM front/back ends, TDM and DSD handling, and codec-specific rate/channel/MCLK policy for AKM codecs, CS42888, and WM8524.

## APIs, Types, and Functions
Key types are `enum codec_type`, `struct imx_akcodec_fs_mul`, `struct imx_akcodec_tdm_fs_mul`, `struct imx_card_plat_data`, `struct dai_link_data`, and `struct imx_card_data`. Important functions are `format_is_dsd()`, `format_is_tdm()`, `codec_is_akcodec()`, `akcodec_get_mclk_rate()`, `imx_aif_hw_params()`, `ak5558_hw_rule_rate()`, `imx_aif_startup()`, `imx_aif_shutdown()`, `be_hw_params_fixup()`, `imx_card_parse_of()`, and `imx_card_probe()`.

## Control Flow, State, and Persistence
Probe allocates card/private/platform data, parses the `model`, optional `audio-routing`, and one child node per DAI link. Each link gets CPU/platform components, optional codec components or dummy codec, link direction flags, DAI format, TDM slot count/width, and ASRC-specific dynamic/no-pcm behavior. Runtime startup applies channel/rate constraints from codec type and may add an AK5558 rate rule. `hw_params()` normalizes non-TDM streams to I2S or PDM for DSD, programs CPU and codec DAI formats and TDM slots, computes MCLK, sets CPU sysclk output and codec sysclk input, and shutdown clears sysclks. ASRC backends use fixed rate/format from the ASRC node.

## Dependencies and Integration
Depends on ASoC core, `simple-card-utils`, OF graph direction parsing, `fsl_sai.h`, ALSA PCM constraints, and codec DAI names for type detection. Integrates with SAI CPU DAIs, ASRC front/back end naming conventions (`HiFi-ASRC-FE`/`HiFi-ASRC-BE`), AKM/CS/WM codecs, and card-level DAPM routes.

## Risks and Test Signals
Risks include global mutation of `ak4497_fs_mul` based on one link's `fsl,mclk-equal-bclk`, static constraint-list objects shared across startups, reliance on codec DAI name strings, using the last codec DAI after a loop for sysclk, and DAPM route assumptions when the number of codecs or links varies. Test signals are card registration for single-link and three-link ASRC cards, I2S/TDM/DSD playback, codec-specific rate/channel constraint enforcement, MCLK frequency measurements, ASRC fixed output format, and suspend/resume through `snd_soc_pm_ops`.
