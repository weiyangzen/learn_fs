## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-pci.c

### Purpose
`ptdma-pci.c` is the PCI bus driver for AMD PassThru DMA. It allocates PT device state, maps the configured BAR, obtains MSI-X/MSI interrupts, configures DMA masks, and calls PTDMA core initialization.

### Important APIs, Types, And Functions
Important functions are `pt_alloc_struct()`, `pt_get_msix_irqs()`, `pt_get_msi_irq()`, `pt_get_irqs()`, `pt_free_irqs()`, `pt_pci_probe()`, and `pt_pci_remove()`. It matches AMD PCI device `0x1498` with `struct pt_dev_vdata` selecting BAR 2.

### Control Flow, State, And Persistence
Probe allocates `struct pt_device` and MSI-X state with devm, enables the PCI device, maps all memory BARs, selects BAR 2 from the ioremap table, obtains MSI-X or MSI, sets bus mastering, attempts 48-bit then 32-bit coherent DMA mask, stores driver data, and invokes `pt_core_init()`. Remove calls `pt_core_destroy()` when initialized and frees the interrupt mode.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include PCI/pcim resource management, MSI/MSI-X APIs, DMA masks, PT core functions, and device IDs. Risks include legacy `pci_enable_msix_range()`/`pci_enable_msi()` cleanup differences, mapping all BARs while using only one, returning from failed probe without freeing IRQs in some error paths after allocation, and assuming driver data is always present for matched IDs. Test signals include probe for device `0x1498`, BAR 2 mapping, MSI-X success and MSI fallback, 48-bit mask fallback to 32-bit, init failure unwind, and remove after registered dmaengine activity.
