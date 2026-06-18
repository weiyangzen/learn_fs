# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/Kconfig

## Purpose

This Kconfig fragment exposes Cirrus Logic HDA codec support and its per-driver build switches. `SND_HDA_CODEC_CIRRUS` is the parent menu option; the CS420x, CS421x, and CS8409 drivers are selected beneath it.

## Important APIs, types, and functions

The important symbols are `SND_HDA_CODEC_CIRRUS`, `SND_HDA_CODEC_CS420X`, `SND_HDA_CODEC_CS421X`, and `SND_HDA_CODEC_CS8409`. CS420x and CS421x select `SND_HDA_GENERIC`; CS8409 selects both `SND_HDA_GENERIC` and `SND_HDA_SCODEC_COMPONENT` because it can bind side-codec amplifier components.

## Control flow

Kconfig control flow is declarative. Enabling the parent exposes the children. CS420x and CS421x default to `y` under the parent, while individual toggling is hidden unless `EXPERT` is set. CS8409 is explicit and remains separately selectable. The comments warn about module autoloading when the HDA core is built-in but a codec driver is modular.

## State and persistence behavior

There is no runtime state. The selected symbols persist in kernel configuration and control which object files are compiled or loadable. Misconfiguration can leave matching HDA codec IDs without a driver at runtime.

## Dependencies and integration points

This file integrates with the ALSA HDA codec build system and the Cirrus `Makefile`. Runtime integration is through the module aliases emitted by each compiled driver. The CS8409 dependency on `SND_HDA_SCODEC_COMPONENT` is an integration requirement for its component manager path.

## Risks and test signals

Risks include missing generic-parser support, forgetting the side-codec component selection for CS8409, and built-in HDA core plus modular codec autoload mismatches. Test signals are `olddefconfig` coverage, `modinfo` aliases for modular builds, boot probing on Cirrus hardware, and build matrix checks for built-in and module combinations.
