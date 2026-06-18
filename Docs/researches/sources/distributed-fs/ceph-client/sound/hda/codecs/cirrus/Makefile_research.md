# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/Makefile

## Purpose

This Makefile maps the Cirrus Kconfig symbols to codec driver objects.

## Important APIs, types, and functions

`snd-hda-codec-cs420x-y`, `snd-hda-codec-cs421x-y`, and `snd-hda-codec-cs8409-y` define the object composition. CS8409 is built from both `cs8409.o` and `cs8409-tables.o`. `subdir-ccflags-y += -I$(src)/../../common` provides access to common HDA headers.

## Control flow

Kbuild appends `snd-hda-codec-cs420x.o`, `snd-hda-codec-cs421x.o`, or `snd-hda-codec-cs8409.o` to `obj-*` when the matching config symbol is enabled as built-in or module.

## State and persistence behavior

No runtime state exists. The persisted build result determines module names and linked objects. Splitting CS8409 tables into a second object means both files must remain in the same symbol namespace and module.

## Dependencies and integration points

The Makefile integrates with `Kconfig`, ALSA HDA codec infrastructure, and the common side-codec include path. CS8409 depends on symbols declared across `cs8409.h`, `cs8409.c`, and `cs8409-tables.c`.

## Risks and test signals

Risks include omitting table objects from CS8409, breaking include paths, or mismatching Kconfig symbol names. Test signals are `make M=sound/hda/codecs/cirrus`, full kernel builds for each symbol as `y` and `m`, and unresolved-symbol checks for `cs8409-tables.o` exports consumed by `cs8409.o`.
