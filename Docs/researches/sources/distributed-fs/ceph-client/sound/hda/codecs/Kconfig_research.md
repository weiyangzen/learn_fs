# sources/distributed-fs/ceph-client/sound/hda/codecs/Kconfig

## Purpose

This Kconfig file defines selectable HD-audio codec driver symbols and sources vendor-specific codec subtrees under the `SND_HDA` dependency.

## Important APIs, types, and functions

Symbols include `SND_HDA_GENERIC_LEDS`, vendor codec tristates for Analog, Sigmatel/IDT, VIA, Conexant, Senarytech, Creative CA0110/CA0132, C-Media, CM9825, SI3054, and `SND_HDA_GENERIC`. `SND_HDA_CODEC_CA0132_DSP` enables firmware-backed DSP support. It sources Realtek, Cirrus, HDMI, and side-codec Kconfig files.

## Control flow

All options are inside `if SND_HDA`. Many vendor codecs `select SND_HDA_GENERIC`, and some select generic LED support. Comments warn users about built-in HDA with modular codec auto-loading. CA0132 DSP depends on the CA0132 codec and selects DSP loader plus firmware loader.

## State and persistence behavior

There is no runtime state. Configuration choices persist in `.config` and determine codec object inclusion and feature dependencies.

## Dependencies and integration points

This file integrates codec-specific drivers with the generic parser, LED class, firmware loader, and vendor subdirectories. Its symbols are consumed by `sound/hda/codecs/Makefile`.

## Risks and test signals

Risks include missing `select` dependencies, bad module/built-in combinations, and firmware dependency surprises. Test signals are config matrix builds for y/m combinations, auto-loading behavior with `SND_HDA=y`, and CA0132 DSP firmware path validation.
