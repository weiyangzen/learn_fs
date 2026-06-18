# sources/distributed-fs/ceph-client/sound/firewire/oxfw/Makefile

## Purpose

This Makefile builds the OXFW970/971 ALSA FireWire driver object from its component sources and ties it to `CONFIG_SND_OXFW`.

## Important APIs, types, and functions

`snd-oxfw-y` lists the linked objects: command, stream, PCM, proc, MIDI, hwdep, speaker controls, SCS.1x support, and driver core. `obj-$(CONFIG_SND_OXFW) += snd-oxfw.o` exposes the final module/built-in object to Kbuild.

## Control flow

Kbuild evaluates the config symbol and either builds `snd-oxfw.o` from all listed objects or skips it. Link order places the core object last but all entries are part of one composite module.

## State and persistence behavior

The file has no runtime state. Its persistent effect is build graph membership.

## Dependencies and integration points

It integrates with the parent sound/firewire Kbuild and the `SND_OXFW` Kconfig option defined elsewhere.

## Risks and test signals

Risks are missing new source files from the object list or stale object names after refactors. Test signals are `make M=sound/firewire/oxfw`, full kernel builds with `SND_OXFW=m/y`, and module symbol resolution.
