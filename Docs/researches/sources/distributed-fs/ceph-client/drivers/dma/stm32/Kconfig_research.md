# sources/distributed-fs/ceph-client/drivers/dma/stm32/Kconfig

## Purpose
This Kconfig file exposes build-time configuration symbols for STM32 DMA controller drivers when `ARCH_STM32` or `COMPILE_TEST` is enabled. It controls inclusion of the classic STM32 DMA controller, STM32 DMAMUX router, STM32 MDMA controller, and STM32 DMA3 controller.

## Important APIs, Types, And Functions
The configuration symbols are `STM32_DMA`, `STM32_DMAMUX`, `STM32_MDMA`, and `STM32_DMA3`. `STM32_DMA`, `STM32_MDMA`, and `STM32_DMA3` select `DMA_ENGINE`; all except DMAMUX also select or rely on `DMA_VIRTUAL_CHANNELS`. `STM32_DMAMUX` depends on `STM32_DMA`, reflecting that the router is useful only with the classic STM32 DMA master in this directory. `STM32_MDMA` depends on `OF`. `STM32_DMA3` is tristate while the others are bool in this file.

## Control Flow
There is no runtime control flow. The build system evaluates the symbols and feeds the Makefile object selections. The top-level condition hides these options outside STM32 builds unless compile-testing is enabled.

## State And Persistence
Configuration state is stored in the kernel `.config` and influences compiled objects. There is no runtime state in this file.

## Dependencies And Integration Points
The file integrates with the kernel Kconfig system, the DMAEngine framework through selected symbols, and `drivers/dma/stm32/Makefile` through matching `CONFIG_STM32_*` object rules. It also controls whether device-tree compatible platform drivers for STM32 DMA variants can be built into or loaded by the kernel.

## Risks
Because `STM32_DMAMUX` depends specifically on `STM32_DMA`, configurations using DMA3 with a different routing model are not enabled by this symbol. The mix of bool and tristate options means DMA3 can be modular while classic STM32 DMA cannot from this Kconfig context. Missing dependency updates can surface as compile-test failures when headers or framework APIs change.

## Test Signals
Useful signals are `olddefconfig` coverage for STM32 and COMPILE_TEST builds, build tests for each symbol enabled independently where dependencies allow, and module/built-in link checks confirming that Makefile object selection matches the Kconfig symbols.
