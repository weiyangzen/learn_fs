# sources/distributed-fs/ceph-client/sound/usb/hiface/Makefile

## Purpose
Builds the standalone M2Tech hiFace-compatible USB-SPDIF ALSA driver.

## Build Integration
`snd-usb-hiface-y := chip.o pcm.o` links the probe/card layer and PCM streaming layer into one module object. `obj-$(CONFIG_SND_USB_HIFACE) += snd-usb-hiface.o` includes it when the Kconfig symbol is enabled.

## Dependencies and Risks
The Makefile assumes `chip.c` and `pcm.c` jointly provide all module entry points. Risks are straightforward build drift if a new source file is added but not listed, or if `CONFIG_SND_USB_HIFACE` is renamed.

## Test Signals
Kernel build with `CONFIG_SND_USB_HIFACE=m` or `y` confirms object composition; module load/probe tests confirm runtime linkage.
