# sources/distributed-fs/ceph-client/sound/hda/codecs/realtek/Makefile

## Purpose

This Makefile maps Realtek HDA codec Kconfig symbols to kernel objects and declares the source object composition for each Realtek codec module.

## Important APIs, types, and functions

It adds `-I$(src)/../../common`, defines `snd-hda-codec-realtek-lib-y := realtek.o`, maps each codec module name to its source object, and uses `obj-$(CONFIG_...)` to include the library and per-codec modules.

## Control flow

Kbuild expands the `obj-*` assignments according to `.config`, producing built-in or loadable Realtek codec objects. The shared library object is built when `CONFIG_SND_HDA_CODEC_REALTEK_LIB` is enabled.

## State and persistence behavior

No runtime state exists. The file controls build artifacts and module composition.

## Dependencies and integration points

It is paired with `Kconfig` and the individual `alc*.c` sources. The include path lets Realtek sources use shared common codec headers.

## Risks and test signals

Risks include mismatched Kconfig/object names, missing new codec sources, and include path regressions. Test all Realtek codec configs as built-in and modules, clean incremental builds, and namespace imports in each generated module.
