## sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma-pci.c

### Purpose
`ae4dma-pci.c` is the PCI bus glue for AMD AE4DMA. It allocates device state, maps PCI BARs, configures MSI-X/MSI interrupts and DMA mask, then calls AE4 core initialization.

### Important APIs, Types, And Functions
Important functions are `ae4_get_irqs()`, `ae4_free_irqs()`, `ae4_deinit()`, `ae4_pci_probe()`, and `ae4_pci_remove()`. The PCI ID table matches AMD device `0x149B`, and `module_pci_driver()` registers the driver named `ae4dma`.

### Control Flow, State, And Persistence
Probe devm-allocates `struct ae4_device` and MSI-X bookkeeping, enables the PCI function, maps all memory BARs via pcim helpers, stores BAR0 as `pt->io_regs`, obtains MSI-X vectors for all queue slots or falls back to a single MSI vector shared across queue entries, sets bus mastering, requests a 48-bit coherent DMA mask, stores driver data, and invokes `ae4_core_init()`. Remove cancels/destroys workqueues and frees IRQ vectors.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include PCI core, managed PCI I/O mapping, IRQ vector allocation, AE4 core code, and shared PTDMA device fields. Risks include mapping all BARs but assuming index 0, fallback MSI sharing all queues, not checking `dma_set_mask_and_coherent()` return, partial initialization cleanup relying on devm/pcim, and remove not explicitly unregistering dmaengine channels if core init succeeded. Test signals include matching device `0x149B`, MSI-X and MSI fallback paths, BAR mapping failures, 48-bit DMA mask behavior, probe error cleanup, and remove after active DMA submissions.
