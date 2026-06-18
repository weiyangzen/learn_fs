# sources/distributed-fs/ceph-client/sound/pci/ac97/Makefile

## Purpose

This Makefile builds the ALSA AC97 codec support module used by many PCI audio and modem controllers.

## Important APIs, Types, and Functions

It composes `snd-ac97-codec.o` from `ac97_codec.o` and `ac97_pcm.o`, conditionally adding `ac97_proc.o` when `CONFIG_SND_PROC_FS` is enabled. It adds the module with `obj-$(CONFIG_SND_AC97_CODEC) += snd-ac97-codec.o`.

## Control Flow

When `CONFIG_SND_AC97_CODEC=y` or `m`, kbuild links the core codec and PCM helper objects, plus procfs diagnostics when configured. When disabled, no AC97 codec support object is emitted.

## State and Persistence

No runtime state is defined here. The Makefile controls object composition and optional procfs support.

## Dependencies and Integration Points

It is reached by `sound/pci/Makefile` and by controller Kconfig symbols that `select SND_AC97_CODEC`. Runtime APIs are exported from `ac97_codec.c` and companion objects to AC97 controller drivers.

## Risks and Edge Cases

Procfs support changes module contents and enables declarations in `ac97_local.h`; both sides must remain synchronized. Omitting `ac97_pcm.o` would break PCM setup consumers even if codec registration builds.

## Test Signals

Build `CONFIG_SND_AC97_CODEC=m/y` with `CONFIG_SND_PROC_FS=y/n`, and ensure dependent PCI AC97 controller modules link against exported codec symbols.
