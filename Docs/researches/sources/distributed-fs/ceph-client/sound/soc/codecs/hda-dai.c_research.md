# sources/distributed-fs/ceph-client/sound/soc/codecs/hda-dai.c

## Purpose

This file provides common ASoC DAI operations for HDA codecs whose PCM streams are represented as ASoC DAIs. It translates ALSA SoC stream callbacks into legacy HDA codec PCM operations.

## Important APIs, types, and functions

The exported object is `snd_soc_hda_codec_dai_ops`. Its callbacks are `hda_codec_dai_startup()`, `hda_codec_dai_shutdown()`, `hda_codec_dai_hw_free()`, and `hda_codec_dai_prepare()`. These use `struct hda_codec`, `struct hda_pcm`, `struct hda_pcm_stream`, and `struct hdac_stream`.

## Control flow

Startup retrieves the HDA codec from the DAI device, gets the stream info from DAI DMA data, derives the owning `hda_pcm`, increments the PCM reference, and calls the HDA stream `open` op. Shutdown calls the stream `close` op and drops the PCM reference. Prepare converts runtime format/channel/rate into an HDA stream format using the maximum bits per sample, then calls `snd_hda_codec_prepare()` with the stream tag from the HD-audio stream. Hw-free calls `snd_hda_codec_cleanup()`.

## State and persistence behavior

The file does not own persistent state; it operates on HDA codec/PCM objects created elsewhere. It temporarily increments HDA PCM usage between startup and shutdown and relies on DAI DMA data to point at stable stream descriptors.

## Dependencies and integration points

It depends on ASoC DAI callbacks, HDA codec helpers, and `hda.h`. `hda.c` assigns these ops to DAIs that it creates from the legacy HDA codec PCM list.

## Risks and test signals

Risks include invalid DAI DMA data, missing stream ops, mismatched stream tags in runtime private data, and prepare format mismatches for unusual subformats or maxbps. Test open/close reference balancing, prepare/hw_free sequencing, playback and capture streams, and error paths from legacy HDA stream ops.
