# sources/distributed-fs/ceph-client/sound/pci/echoaudio/Makefile

## Purpose

This Makefile declares the ALSA Echoaudio PCI card modules and maps Kconfig symbols to object targets.

## Important APIs, types, and functions

It defines one `snd-*-y` composite object per supported card family member, including Darla20, Darla24, Echo3G, Gina, Layla, Mona, Mia, and Indigo variants. `obj-$(CONFIG_SND_...)` lines add enabled modules to the build.

## Control flow

Kernel kbuild evaluates each `CONFIG_SND_*` symbol and builds the matching single-object module. Each card `.c` file includes shared implementation files rather than linking separate shared objects.

## State and persistence behavior

The Makefile stores build-time module composition only; it has no runtime state.

## Dependencies and integration points

It integrates Echoaudio card drivers into the ALSA PCI sound build and depends on Kconfig symbols from the surrounding sound subsystem.

## Risks and test signals

Risks are missing object mappings, stale card names, or build symbol drift. Test signals are allmodconfig/build coverage and module presence for each selected `CONFIG_SND_*`.
