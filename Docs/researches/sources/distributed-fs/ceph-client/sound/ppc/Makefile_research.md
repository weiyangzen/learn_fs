# sources/distributed-fs/ceph-client/sound/ppc/Makefile

## Purpose

This Makefile links ALSA PowerPC sound modules for PowerMac and PS3 hardware.

## Important APIs, types, and functions

It builds `snd-powermac` from `powermac.o`, `pmac.o`, `awacs.o`, `burgundy.o`, `daca.o`, `tumbler.o`, `keywest.o`, and `beep.o`. It builds `snd_ps3.o` directly for `CONFIG_SND_PS3`.

## Control flow

Kbuild includes each module according to `CONFIG_SND_POWERMAC` and `CONFIG_SND_PS3`.

## State and persistence behavior

No runtime state exists. Object membership is build metadata and determines which codec-specific functions are available to the PowerMac probe switch.

## Dependencies and integration points

The PowerMac link unit requires all codec/mixer helpers because `powermac.c` may select AWACS, Burgundy, DACA, Tumbler, or Snapper at runtime. PS3 is independent.

## Risks and test signals

Risks are missing object dependencies or dead declarations when Kconfig changes. Build module and built-in configurations and confirm symbols such as `snd_pmac_awacs_init`, `snd_pmac_keywest_init`, and PS3 module init resolve.
