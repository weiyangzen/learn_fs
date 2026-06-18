# sources/distributed-fs/ceph-client/sound/soc/ux500/Makefile

## Purpose
Build manifest for Ux500 ASoC objects. It groups the MSP DAI/I2S low-level driver, DMA PCM platform, and MOP500 machine driver into config-controlled modules.

## Important APIs, Types, and Functions
Defines composite objects `snd-soc-ux500-plat-msp-i2s-y`, `snd-soc-ux500-plat-dma-y`, and `snd-soc-ux500-mach-mop500-y`, then wires them to `CONFIG_SND_SOC_UX500_PLAT_MSP_I2S`, `CONFIG_SND_SOC_UX500_PLAT_DMA`, and `CONFIG_SND_SOC_UX500_MACH_MOP500`.

## Control Flow, State, and Persistence
No runtime behavior. Build composition determines link boundaries: `ux500_msp_dai.o` and `ux500_msp_i2s.o` share one module, `ux500_pcm.o` is the DMA platform module, and `mop500.o` plus `mop500_ab8500.o` form the machine module.

## Dependencies and Integration Points
Integrates with Kbuild and the Kconfig symbols in the same directory. The object grouping matters because the DAI file calls low-level MSP functions and the machine file calls AB8500 board helpers.

## Risks and Test Signals
Risks are missing object linkage if config symbols are changed or helper exports are removed. Test signals are `make M=sound/soc/ux500`, module alias generation, and no unresolved references among MOP500, MSP, and PCM objects.
