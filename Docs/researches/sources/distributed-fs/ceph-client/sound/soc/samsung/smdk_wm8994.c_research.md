# sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_wm8994.c

## Purpose
SMDK I2S machine driver for WM8994. It defines primary I2S and secondary FIFO playback links, programs WM8994 FLL1 based on stream parameters, disables unused codec pins, and supports optional DT CPU phandle parsing.

## Important APIs, Types, And Functions
- `smdk_hw_params()` calculates WM8994 FLL output based on width/rate and sets FLL1/SYSCLK.
- `smdk_wm8994_init_paiftx()` disables unused DAPM pins.
- Static DAI links bind `samsung-i2s.0` and `samsung-i2s-sec` to `wm8994-aif1`.
- `smdk_audio_probe()` optionally replaces CPU/platform names with `samsung,i2s-controller` OF node and registers the card.

## Control Flow
Probe sets card device, updates the primary link for DT if present, then registers the static card. Link init disables not-connected codec pins. `hw_params` starts FLL1 for both primary and secondary links.

## State And Persistence
Static card/link structures are mutated for DT. Codec FLL/SYSCLK settings persist until changed by codec/card lifecycle. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S primary and secondary DAI names, WM8994 codec, DAPM, and optional DT property `samsung,i2s-controller`.

## Risks And Edge Cases
- DT parsing updates only the first DAI link, leaving secondary link name-based.
- Static card mutation is not multi-instance safe.
- FLL is not explicitly stopped in this machine driver.

## Test Signals
Probe with platform-name and DT modes, primary and secondary playback, DAPM disabled-pin verification, and FLL rate setup for 8/11.025/24-bit cases.
