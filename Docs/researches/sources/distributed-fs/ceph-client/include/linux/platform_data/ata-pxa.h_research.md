# sources/distributed-fs/ceph-client/include/linux/platform_data/ata-pxa.h

Purpose: defines platform data for the generic PXA PATA/ATA driver.

Important APIs and types: `struct pata_pxa_pdata` contains DMA request line `dma_dreq`, register address shift `reg_shift`, and `irq_flags`.

Control flow: board setup supplies the struct to the PXA PATA platform device; the ATA driver uses it for register addressing, DMA channel/request selection, and interrupt request flags.

State and persistence: static hardware wiring/configuration only. Runtime ATA ports, DMA descriptors, IRQ state, and disk data are managed elsewhere.

Dependencies and integration points: integrates PXA board files, libata PATA driver, DMA request routing, MMIO register layout, and IRQ setup.

Risks and test signals: risks include wrong register shift corrupting accesses, wrong DMA request line, and incompatible IRQ trigger flags. Test PIO and DMA transfers, IRQ handling, device detection, suspend/resume, and board variants with different register wiring.
