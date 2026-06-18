# sources/distributed-fs/ceph-client/drivers/dma/hsu/Makefile

## Purpose
This Makefile maps HSU DMA Kconfig symbols to Kbuild objects.

## Important APIs, Types, And Functions
`hsu_dma.o` is built from `hsu.o` when `CONFIG_HSU_DMA` is enabled. `hsu_dma_pci.o` is built from `pci.o` when `CONFIG_HSU_DMA_PCI` is enabled.

## Control Flow
There is no runtime flow; Kbuild composes objects according to tristate values.

## State And Persistence Behavior
It controls built-in versus module artifacts and keeps the reusable core separate from PCI glue.

## Dependencies And Integration Points
It depends on `hsu/Kconfig` symbols and the exported core API consumed by `pci.c`.

## Risks And Test Signals
Object naming must stay aligned with module metadata. Build `drivers/dma/hsu/` for built-in and module configurations and inspect `modinfo` for the PCI module.
