# sources/distributed-fs/ceph-client/drivers/dma/stm32/Makefile

## Purpose
The STM32 DMA Makefile maps Kconfig symbols to object files for the STM32 DMA family drivers in this directory.

## Important APIs, Types, And Functions
The object rules are `obj-$(CONFIG_STM32_DMA) += stm32-dma.o`, `obj-$(CONFIG_STM32_DMAMUX) += stm32-dmamux.o`, `obj-$(CONFIG_STM32_MDMA) += stm32-mdma.o`, and `obj-$(CONFIG_STM32_DMA3) += stm32-dma3.o`. There are no functions or types.

## Control Flow
Kernel kbuild expands each `obj-$()` rule based on the resolved `.config`. Built-in symbols compile into the kernel image, tristate module values compile as modules when allowed by the corresponding Kconfig type, and disabled symbols omit the objects.

## State And Persistence
The Makefile has no runtime state. Its effect persists only through generated build artifacts.

## Dependencies And Integration Points
It integrates directly with `stm32/Kconfig` and the kernel build system. The object names correspond to platform drivers that register with DMAEngine and OF DMA routing at runtime.

## Risks
The main risk is drift between Kconfig symbols and object names. If a source file is renamed or a Kconfig symbol changes without updating this Makefile, the driver silently stops building for that configuration. Because `stm32-mdma.o` is listed but not part of this research subset, changes to Kconfig around MDMA should still consider that object.

## Test Signals
Build tests with each `CONFIG_STM32_*` symbol enabled should show the expected object compilation. `make drivers/dma/stm32/` under COMPILE_TEST is the direct smoke signal, with module installation checks for `STM32_DMA3=m`.
