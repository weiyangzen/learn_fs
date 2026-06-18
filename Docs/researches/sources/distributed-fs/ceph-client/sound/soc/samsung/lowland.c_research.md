# sources/distributed-fs/ceph-client/sound/soc/samsung/lowland.c

## Purpose
Machine driver for Wolfson Lowland boards using Samsung I2S, WM5100, WM1250 baseband, and WM9081 sub speaker codec.

## Important APIs, Types, And Functions
- `lowland_wm5100_init()` sets WM5100 SYSCLK from MCLK1, configures OPCLK output, creates headset jack pins, and starts WM5100 detection.
- `lowland_wm9081_init()` disables `LINEOUT` DAPM pin and sets WM9081 MCLK.
- Static DAI links define CPU, baseband, and sub speaker paths; `sub_params` fixes sub speaker to 44.1 kHz S32 stereo.

## Control Flow
Probe registers the static card. Link init for the main codec sets clocks and jack detection. Link init for the sub speaker configures its clock and disables a DAPM pin. ASoC then manages the three DAI links and DAPM routes.

## State And Persistence
Static card/link/jack objects hold runtime state. Codec clocks and jack state persist in ASoC/hardware state. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S named platform, WM5100 codec, WM9081 codec, WM1250 EV1, DAPM, jack APIs, and codec-conf prefixing for the sub codec.

## Risks And Edge Cases
- Static structures are not multi-instance safe.
- Clock rates are hard-coded to 44.1 kHz-derived values.
- Minimal error handling beyond link init return codes.

## Test Signals
Probe/register card, WM5100 jack detection, main/baseband/sub link activation, and DAPM route validation for main speaker/sub codec.
