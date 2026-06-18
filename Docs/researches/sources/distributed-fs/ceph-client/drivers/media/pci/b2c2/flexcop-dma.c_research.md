# sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/flexcop-dma.c

## Purpose
`flexcop-dma.c` provides the exported DMA buffer lifecycle and DMA register programming helpers for B2C2 FlexCopII/FlexCopIII PCI digital TV devices. It allocates one coherent DMA area and exposes it to the hardware as two equal sub-buffers so the PCI ISR can alternate or stream through halves.

## Important APIs, Types, and Functions
The public API is `flexcop_dma_allocate()`, `flexcop_dma_free()`, `flexcop_dma_config()`, `flexcop_dma_xfer_control()`, `flexcop_dma_control_timer_irq()`, and `flexcop_dma_config_timer()`, all exported except the internal `flexcop_dma_remap()`. The functions operate on `struct flexcop_dma`, `struct flexcop_device`, `struct pci_dev`, `flexcop_dma_index_t`, `flexcop_dma_addr_index_t`, `flexcop_ibi_value`, and `flexcop_ibi_register`.

## Control Flow
Allocation rejects odd byte sizes, allocates coherent memory with `dma_alloc_coherent()`, and splits it into `cpu_addr0`/`dma_addr0` and `cpu_addr1`/`dma_addr1`. Configuration writes the shifted DMA base addresses and transfer size into either the DMA1 or DMA2 register block. Transfer control selects DMA1 or DMA2, reads the current start registers, toggles sub-address 0 and/or 1 start bits, and writes the values back. Timer setup disables remap, writes the DMA timer cycle count, and timer IRQ control toggles DMA1/DMA2 timer enable bits in `ctrl_208`.

## State and Persistence
Software state is the coherent buffer metadata stored in `struct flexcop_dma`. Hardware state is volatile FlexCop IBI register contents for DMA base, size, remap, start, and timer bits. There is no persistence across remove, suspend, or process lifetime.

## Dependencies and Integration Points
The file depends on PCI DMA APIs and the FlexCop bus abstraction supplied by `flexcop.h`: `read_ibi_reg()`, `write_ibi_reg()`, register names such as `dma1_000`, `dma2_010`, and logging macros. `flexcop-pci.c` calls these helpers during probe, stream start/stop, and IRQ-driven demux feeding.

## Risks and Edge Cases
The code assumes the hardware DMA address fields are word-addressed and stores addresses shifted right by two; non-word-aligned DMA addresses would be invalid for the device. `flexcop_dma_config()` and `flexcop_dma_xfer_control()` reject combined DMA1/DMA2 requests, while timer IRQ control accepts a mask. `flexcop_dma_free()` assumes a successfully initialized `pdev` and buffer metadata. Size must be even, and DMA1 sizes used by the PCI path must also be compatible with 188-byte MPEG-TS packet framing.

## Test Signals
Useful signals are successful coherent allocation/free, correct DMA1/DMA2 register writes, no transfer on invalid DMA masks, timer IRQ enable/disable visibility in `ctrl_208`, stream delivery from both sub-buffers, and clean device removal without DMA API warnings.
