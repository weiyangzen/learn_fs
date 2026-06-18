# sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hda.h

## Purpose

This header defines DAI IDs and private state used by the `hdac_hda.c` ASoC extension for legacy HDA codecs.

## Important APIs, types, and functions

The DAI ID enum covers analog, digital, alternate analog, four HDMI DAIs, and a count value. `struct hdac_hda_pcm` stores playback/capture stream tags and HDA format values. `struct hdac_hda_priv` stores the `hda_codec` pointer, per-DAI PCM state array, display-power requirement, and device index. The public API declaration is `snd_soc_hdac_hda_get_ops()`.

## Control flow

The header itself has no control flow. `hdac_hda.c` indexes `pcm[]` by DAI ID during set_stream, hw_params, prepare, and cleanup.

## State and persistence behavior

The structs define the persistent per-codec ASoC/HDA bridge state. Stream tags and format values are per direction and are updated as PCM streams are configured.

## Dependencies and integration points

It is private to the legacy HDA ASoC extension layer and requires HDA and HD-audio extended bus types to be visible through including files.

## Risks and test signals

Risks include enum order changes breaking DAI array indexing and `HDAC_DAI_ID_NUM` drifting from registered DAIs. Build and runtime tests should cover every DAI ID, both stream directions, and HDMI DAI indexing.
