# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-mbi.c

## Purpose

`irq-gic-v3-mbi.c` implements GICv3 Message Based Interrupt support for systems that expose SPIs through GICD `SETSPI_NSR` and `CLRSPI_NSR` writes rather than a full ITS. It creates an MSI parent irq domain over the normal GIC domain, allocates SPIs from firmware-described MBI ranges, and composes MSI or MBI messages that devices can write to assert and, for level-capable platform MSI, clear an interrupt.

## Important APIs, Types, And Functions

The central type is `struct mbi_range`, which records an SPI base, SPI count, and allocation bitmap. Global state is `mbi_lock`, `mbi_phys_base`, `mbi_ranges`, and `mbi_range_nr`. `mbi_irq_chip` delegates mask, unmask, EOI, type, and affinity operations to the parent GIC IRQ.

`mbi_init()` is the firmware entry point called by the GICv3 core when `GICD_TYPER.MBIS` is present. It parses the OF `msi-controller`, `mbi-ranges`, and optional `mbi-alias` properties, allocates range bitmaps, records the frame physical base, and calls `mbi_allocate_domain()`. Domain operations are `mbi_irq_domain_alloc()`, `mbi_irq_domain_free()`, and the `msi_lib_irq_domain_select()` selector. `mbi_irq_gic_domain_alloc()` allocates the parent GIC SPI using an OF-style fwspec and forces edge-rising type. `mbi_compose_msi_msg()` creates a one-message set-SPI MSI, while `mbi_compose_mbi_msg()` creates set and clear messages for level-capable device MSI.

## Control Flow

Initialization is OF-only. If the GIC node lacks `msi-controller`, `mbi_init()` returns success without creating a domain. Otherwise, it validates the `mbi-ranges` property as pairs of `(spi_start, nr_spis)`, allocates a bitmap per range, determines the physical MBI frame from `mbi-alias` or the GIC resource base, and creates an MSI parent domain with `gic_v3_mbi_msi_parent_ops`.

During MSI allocation, `mbi_irq_domain_alloc()` searches all range bitmaps under `mbi_lock` for a power-of-two aligned region large enough for `nr_irqs`. It prepares the MSI through `iommu_dma_prepare_msi()` against `mbi_phys_base + GICD_SETSPI_NSR`, allocates each parent GIC SPI through `mbi_irq_gic_domain_alloc()`, and assigns `mbi_irq_chip` plus the selected range as chip data. Freeing releases the bitmap region and parent IRQs. Message composition writes the parent hwirq as MSI data and sets the target address to `SETSPI_NSR`; MBI level messages also include a `CLRSPI_NSR` clear message.

## State And Persistence Behavior

The MBI driver stores all configured ranges for the life of the kernel. Allocation state is the bitmap inside each `mbi_range`, protected by `mbi_lock`. Per-IRQ chip data points back to the owning `mbi_range` so frees can release the correct bitmap. There is no suspend/resume state in this file; persistence is primarily the static MMIO frame base and the allocated MSI parent domain.

## Dependencies And Integration Points

This driver depends on OF GIC node properties, the parent GICv3 irq domain, Linux MSI parent-domain helpers, the irq-msi-lib selector and MSI info initializer, IOMMU MSI preparation, and generic parent irq-chip delegation. It integrates into `irq-gic-v3.c` through `mbi_init(handle, gic_data.domain)` when the distributor reports MBIS. It supports PCI MSI/MSI-X and platform device MSI via `MATCH_PCI_MSI | MATCH_PLATFORM_MSI`, but explicitly rejects ACPI because the specification has no MBI description.

## Risks

Important risks are firmware description errors, bitmap sizing/alignment mismatches for multi-MSI allocations, and failing to release allocated bitmap regions if parent allocation or IOMMU preparation fails. Since all parent IRQs are forced edge-rising by default, devices needing level semantics rely on the platform MSI path to mark level capability and compose clear messages. Incorrect `mbi-alias` translation would direct devices to the wrong set/clear SPI frame.

## Test Signals

Boot logs should show each MBI range and the selected MBI frame address. Tests should allocate PCI MSI, PCI MSI-X, and platform MSI vectors, verify the composed address/data pair targets `SETSPI_NSR`, verify level-capable platform MSI gets both set and clear messages, free and reallocate ranges, exercise multi-vector power-of-two allocation, and verify affinity/type operations delegate to the parent GIC domain.
