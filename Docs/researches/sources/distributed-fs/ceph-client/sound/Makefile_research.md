# sources/distributed-fs/ceph-client/sound/Makefile

## Purpose

This top-level sound Makefile wires configured sound subsystems into the kernel build, including soundcore, ALSA directories, Apple Onboard Audio, and both old and new AC97 bus implementations.

## Important APIs, types, and functions

The important Kbuild variables are `obj-$(CONFIG_SOUND)`, `obj-$(CONFIG_DMASOUND)`, `obj-$(CONFIG_SND)`, `obj-$(CONFIG_SND_AOA)`, `obj-$(CONFIG_AC97_BUS)`, `obj-$(CONFIG_AC97_BUS_NEW)`, and `soundcore-y`.

## Control Flow

Kbuild conditionals include directory subtrees or objects according to `.config`. `last.o` is added only when `CONFIG_SND=y`, preserving ALSA link ordering.

## State and Persistence

No runtime state exists. Build output depends on selected config symbols.

## Dependencies and Integration Points

It integrates Kconfig selections with directory recursion. It intentionally allows `ac97_bus.o` to build even when sound is otherwise disabled.

## Risks and Test Signals

Risks include link-order regressions, missing subdirectory inclusion for enabled drivers, and AC97 dependency mistakes. Build tests with sound disabled but AC97 enabled, ALSA built-in, ALSA modular, and AOA enabled are useful.
