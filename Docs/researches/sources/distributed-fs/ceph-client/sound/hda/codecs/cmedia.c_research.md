# sources/distributed-fs/ceph-client/sound/hda/codecs/cmedia.c

## Purpose

This is the generic C-Media HDA codec driver for CMI8888 and CMI9880-family codecs. Most behavior is delegated to the ALSA HDA generic parser, with one CMI8888-specific headphone amplifier control.

## Important APIs, types, and functions

`cmedia_probe()` allocates `struct hda_gen_spec`, initializes generic parser state, parses BIOS pin defaults, runs generic auto-config, and optionally adds `Headphone Amp Playback Volume` for CMI8888 pin `0x10` when that pin is configured as headphone output. `cmedia_codec_ops` binds probe/remove/build/init/unsol/check-power/stream-PM operations to generic HDA helpers.

## Control flow

Probe detects CMI8888 by codec vendor ID, masks NID `0x10` out of generic output-volume selection so the boost amp is not folded into normal output volume, parses pin config, then adds the explicit amp control if the pin default indicates `AC_JACK_HP_OUT`. Errors call `snd_hda_gen_remove()` before returning.

## State and persistence behavior

State is the generic parser spec in `codec->spec`, plus `out_vol_mask` for CMI8888. Hardware persistence is limited to generic HDA control state and any mixer writes through the manually added headphone amp control.

## Dependencies and integration points

The driver uses ALSA HDA core, generic auto parser, HDA jack support, and module IDs `0x13f68888`, `0x13f69880`, and `0x434d4980`. It integrates almost entirely through generic build/init/PCM and jack-event handling.

## Risks and test signals

Risks include misdetecting the CMI8888 boost amp, duplicate or missing headphone volume controls, BIOS pin defaults that hide the intended HP amp, and generic-parser regressions affecting CMI9880. Test signals are mixer enumeration on CMI8888, headphone amp gain changes, generic playback/capture/jack behavior on CMI9880, and probe failure cleanup under injected allocation/control-add errors.
