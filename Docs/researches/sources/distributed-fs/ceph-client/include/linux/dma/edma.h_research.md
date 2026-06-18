<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/edma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/edma.h

## Purpose
Declares the Synopsys DesignWare eDMA controller platform interface.

## Important APIs, Types, And Functions
Defines `EDMA_MAX_WR_CH`, `EDMA_MAX_RD_CH`, `struct dw_edma_region`, `struct dw_edma_plat_ops`, `enum dw_edma_map_format`, `enum dw_edma_chip_flags`, and `struct dw_edma_chip`. APIs are `dw_edma_probe()` and `dw_edma_remove()` with disabled stubs.

## Control Flow
Platform code describes register base, IRQ mapping, write/read linked-list regions, data regions, doorbell interrupt emulation, map format, and flags, then calls `dw_edma_probe()`. The core initializes DMAengine channels and stores private state in `chip->dw`.

## State And Persistence
State includes per-channel linked-list and data memory regions, IRQ vectors, register mapping format, local endpoint flag, non-linked-list config flag, and core private state. No persistence exists.

## Dependencies And Integration Points
Depends on devices, DMAengine, PCI address translation, and platform-specific IRQ/address ops. It integrates DW PCIe root/endpoint controllers with eDMA core code.

## Risks And Edge Cases
Write/read channel counts must not exceed eight. PCI address translation may be unnecessary or mandatory depending on iATU/DMA_BYPASS. Map-format mismatches can corrupt register access. Local endpoint flags affect address interpretation.

## Test Signals
Tests should cover each map format, IRQ-vector mapping, PCI address translation, channel-count boundaries, linked-list region setup, local endpoint mode, non-linked-list mode, and probe stubs when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/edma.h -->
