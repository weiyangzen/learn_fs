# sources/distributed-fs/ceph-client/sound/hda/common/Makefile

## Purpose
This Makefile builds the common ALSA HDA codec support object `snd-hda-codec.o`. It lists the core object members used by legacy HDA codec drivers and conditionally adds optional proc, hwdep, and beep support based on configuration.

## Important APIs, Types, And Functions
The key build variables are `snd-hda-codec-y`, `snd-hda-codec-$(CONFIG_SND_PROC_FS)`, `snd-hda-codec-$(CONFIG_SND_HDA_HWDEP)`, `snd-hda-codec-$(CONFIG_SND_HDA_INPUT_BEEP)`, `CFLAGS_controller.o`, and `obj-$(CONFIG_SND_HDA)`. The always-built members are `bind.o`, `codec.o`, `jack.o`, `auto_parser.o`, `sysfs.o`, and `controller.o`.

## Control Flow
When `CONFIG_SND_HDA` is enabled, Kbuild emits `snd-hda-codec.o` from the object list. Optional objects are appended if their config symbols are enabled. `CFLAGS_controller.o := -I$(src)` adds the local source directory to controller compilation so tracepoint headers or local includes resolve correctly.

## State And Persistence
The Makefile does not hold runtime state. Its persistent effect is the composition of the built kernel object/module. Optional compilation determines whether symbols such as beep helpers, hwdep interfaces, and proc hooks are available to codec drivers and runtime users.

## Dependencies And Integration Points
This file integrates directly with `common/Kconfig`. It provides common symbols consumed by codec drivers in `sound/hda/codecs`, by controller code, and by the HDA bus binding path. Conditional entries must stay consistent with `#ifdef CONFIG_SND_HDA_INPUT_BEEP`, `CONFIG_SND_PROC_FS`, and `CONFIG_SND_HDA_HWDEP` guards in C sources.

## Risks
Missing an object here can create unresolved symbols or silently remove runtime features. Adding objects without matching Kconfig guards can break slim builds. Include-path changes for `controller.o` can affect tracepoint compilation.

## Test Signals
Build tests should verify that `snd-hda-codec.o` contains expected objects under several config combinations. Link-time success for codec modules, availability of proc/hwdep/beep symbols only when configured, and successful `modpost` are the main signals.
