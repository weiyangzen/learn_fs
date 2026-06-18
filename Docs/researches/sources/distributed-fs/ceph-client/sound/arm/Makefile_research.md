# sources/distributed-fs/ceph-client/sound/arm/Makefile

## Purpose
This Makefile maps ARM ALSA Kconfig symbols to build objects for the AACI driver and PXA2xx helper library.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SND_ARMAACI)` builds `snd-aaci.o` from `aaci.o`. `obj-$(CONFIG_SND_PXA2XX_LIB)` builds `snd-pxa2xx-lib.o` from `pxa2xx-pcm-lib.o`, and conditionally appends `pxa2xx-ac97-lib.o` when `CONFIG_SND_PXA2XX_LIB_AC97` is enabled.

## Control Flow
The build system includes object files according to Kconfig expansion. There is no runtime control flow.

## State And Persistence
No runtime state exists. The file controls persistent module composition at build time.

## Dependencies And Integration Points
It integrates `sound/arm` with kbuild and mirrors symbols declared in `Kconfig`. The PXA library composition is important because AC97 symbols are exported only when the AC97 helper object is included.

## Risks And Test Signals
Test signals are compile/link success for every enabled combination. A key risk is unresolved exported PXA AC97 symbols if external users select `SND_PXA2XX_LIB_AC97` inconsistently.
