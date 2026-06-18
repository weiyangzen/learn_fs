# sources/distributed-fs/ceph-client/sound/firewire/tascam/Makefile

## Purpose

This Makefile builds the TASCAM FireWire ALSA driver composite object and gates it behind `CONFIG_SND_FIREWIRE_TASCAM`.

## Important APIs, types, and functions

`snd-firewire-tascam-y` lists proc, AMDTP protocol, stream, PCM, hwdep, transaction, MIDI, and core driver objects. `obj-$(CONFIG_SND_FIREWIRE_TASCAM) += snd-firewire-tascam.o` connects the composite object to Kbuild.

## Control flow

Kbuild includes all component objects when the config symbol is enabled as built-in or module. The listed object order forms one linked module.

## State and persistence behavior

No runtime state exists here; the file persists build topology.

## Dependencies and integration points

It integrates with the parent FireWire sound Makefile and TASCAM Kconfig symbol.

## Risks and test signals

Risks are stale object names and missing new sources. Test signals are module and built-in builds with `SND_FIREWIRE_TASCAM` enabled.
