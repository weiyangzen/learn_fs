# sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hda.c

## Purpose

This file provides an older ASoC extension layer that reuses legacy HDA codec drivers with ASoC platform drivers. It exposes fixed analog/digital/alternate-analog and HDMI DAI stubs, maps those DAIs to HDA PCMs by name, translates stream callbacks to HDA operations, handles optional patch firmware, and exports HD-audio extended bus ops.

## Important APIs, types, and functions

Important callbacks are `hdac_hda_dai_set_stream()`, `hdac_hda_dai_hw_params()`, `hdac_hda_dai_prepare()`, `hdac_hda_dai_open()`, and `hdac_hda_dai_close()`. `snd_soc_find_pcm_from_dai()` maps DAI IDs to HDA PCM names. Lifecycle functions are `hdac_hda_codec_probe()`, `hdac_hda_codec_remove()`, `hdac_hda_dev_probe()`, and `snd_soc_hdac_hda_get_ops()`. `loadable_patch[]` is a module parameter when patch loading is enabled.

## Control flow

Device probe gets the HD-audio link and registers either analog/digital DAIs or HDMI DAIs depending on `need_display_power`. Component probe obtains the link, powers display if required, creates the HDA codec device, optionally loads a patch firmware indexed by codec address, marks the device type as ASoC, keeps runtime PM active while initializing, sets codec name, initializes regmap, calls the legacy codec probe, parses PCMs, builds controls for non-HDMI codecs, enables lazy cache, drops display power, allows runtime PM, and suspends the codec. DAI open finds the matching HDA PCM, increments its reference, and calls the legacy stream open. Hw_params stores HDA format values, set_stream stores stream tags, prepare programs HDA stream/tag/format, close calls stream close and drops the PCM reference.

## State and persistence behavior

`struct hdac_hda_priv` persists the codec pointer, per-DAI stream tags and format values, display-power requirement, and device index. Runtime PM state is manipulated during component probe and remove. HDA PCM matching relies on stable PCM names such as `Analog`, `Digital`, `Alt Analog`, and `HDMI N`.

## Dependencies and integration points

It depends on HDA codec core, HDA extended bus, HDA i915 display power, optional HDA patch loader, ASoC component/DAI/DAPM, and `hdac_hda.h`. Platform drivers obtain the ops table through `snd_soc_hdac_hda_get_ops()`.

## Risks and test signals

Risks include name-based PCM mapping errors, missing `snd_hda_codec_pcm_put()` on open failure, PM/link reference imbalance on error paths, patch firmware lifetime issues when load fails, HDMI controls delegated to machine drivers, and fixed stub capabilities not matching actual converter caps. Test analog, digital, alternate analog, and HDMI DAIs; stream tag/format programming; patch-loader success/failure; runtime PM transitions; incomplete probe cleanup; and codec remove after open/close cycles.
