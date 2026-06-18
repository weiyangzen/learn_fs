# sources/distributed-fs/ceph-client/drivers/irqchip/irq-alpine-msi.c

Purpose: Provides Annapurna Labs Alpine MSI-X support by allocating GIC SPIs and composing MSI messages targeting a local GIC interrupt doorbell address.

Important APIs/types/functions: `struct alpine_msix_data`, `alpine_msix_allocate_sgi()`, `alpine_msix_free_sgi()`, `alpine_msix_compose_msi_msg()`, `alpine_msix_middle_domain_alloc()`, `alpine_msix_init_domains()`, `alpine_msix_init()`, `middle_irq_chip`, and `alpine_msi_parent_ops`.

Control flow: Init reads the MSI doorbell resource and DT properties `al,msi-base-spi`/`al,msi-num-spis`, creates a bitmap of available SPIs, finds the parent GIC domain, and creates an MSI parent domain. Allocation reserves a contiguous bitmap range, allocates matching parent GIC IRQs with edge-rising fwspecs, and associates the middle irqchip for MSI message composition.

State and persistence: Driver state holds a spinlock, doorbell address, SPI base/count, and allocation bitmap retained after successful init. Each allocated IRQ stores the SPI hwirq and chip data.

Dependencies/integration: Uses OF address/IRQ helpers, GIC IRQ domains, PCI MSI generic library, MSI parent domains, and bitmap allocation.

Risks and test signals: Test multi-vector MSI allocation/free, ENOSPC handling, parent allocation rollback, MSI message address/data encoding, property validation, and affinity propagation through the parent irqchip.
