# sources/distributed-fs/ceph-client/sound/hda/codecs/Makefile

## Purpose

This Makefile maps HDA codec Kconfig symbols to codec driver objects and descends into vendor subdirectories.

## Important APIs, types, and functions

`subdir-ccflags-y` adds the common include path. `snd-hda-codec-*-y` variables map composite module names to source objects such as `generic.o`, `cmedia.o`, `analog.o`, `ca0132.o`, `conexant.o`, and `sigmatel.o`. `obj-y` descends into `cirrus/`, `hdmi/`, `realtek/`, and `side-codecs/`; `obj-$(CONFIG_...)` gates each top-level codec object.

## Control flow

Kbuild applies the include flag to this subtree, descends into vendor folders, and builds each codec module when its config symbol is enabled. Composite object variables support module names that differ from source filenames.

## State and persistence behavior

No runtime state exists. The file persists build graph and object naming.

## Dependencies and integration points

It depends on symbols from `codecs/Kconfig` and headers under `../common`. It integrates top-level codecs with vendor-specific subtrees and the parent HDA Makefile ordering.

## Risks and test signals

Risks include object-name mismatches, missing include paths, and Kconfig/Makefile symbol drift. Test signals are per-codec module builds, allmodconfig, allyesconfig, and vendor subtree builds.
