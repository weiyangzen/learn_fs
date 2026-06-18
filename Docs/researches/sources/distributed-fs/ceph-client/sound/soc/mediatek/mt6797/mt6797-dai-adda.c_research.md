# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-dai-adda.c

## Purpose

This file implements the MT6797 analog/digital audio ADDA DAI, including DAPM mixers, ADDA power supplies, clock supplies, sample-rate-specific playback/capture register programming, and registration into the platform sub-DAI list.

## Important APIs, Types, and Functions

- DAPM mixer controls select DL and capture sources into `ADDA_DL_CH1/CH2`.
- Supplies control `ADDA Enable`, playback/capture source enable bits, DAC/ADC clocks, and `mtkaif_26m_clk`.
- `mtk_adda_ul_event()` delays after capture power-down to satisfy a 1/fs settling requirement.
- `mtk_dai_adda_hw_params()` programs playback predistortion, DL SRC mode/gain, voice mode, and capture UL source/new-interface settings.
- `mt6797_dai_adda_register()` adds the ADDA DAI, widgets, and routes to `afe->sub_dais`.

## Control Flow

During platform probe, registration appends one sub-DAI. At stream `hw_params`, playback clears predistortion, maps rate through common ADDA helpers, selects upsampling mode, enables gain, and writes DL source registers. Capture selects internal ADC, maps rate to UL voice mode, configures new-interface registers, handles hires versus normal mode, and writes UL source config. DAPM turns supply bits on/off around active routes and delays after capture power down.

## State and Persistence Behavior

No private state is allocated. Hardware register state persists until DAPM or runtime PM changes it. Routes and widgets are static and combined into the platform component.

## Dependencies and Integration Points

Depends on `mtk-dai-adda-common.h` for rate transforms, MT6797 register/interconnection macros, regmap, and ASoC DAPM. It connects memif DL/UL streams, PCM modem DAIs, and hostless routes through ADDA endpoints.

## Risks and Edge Cases

Capture code writes `AFE_ADDA_NEWIF_CFG2` with rate-specific hires mode, then unconditionally overwrites the same field with `8 << 28`, which may defeat hires configuration. Playback gain constants are hardware-tuned magic values. DAPM route bit errors can silently connect wrong channels.

## Test Signals

Playback/capture at 8/16/32/48/96/192 kHz, DAPM power sequencing, regmap checks for DL/UL source registers, and analog loopback/hostless paths validate behavior.
