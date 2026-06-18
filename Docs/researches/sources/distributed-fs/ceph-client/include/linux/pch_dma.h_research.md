# Research: sources/distributed-fs/ceph-client/include/linux/pch_dma.h

Purpose: `pch_dma.h` declares Intel PCH DMA slave configuration used by platform drivers binding to the DMAengine subsystem.

Important APIs/types/functions: `enum pch_dma_width` defines 1, 2, and 4 byte transfer widths. `struct pch_dma_slave` carries the DMA controller device, channel ID, TX/RX register DMA addresses, and transfer width.

Control flow and state: clients provide this static configuration to DMAengine filter/probe paths so the DMA controller can select a channel and program device register endpoints. State is per-slave configuration, not managed by this header.

Dependencies and integration points: depends on `linux/dmaengine.h` and integrates with Intel PCH peripheral drivers and DMAengine channel setup.

Risks and test signals: risks include wrong register DMA addresses, mismatched width causing data corruption, and channel ID conflicts. Tests should cover DMA channel request, TX/RX register programming, width variants, transfer completion, and fallback when DMA is unavailable.
