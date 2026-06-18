# sources/distributed-fs/ceph-client/sound/soc/samsung/arndale.c

## Purpose
Machine driver for Arndale boards with either RT5631/ALC5631 or WM1811 codecs. It creates a simple single-link I2S card and applies codec-specific clock setup.

## Important APIs, Types, And Functions
- `arndale_rt5631_hw_params()` sets Samsung I2S CDCLK output, RCLK source, and RT5631 sysclk at `rate * 256`.
- `arndale_wm1811_hw_params()` chooses WM1811 MCLK1 rate based on width/rate and applies the `+1` clock rounding workaround.
- `arndale_put_of_nodes()` releases CPU and codec phandles in DAI links.
- `arndale_audio_probe()` selects a card from OF match data, parses `samsung,audio-cpu` and `samsung,audio-codec`, and registers it.

## Control Flow
OF compatible selects the RT5631 or WM1811 static card. Probe fills CPU/platform/codec OF nodes and registers the card. During `hw_params`, the selected ops configure CPU/codec clocks for the active sample rate and format.

## State And Persistence
The card and DAI links are static structures mutated with OF nodes at probe time. No runtime state beyond clock settings in CPU/codec drivers.

## Dependencies And Integration Points
Integrates with Samsung I2S (`SAMSUNG_I2S_*`) and either RT5631 or WM8994/WM1811 codec DAIs. Depends on DT properties `samsung,audio-cpu` and `samsung,audio-codec`.

## Risks And Edge Cases
- Static card mutation is not multi-instance safe.
- Clock setup is narrow and does not validate all possible rates/formats beyond codec/CPU return values.
- Node cleanup relies on remove/error paths; successful devm card registration keeps phandles until remove.

## Test Signals
Probe tests for all three compatibles, DT missing-phandle failures, playback with 16/24-bit rates, and remove/unbind phandle cleanup.
