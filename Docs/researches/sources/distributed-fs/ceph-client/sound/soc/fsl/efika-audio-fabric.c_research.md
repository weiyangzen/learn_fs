# sources/distributed-fs/ceph-client/sound/soc/fsl/efika-audio-fabric.c

## Purpose
`efika-audio-fabric.c` is a legacy ASoC machine driver for the bplan Efika PowerPC platform using MPC5200 PSC AC97 interfaces and an STAC9766 codec. It creates an ASoC card with separate analog and IEC958 AC97 links.

## Important APIs, Types, And Functions
The file defines two `SND_SOC_DAILINK_DEFS()` blocks for `analog` and `iec958`, a two-entry `efika_fabric_dai[]` array, and a static `snd_soc_card` named `Efika`. The only runtime entry point is `efika_fabric_init()`, registered with `module_init()`.

## Control Flow
At module init, the driver checks `of_machine_is_compatible("bplan,efika")`. Non-Efika systems return `-ENODEV`. On Efika, it allocates a `soc-audio` platform device, stores the static card as driver data, and adds the platform device. The generic soc-audio machinery then consumes the card and its DAI links.

## State And Persistence
State is mostly static: the card and DAI link definitions are global. The allocated platform device persists after successful module init; there is no explicit module exit or device unregister path in this file.

## Dependencies And Integration Points
It depends on OF machine compatibility, platform device APIs, ASoC card/link definitions, MPC5200 PSC AC97 CPU DAIs (`mpc5200-psc-ac97.0` and `.1`), STAC9766 codec DAIs, and `mpc5200-pcm-audio` platform DMA.

## Risks And Edge Cases
The file uses static card/link data and a legacy `soc-audio` platform-device registration style. There is no cleanup function after successful init, which is acceptable for old built-in board support but less flexible for unload scenarios. Hard-coded component names must match the PSC, codec, and platform drivers exactly.

## Test Signals
Test that non-Efika machines skip cleanly, Efika creates the `soc-audio` device, both analog and IEC958 links bind to expected CPU/codec/platform components, and failure paths from allocation/addition release the platform device. Build tests should include `SND_MPC52xx_SOC_EFIKA`.
