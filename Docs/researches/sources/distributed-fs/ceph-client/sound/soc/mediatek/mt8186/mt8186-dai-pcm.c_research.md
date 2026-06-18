# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-dai-pcm.c

## Purpose

`mt8186-dai-pcm.c` registers and configures the MT8186 PCM 1 DAI, used primarily for Bluetooth SCO style PCM/I2S connectivity. It defines the PCM format/private-state model, DAPM mixers and loopback muxes, GPIO power events, register programming for `PCM_INTF_CON1`, and the single `PCM 1` DAI driver. The complete 419-line file was read.

## Important APIs, Types, and Functions

The private type is `struct mtk_afe_pcm_priv`, containing id, PCM format, bit-clock inversion, and frame-clock inversion. Configuration enums encode register values for TX channel repeat, VBT 16 kHz mode, external modem select, sync type, BT mode, AFIFO source, clock master/slave, word length, 24-bit mode, PCM mode, format, and clock inversion.

Key functions are `mtk_pcm_en_event()`, `mtk_dai_pcm_hw_params()`, `mtk_dai_pcm_set_fmt()`, `init_pcm_priv_data()`, and public `mt8186_dai_pcm_register(struct mtk_base_afe *afe)`. Important data objects include `mtk_dai_pcm_widgets[]`, `mtk_dai_pcm_routes[]`, `mtk_dai_pcm_driver[]`, and `mtk_dai_pcm_ops`.

## Control Flow

During registration, the driver allocates an AFE sub-DAI record, adds it to `afe->sub_dais`, attaches the PCM DAI driver and DAPM topology, allocates private state, initializes it to I2S format with non-inverted clocks, and stores it at `afe_priv->dai_priv[MT8186_DAI_PCM]`.

`mtk_dai_pcm_set_fmt()` is called by the ASoC core from machine-link format settings. It maps `SND_SOC_DAIFMT_I2S`, `LEFT_J`, `DSP_A`, and `DSP_B` onto internal PCM format values, then maps the inversion mask onto bit-clock and frame-clock inversion flags.

`mtk_dai_pcm_hw_params()` checks the playback and capture DAPM widgets; if either is already active it returns without reprogramming the shared PCM interface. Otherwise it builds `pcm_con`, sets external modem and master mode defaults, inserts rate mode from `mt8186_rate_transform()`, inserts previously selected format and inversion flags, derives 16/24-bit and 32/64-BCK-cycle word settings from the requested PCM format, and writes all non-enable bits to `PCM_INTF_CON1` using mask `0xfffffffe`.

DAPM supply event `mtk_pcm_en_event()` requests or releases PCM GPIO configuration on power up/down.

## State and Persistence Behavior

Runtime state lives in `struct mtk_afe_pcm_priv` under `afe_priv->dai_priv`. It persists between `set_fmt()` and `hw_params()` so machine-link format choices can be applied when hardware params arrive. Hardware register state is volatile in `PCM_INTF_CON1`, plus DAPM power state for `PCM_EN_SFT`. No filesystem or firmware persistence is used.

## Dependencies and Integration Points

The file depends on `linux/regmap.h`, `sound/pcm_params.h`, `mt8186-afe-common.h`, `mt8186-afe-gpio.h`, and `mt8186-interconnection.h`. Its DAPM routes connect `DL2`, `DL4`, I2S loopback paths, `I2S0`, and `I2S3`. Machine-card integration appears in the MT6366 card where the `PCM 1` backend is connected to the `bt-sco` codec with I2S/NB_IF format.

## Risks and Edge Cases

The shared interface is not reprogrammed if either playback or capture widget is active, so late format/rate changes while the opposite direction is active are ignored. Unsupported DAIFMT values silently default to I2S or non-inverted clocks rather than returning an error. `mt8186_rate_transform()` output is not validated locally. The register mask intentionally avoids bit 0 so DAPM controls enable state, but accidental field additions in `PCM_INTF_CON1` could be missed if the hard-coded mask is not updated.

## Test Signals

Build coverage should include `CONFIG_SND_SOC_MT8186`. Runtime tests should confirm `PCM 1` playback/capture appears, GPIO requests occur on DAPM power changes, BT SCO backend opens at 8/16/32/48 kHz as advertised, DAIFMT changes alter `PCM_FMT`, `PCM_SYNC_OUT_INV`, and `PCM_BCLK_OUT_INV`, and loopback muxes route PCM in/out to I2S widgets as expected.
