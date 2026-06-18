# sources/distributed-fs/ceph-client/sound/soc/atmel/Makefile

## Purpose
This Kbuild file maps Atmel/Microchip ASoC Kconfig symbols to platform, PCM, and machine-driver objects.

## Important APIs, Types, And Functions
It defines object groups for PDC PCM, DMA PCM, SSC DAI, Atmel I2S, Microchip I2S MCC/SPDIF/PDMC, and machine drivers such as WM8904, CLASSD, PDMIC, TSE850, and Mikroe PROTO. Conditional `ifdef CONFIG_SND_ATMEL_SOC_PDC/DMA` ensures SSC users get built-in-compatible PCM support.

## Control Flow
Build-time only. `obj-$(CONFIG_...)` lines include drivers according to selected symbols.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It depends on the Kconfig fragment and source object names in the folder. The PDC/DMA built-in handling is an integration point for SSC users because SSC can select both transports but choose one at runtime from `ssc->pdata->use_dma`.

## Risks And Test Signals
Risk is build/link failure if Kconfig enables an object without its transport dependencies. Test signals include Atmel/Microchip `allyesconfig` and mixed built-in/module builds for SSC PDC and DMA variants.
