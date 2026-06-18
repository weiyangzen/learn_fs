# sources/distributed-fs/ceph-client/sound/pci/aw2/Makefile

## Purpose
Defines the kernel build objects for the Audiowerk2 ALSA driver.

## Important APIs, Types, And Functions
No code APIs. It sets `snd-aw2-y := aw2-alsa.o aw2-saa7146.o` and adds `snd-aw2.o` to `obj-$(CONFIG_SND_AW2)`.

## Control Flow
Kbuild compiles the ALSA module from the top-level ALSA wrapper and the SAA7146 helper when `CONFIG_SND_AW2` is enabled. `aw2-tsl.c` is not listed because it is included directly by `aw2-saa7146.c`.

## State And Persistence
No runtime state. Build configuration determines whether the module exists.

## Dependencies And Integration Points
Depends on the kernel ALSA PCI Kconfig selecting `CONFIG_SND_AW2` and on the two object files resolving each other's symbols.

## Risks
Because `aw2-tsl.c` is textually included, adding it to the object list would duplicate definitions. Missing either object would break module linkage.

## Test Signals
`make M=sound/pci/aw2` or full kernel builds with `CONFIG_SND_AW2=m/y` should produce `snd-aw2.o`/module without unresolved symbols.
