# sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_wm8994pcm.c

## Purpose
SMDK PCM machine driver for WM8994 over the Samsung PCM controller. It supports an 8 kHz DSP_B PCM link and configures codec FLL/sysclk plus CPU PCM source clock/divider.

## Important APIs, Types, And Functions
- `smdk_wm8994_pcm_hw_params()` accepts only 8 kHz, sets WM8994 FLL1/SYSCLK to 512fs, sets CPU `S3C_PCM_CLKSRC_MUX`, and sets `S3C_PCM_SCLK_PER_FS`.
- Static DAI link connects `samsung-pcm.0` to `wm8994-aif1` with DSP_B, inverted bit clock, codec/provider clock flags.
- `snd_smdk_probe()` registers the static card.

## Control Flow
Probe assigns device and registers card. During hw_params, unsupported rates fail; 8 kHz configures codec and PCM controller clocks before stream start.

## State And Persistence
Static card/link data only. Codec and PCM clock settings persist in hardware until changed.

## Dependencies And Integration Points
Depends on Samsung PCM DAI constants from `pcm.h`, WM8994 codec APIs, and platform DAI names.

## Risks And Edge Cases
- Only 8 kHz is accepted.
- No DT parsing or dynamic routing.
- FLL is not explicitly stopped.

## Test Signals
8 kHz playback/capture setup, unsupported-rate rejection, CPU DAI clock/divider call success, and card registration.
