# sources/distributed-fs/ceph-client/drivers/dma/hsu/hsu.h

## Purpose
`hsu.h` defines private registers, status/control bits, structures, and MMIO helpers for the Intel HSU DMA core.

## Important APIs, Types, And Functions
It defines channel status/control/descriptor registers, four descriptor start/size slots, `HSU_DMA_CHAN_NR_DESC`, `HSU_DMA_CHAN_LENGTH`, `hsu_dma_sg`, `hsu_dma_desc`, `hsu_dma_chan`, and `hsu_dma`. Inline helpers perform container conversion and per-channel MMIO.

## Control Flow
The header has no independent control flow. `hsu.c` uses it to program descriptors, read status, compute residue, and register channel objects.

## State And Persistence Behavior
It models volatile channel state and hardware status. Descriptor timeout, channel error, descriptor done, and current-descriptor bits are consumed by the core and PCI IRQ glue.

## Dependencies And Integration Points
It includes the public `linux/dma/hsu.h` chip interface and `virt-dma`, allowing PCI and other glue to call core helpers.

## Risks And Test Signals
Four-slot descriptor and 16-bit length limits shape all transfers. Validate register programming against SG entries, compile with `CONFIG_HSU_DMA`, and run UART DMA traffic.
