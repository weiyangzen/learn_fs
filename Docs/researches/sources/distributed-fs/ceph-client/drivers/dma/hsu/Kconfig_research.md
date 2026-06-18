# sources/distributed-fs/ceph-client/drivers/dma/hsu/Kconfig

## Purpose
This fragment declares build symbols for Intel High Speed UART DMA.

## Important APIs, Types, And Functions
`CONFIG_HSU_DMA` is the tristate core symbol and selects `DMA_ENGINE` plus `DMA_VIRTUAL_CHANNELS`. `CONFIG_HSU_DMA_PCI` is PCI glue and depends on `HSU_DMA && PCI`.

## Control Flow
Kconfig resolution decides which objects are eligible to build; there is no runtime code.

## State And Persistence Behavior
The only persistent state is kernel configuration. Enabling PCI glue implies the core is available.

## Dependencies And Integration Points
It integrates with `hsu/Makefile`, dmaengine, virtual channels, and PCI configuration.

## Risks And Test Signals
The core symbol has no prompt here, so it must be selected or enabled through surrounding config. Validate built-in/module/disabled combinations and dependency enforcement.
