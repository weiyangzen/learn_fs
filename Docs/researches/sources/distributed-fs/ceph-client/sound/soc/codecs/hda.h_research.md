# sources/distributed-fs/ceph-client/sound/soc/codecs/hda.h

## Purpose

This header declares the common ASoC/HDA bridge symbols used by `hda.c` and `hda-dai.c` and provides a helper macro for identifying Intel display HDA codecs.

## Important APIs, types, and functions

`hda_codec_is_display(codec)` checks the high 16 bits of the codec vendor ID for Intel `0x8086`. The header declares `snd_soc_hda_codec_dai_ops`, `soc_hda_ext_bus_ops`, and `hda_codec_probe_complete()`.

## Control flow

There is no independent control flow. The macro gates display-power and DAPM behavior in `hda.c`; exported declarations connect the common DAI ops and bus ops across compilation units.

## State and persistence behavior

The header stores no state. It encodes a vendor-ID classification that affects persistent runtime PM and display power behavior in the C implementation.

## Dependencies and integration points

It is private to the HDA ASoC bridge and requires HDA codec and ASoC types to be visible from including files.

## Risks and test signals

Risks include treating all Intel-vendor codecs as display codecs and missing non-Intel display codecs if any exist. Build tests catch declaration drift; runtime tests should confirm analog and HDMI/display codecs follow the right probe paths.
