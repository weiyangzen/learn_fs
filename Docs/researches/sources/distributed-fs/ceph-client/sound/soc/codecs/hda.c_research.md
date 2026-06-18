# sources/distributed-fs/ceph-client/sound/soc/codecs/hda.c

## Purpose

This file bridges legacy HD-audio codec drivers into ASoC component and DAI registration. It creates DAIs dynamically from the HDA codec PCM list, handles codec probe/complete/remove sequencing, manages HD-audio link and display power, and exports `soc_hda_ext_bus_ops` for HD-audio extended bus attach/detach.

## Important APIs, types, and functions

Key functions are `hda_codec_create_dais()`, `hda_codec_register_dais()`, `hda_codec_unregister_dais()`, `hda_codec_probe_complete()`, `hda_codec_probe()`, `hda_codec_remove()`, `hda_hdev_attach()`, and `hda_hdev_detach()`. The exported bus ops are `soc_hda_ext_bus_ops`. The file uses common DAI ops from `snd_soc_hda_codec_dai_ops`.

## Control flow

When an HDA device attaches, display codecs without an audio component are skipped. Otherwise the code allocates an ASoC component driver named after the HDA device and registers a placeholder binder DAI. Component probe obtains the HD-audio link, gets runtime PM on the bus, powers display codecs if needed, creates the HDA codec device, sets the codec name, initializes regmap, calls the legacy codec driver probe, parses HDA PCMs, and registers one ASoC DAI per HDA PCM. Non-display codecs immediately build controls and register through `hda_codec_probe_complete()`. Remove forbids runtime PM, unregisters DAIs and DAPM widgets, calls legacy remove, cleans up HDA codec state, drops display power/link references, and balances bus PM if probe never completed.

## State and persistence behavior

DAI definitions and stream names are devm-allocated from the HDA device. The codec's PCM list and registered flag determine remove behavior. Runtime PM state is carefully expected to enter and leave with device usage count 1 and suspended status. `codec->core.lazy_cache` is enabled after successful probe.

## Dependencies and integration points

It depends on ALSA SoC, HDA codec core, HDA extended bus links, runtime PM, and optional HDA i915 display power. It is used by bus drivers that call `soc_hda_ext_bus_ops` during codec enumeration.

## Risks and test signals

Risks include PM reference imbalance on probe failures, stale DAPM widgets when DAI registration partially fails, display-power handling without i915, dynamic DAI count mismatches with PCM list changes, and assumptions about initial runtime PM state. Test analog and display codecs, early failures at each probe stage, dynamic PCM lists with capture-only/playback-only streams, remove after incomplete probe, runtime suspend, and jackpoll cancellation on detach.
