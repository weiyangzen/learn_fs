# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v2m.c

## Purpose
Implements ARM GICv2m MSI/MSI-X support by exposing MSI parent domains backed by GIC SPI ranges and v2m frame registers.

## Important APIs, Types, and Functions
`struct v2m_data` stores frame resource, fwnode, base, SPI range, bitmap, and quirks. Key functions include `gicv2m_init()`, OF/ACPI init helpers, `gicv2m_init_one()`, `gicv2m_allocate_domains()`, `gicv2m_irq_domain_alloc()/free()`, `gicv2m_compose_msi_msg()`, and quirk/teardown helpers.

## Control Flow
OF or ACPI discovery creates one or more `v2m_data` frames, reads or overrides SPI base/count, applies IIDR/Graviton quirks, allocates bitmaps, and creates an MSI parent domain. Allocation searches all frames for an aligned free SPI range, prepares DMA MSI addressing, allocates parent GIC IRQs as edge-rising SPIs, and installs a v2m chip whose MSI message writes either SETSPI_NS or quirked address/data.

## State and Persistence
Global `v2m_nodes` and `v2m_lock` protect frame list and bitmap allocation. Hardware state includes mapped v2m frame registers and parent GIC SPI configuration. ACPI may register an MSI fwnode provider for PCI.

## Dependencies and Integration Points
Depends on ARM GIC parent domains, PCI/platform MSI infrastructure, OF child frame nodes, ACPI MADT/IORT, IOMMU DMA MSI preparation, and `irq-msi-lib`.

## Risks and Test Signals
Risks include SPI range validation, multi-frame domain host-data representing only the first frame while allocation scans all frames, quirked message data/addressing, bitmap leak on `iommu_dma_prepare_msi()` failure, and ACPI Graviton range handling. Test signals include v2m range logs, MSI allocation/free under PCI/MSI-X, correct edge SPI configuration, and working X-Gene/NS2/Graviton quirks.
