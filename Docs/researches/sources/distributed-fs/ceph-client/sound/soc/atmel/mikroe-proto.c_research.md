# sources/distributed-fs/ceph-client/sound/soc/atmel/mikroe-proto.c

## Purpose
Device-tree machine driver for the MikroElektronika PROTO AudioCODEC board using a WM8731 codec. It creates a single DAI link between a DT-specified I2S controller and codec, sets WM8731 sysclk to the fixed 12.288 MHz crystal, and declares basic headphone/microphone DAPM routing.

## Important APIs, Types, And Functions
- `snd_proto_init()` calls `snd_soc_dai_set_sysclk()` for `WM8731_SYSCLK_XTAL`.
- Static `snd_soc_card snd_proto` carries widgets/routes and receives a dynamic DAI link at probe.
- `snd_proto_probe()` parses `model`, `audio-codec`, `i2s-controller`, audio format, and clock-provider information.

## Control Flow
Probe requires an OF node, allocates one DAI link plus three components, binds codec/cpu/platform OF nodes, enforces the same bit-clock and frame-clock master phandle, computes `dai_fmt`, registers the card with devm cleanup, and releases OF references on all paths.

## State And Persistence
The global card object is populated at probe with a dynamically allocated single link. There is no persistent state beyond the card registration.

## Dependencies And Integration Points
Integrates WM8731 codec DAI `wm8731-hifi`, an arbitrary DT I2S controller, ASoC card parsing helpers, and DAPM. Compatible string is `mikroe,mikroe-proto`.

## Risks
Because `snd_proto` is static, multiple device instances would share card fields. Clock-provider parsing rejects split bit/frame masters. Missing DT phandles fail probe. The sysclk is fixed to board hardware and not negotiable.

## Test Signals
DT probe with valid and missing phandles, clock-provider mode variants, card name parsing, and `aplay`/`arecord` through WM8731 with expected DAPM pins.
