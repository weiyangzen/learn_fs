# sources/distributed-fs/ceph-client/sound/soc/samsung/littlemill.c

## Purpose
Machine driver for Wolfson Littlemill boards with Samsung I2S, WM8994, and WM1250 baseband. It manages WM8994 FLLs, DAPM pins/routes, baseband clock supply, and headset jack detection.

## Important APIs, Types, And Functions
- `littlemill_set_bias_level()` and `_post()` start/stop WM8994 FLL1 around codec bias transitions.
- `littlemill_hw_params()` updates global `sample_rate` and programs FLL1/SYSCLK.
- `bbclk_ev()` starts/stops WM8994 FLL2 for the baseband AIF2 clock.
- `littlemill_late_probe()` initializes AIF1/AIF2 sysclks and registers headset jack detection through WM8958/WM8994 helpers.

## Control Flow
Probe registers a static card with CPU and baseband DAI links. During normal audio `hw_params`, FLL1 is set from 32.768 kHz MCLK2 to `sample_rate * 512`. DAPM bias prepare can start FLL1 if no stream did. Bias standby switches back to MCLK2 and stops FLL1. The baseband clock DAPM supply starts/stops FLL2. Late probe configures initial MCLK2 clocks and jack detection.

## State And Persistence
`sample_rate` is a file-static global used for bias-level FLL setup. Codec FLL/sysclk and jack status persist in hardware/ASoC runtime state. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S platform names, WM8994 codec APIs, WM1250 EV1, DAPM, and codec mic-detect helpers.

## Risks And Edge Cases
- Global `sample_rate` is not multi-card safe and defaults to 44.1 kHz.
- Bias-level FLL setup may race conceptually with stream-specific rates if multiple rates are used.
- DAPM widget `"Headset Mic"` is declared as `SND_SOC_DAPM_HP`, which looks semantically odd.

## Test Signals
Playback at multiple rates, DAPM bias transitions without active stream, baseband DAPM clock supply activation, headset detection, and register traces for FLL1/FLL2 start/stop.
