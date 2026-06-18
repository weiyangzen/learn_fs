# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-etdm.c

## Purpose
Implements MT8195 eTDM, HDMI TX, and DP TX digital audio DAIs. It defines capture/playback DAIs for ETDM1/2 input, ETDM1/2/3 output, and DPTX, plus DAPM routing, clock source controls, MCLK setup, TDM format handling, cowork synchronization, channel disable handling, HDMI/DP channel muxing, and trigger-time enable sequencing.

## Important APIs, Types, and Functions
`mt8195_dai_etdm_register()` registers this sub-DAI block. DAI ops include `mtk_dai_etdm_startup()`, `mtk_dai_etdm_shutdown()`, `mtk_dai_etdm_hw_params()`, `mtk_dai_etdm_trigger()`, `mtk_dai_etdm_set_sysclk()`, `mtk_dai_etdm_set_fmt()`, `mtk_dai_etdm_set_tdm_slot()`, and HDMI/DP variants `mtk_dai_hdmitx_dptx_*`. `mtk_dai_etdm_configure()` writes common CON0 format/word/channel/slave fields, then dispatches to `mtk_dai_etdm_in_configure()` or `mtk_dai_etdm_out_configure()`. `mtk_dai_etdm_mclk_configure()` selects APLL parent and divider rate. `mt8195_afe_enable_etdm()` and `mt8195_afe_disable_etdm()` maintain an enable reference count protected by `afe_ctrl_lock`.

Key state is `struct mtk_dai_etdm_priv`: clock/data mode, master/slave flags, inversion, format, slots, LRCK width, MCLK frequency/source/direction, cowork source and slave list, disabled input channels, and enable refcount. Device-tree parsing occurs in `mt8195_dai_etdm_parse_of()`.

## Control Flow
Registration attaches DAI drivers, controls, widgets, and routes, allocates per-eTDM private data, aliases DPTX state to ETDM3_OUT, parses DT properties, and computes cowork master/slave lists. Startup enables MCLK divider and audsys clock gates. In cowork mode it enables the master clock and every slave gate. Shutdown reverses that. DAI probe supports an always-on MCLK rate from DT by runtime-resuming the AFE, configuring the clock, enabling it, then releasing runtime PM.

`hw_params` calculates rate, bit width, and channels. In cowork mode it configures the master first, then each slave and sync source selection. Otherwise it configures only the target DAI. Common configuration validates eTDM id, forces slaves when cowork source is set, fixes one-pin channel counts to 2/4/8/16/24, rejects bit-clock rates above 24.576 MHz, writes format/bit length/word length/channel count/slave mode, and programs input/output-specific registers. Input configuration sets AFIFO mode, LRCK width, multi-pin mode, disabled channel pairs, FS timing for masters, and LRCK/BCK inversion. Output configuration sets relatch domain, LRCK width, slave delay behavior or master FS timing, relatch enable timing, and inversion.

HDMI/DP paths use ETDM_OUT3 registers. DPTX additionally programs `AFE_DPTX_CON` channel enable, channel count, and word length; for 8-channel mode it forces one-pin ETDM data mode and 8 channels. HDMI uses multi-pin mode. Triggers enable DPTX first/last around ETDM_OUT3 enable. Generic eTDM triggers enable master before cowork slaves and disable slaves before master.

## State and Persistence
Format, inversion, slave mode, TDM slot width, MCLK direction/frequency, disabled input channels, cowork relationships, and enable refcounts persist in `afe_priv->dai_priv[]`. DT properties persist in private state: `mediatek,<etdm>-mclk-always-on-rate`, `mediatek,<etdm>-multi-pin-mode`, `mediatek,<etdm>-cowork-source`, and input-only `mediatek,<etdm>-chn-disabled`. Hardware register state persists through regmap cache and runtime PM owned by the AFE platform driver.

## Dependencies and Integration Points
Depends on MT8195 AFE clock helpers, runtime PM, regmap, ASoC DAI/DAPM/control APIs, and `mt8195_afe_fs_timing()`. Integrates with audsys gate ids (`aud_tdm_in`, `aud_i2sin`, `aud_tdm_out`, `aud_i2s_out`, `aud_hdmi_out`), top clock selectors/dividers, the machine driver's ETDM BE links, DPTX/HDMI codec init, RT5682/RT1011 clock programming, and SOF route fixups. DAPM routes connect memif I/O matrix nodes to ETDM playback/capture and DL10 to HDMI/DP muxes.

## Risks
The 24.576 MHz BCK limit rejects some high-rate/high-channel/high-width combinations. ETDM1_OUT only supports master mode unless it is a cowork slave. Cowork config can be invalid if DT points a slave to another slave; the code logs but does not fully unwind. DPTX and ETDM3_OUT share private state, so concurrent or conflicting HDMI/DP settings may collide. `mtk_dai_etdm_set_tdm_slot()` stores slot count but only LRCK width materially affects programming. Many regmap writes are unchecked. Input disabled-channel logic assumes paired channels and indexes `i + 1`; odd channel counts need careful validation.

## Test Signals
Signals include probe with all ETDM DAIs visible, DT parsing logs for invalid cowork/channel data, successful I2S/LJ/RJ/DSP_A/DSP_B format setup, master and slave clock polarity tests, always-on MCLK measurement, cowork master/slave simultaneous start and stop, capture with disabled input channels, HDMI and DP jack playback at 2/4/6/8 channels, DPTX register state matching sample format, and rejection of unsupported BCK rates.
