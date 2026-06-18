# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-dmic.c

Purpose: Implements the MT8188 digital microphone backend DAI. It supports 1 to 8 channel capture across four DMIC controller blocks, loads fixed IIR coefficients, configures source selection and rate modes, controls DMIC clocks and FIFO reset, and exposes hardware gain controls for four DMIC gain engines.

Important APIs and functions: `mt8188_dai_dmic_register()` registers the DAI, DAPM widgets/routes, and mixer controls. `mtk_dai_dmic_hw_params()` validates channel count, programs DMIC source array selection, loads IIR coefficients, chooses voice mode by rate, writes controller registers for the needed DMIC blocks, and caches channel count plus hires requirement. `mtk_dmic_event()` handles DAPM sequencing for FIFO soft reset, source enable, IIR/SDM bits, normal/hires clocks, and power-down delay. `mtk_dmic_gain_event()` enables or bypasses hardware gain based on cached mixer settings. `mtk_dai_dmic_hw_gain_ctrl_get/put()` implements four enum controls.

Control flow: Registration allocates one `mtk_dai_dmic_priv` at `dai_priv[DMIC_IN]`. HW params maps channels to the highest required DMIC block (`DMIC0` for one channel through `DMIC3` for four or more) and applies the same mode bits to all required blocks. DAPM `DMIC_CK_ON` asserts FIFO soft reset before PMU, enables UL source and clocks after PMU, clears setup bits before PMD, and disables clocks after PMD. `DMIC_GAIN_ON` enables or bypasses each gain engine before/after the path.

State and persistence: `mtk_dai_dmic_priv` stores per-DMIC gain enable flags, active channel count, and whether hires clocks are needed. Hardware state persists in DMIC controller, gain, IIR coefficient, and PWR2 top registers.

Dependencies and integration: Uses regmap, ASoC controls/DAPM, PCM params, and clock helpers. Routes expose capture data through `I004` to `I011` into the wider AFE interconnect. Clock IDs come from `mt8188-afe-clk.h`.

Risks: `mtk_dmic_event()` returns `-EINVAL` if DAPM powers before `hw_params` has set channels, so route activation order matters. For channels above four, `mtk_dmic_channels_to_dmic_number()` still selects all four DMIC blocks; channel-to-block semantics depend on hardware pairing. Unsupported rates fall back to 48 kHz register mode despite the DAI rate mask limiting public rates. Hires clock enable calls ignore return values. Gain control identity is string-matched by control name.

Test signals: Capture with 1, 2, 4, and 8 channels should verify correct DMIC block enables and FIFO reset release. 96 kHz capture should enable hires DMIC clocks; 8/16/32/48 kHz should not. Mixer tests should toggle each `DMIC*_HW_GAIN_EN` and gain target/current/step controls. Power-cycle tests should check no clock imbalance warnings.
