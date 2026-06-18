# sources/distributed-fs/ceph-client/sound/soc/kirkwood/armada-370-db.c

## Purpose
Implements the Armada 370 Development Board ASoC machine driver, connecting the MVEBU audio controller to a CS42L51 analog codec plus SPDIF input/output codec endpoints.

## Important APIs, Types, And Functions
`a370db_hw_params()` sets the CS42L51 sysclk based on sample rate. Static DAI links define `analog`, `spdif_out`, and `spdif_in`; DAPM widgets/routes expose output and input jacks. `a370db_probe()` resolves DT phandles `marvell,audio-controller` and `marvell,audio-codec` and registers the `snd_soc_card`.

## Control Flow, State, And Persistence
The static card and DAI-link arrays are patched at probe time with OF nodes. The analog link applies `a370db_ops`; SPDIF links are direct. There is no dynamic state beyond the registered card.

## Dependencies And Integration Points
Depends on DT compatible `marvell,a370db-audio`, CS42L51 codec DAI `cs42l51-hifi`, generic SPDIF DIT/DIR DAIs, and the Kirkwood controller DAIs named `i2s` and `spdif`.

## Risks And Test Signals
Risks include duplicated `AIN1L` route that may be intended as left/right input, phandle ordering assumptions for three codecs, and fixed sysclk mapping only for 44.1/48/96 kHz families. Test signals are card registration, DAPM route visibility, analog playback/capture, SPDIF in/out, and codec sysclk programming on each supported rate.
