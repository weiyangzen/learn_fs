# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/msi.c

## Purpose
Implements pSeries PCI MSI/MSI-X support using RTAS `ibm,change-msi` and `ibm,query-interrupt-source-number`, and exposes it through Linux MSI parent IRQ domains.

## Important APIs, Types, And Functions
Key helpers are `rtas_change_msi`, `rtas_disable_msi`, `rtas_query_irq_number`, `check_req_msi`, `check_req_msix`, `msi_quota_for_device`, `rtas_prepare_msi_irqs`, `pseries_msi_ops_prepare`, `pseries_msi_ops_teardown`, `pseries_irq_domain_alloc`, `pseries_irq_domain_free`, `pseries_msi_allocate_domains`, `pseries_msi_free_domains`, and `rtas_msi_pci_irq_fixup`. Per-allocation state is `struct pseries_msi_device`.

## Control Flow
Initialization locates RTAS tokens and installs a PCI IRQ fixup callback. Domain allocation creates an MSI parent IRQ domain per PHB. For a device request, `rtas_prepare_msi_irqs` checks firmware request properties, computes the PE quota, rounds MSI-X counts when firmware requires powers of two, tries explicit MSI/MSI-X and 32-bit variants, and falls back to legacy change calls. IRQ allocation queries the hardware interrupt source number for the MSI index, allocates parent interrupts, and installs a pSeries MSI chip.

## State And Persistence
Static RTAS tokens are cached. Each MSI allocation stores quota and used count in `struct pseries_msi_device` until teardown, where the firmware allocation is disabled all-at-once. The chip caches MSI messages instead of rewriting MSI-X vector table entries.

## Dependencies And Integration Points
Depends on PCI device-tree properties `ibm,req#msi`, `ibm,req#msi-x`, and `ibm,pe-total-#msi`; EEH PE topology; RTAS; generic MSI library parent ops; Linux IRQ domains; PCI config space; and pSeries PHB setup.

## Risks And Edge Cases
RTAS cannot disable a single vector, so teardown happens at MSI-domain teardown. Firmware may reject non-power-of-two MSI-X counts. Old firmware lacks explicit or 32-bit MSI functions, forcing fallback or a Gen2 32-bit MSI address hack. Quota calculation must avoid starving peer devices in a PE. Devices without LSI or MSI request properties are intentionally left alone by the fixup.

## Test Signals
Test MSI and MSI-X allocation under PowerVM/QEMU, quota clamping across multiple PE devices, 32-bit DMA-mask devices, PCIe Gen2 fallback, vector teardown, suspend/resume MSI message composition, and PHB domain allocation failures. Boot logs should show RTAS token discovery and no unexpected `ibm,change-msi` errors.
