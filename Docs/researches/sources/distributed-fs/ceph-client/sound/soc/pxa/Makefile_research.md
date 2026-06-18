# sources/distributed-fs/ceph-client/sound/soc/pxa/Makefile

Purpose: maps PXA/MMP ASoC Kconfig symbols to object files.

Important APIs/types/functions: builds `pxa2xx-pcm.o`, `pxa2xx-ac97.o`, `pxa2xx-i2s.o`, `pxa-ssp.o`, `mmp-sspa.o`, and Spitz machine object according to config symbols.

Control flow: object lists are included in the kernel build based on selected symbols.

State and persistence: build system state only.

Dependencies and integration: aligned with PXA Kconfig and exported PXA2xx PCM library functions used by AC97/I2S/SSP components.

Risks: missing object inclusion causes unresolved symbols for machine drivers or absent DAIs. Built-in/module combinations need symbol exports from shared libraries.

Test signals: module and built-in builds for each symbol combination, especially Spitz selecting I2S and AC97 selecting PXA library support.
